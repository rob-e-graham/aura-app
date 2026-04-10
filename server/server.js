const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");
const { createPromptService } = require("./lib/prompting");
const { createLlmClient } = require("./lib/providers");

function loadEnvFile(envFilePath) {
  if (!fs.existsSync(envFilePath)) return;
  const lines = fs.readFileSync(envFilePath, "utf8").split(/\r?\n/);
  lines.forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) return;
    const idx = trimmed.indexOf("=");
    if (idx <= 0) return;
    const key = trimmed.slice(0, idx).trim();
    const value = trimmed.slice(idx + 1).trim();
    if (!process.env[key]) process.env[key] = value;
  });
}

loadEnvFile(path.join(__dirname, ".env"));

function readEnv(key, fallback = "") {
  const raw = process.env[key];
  if (raw == null) return fallback;
  const cleaned = String(raw).trim().replace(/^['"]|['"]$/g, "");
  return cleaned || fallback;
}

function normalizeTogetherBaseUrl(url) {
  const cleaned = String(url || "").trim().replace(/\/+$/, "");
  if (!cleaned) return "https://api.together.xyz/v1";
  if (/\/v1$/i.test(cleaned)) return cleaned;
  return `${cleaned}/v1`;
}

const app = express();
const PORT = Number(readEnv("PORT", "3000"));
const JSON_BODY_LIMIT = readEnv("JSON_BODY_LIMIT", "1mb");
const LLM_PROVIDER = readEnv("LLM_PROVIDER", "together").toLowerCase();
const TOGETHER_API_KEY = readEnv("TOGETHER_API_KEY", "");
const TOGETHER_BASE_URL = normalizeTogetherBaseUrl(readEnv("TOGETHER_BASE_URL", "https://api.together.xyz/v1"));
const TOGETHER_MODEL = readEnv("TOGETHER_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo");
const OLLAMA_URL = readEnv("OLLAMA_URL", "http://localhost:11434/api/generate");
const OLLAMA_MODEL = readEnv("OLLAMA_MODEL", "phi3");
const PROMPTS_DIR = path.join(__dirname, "prompts");
const SYSTEM_PROMPT_PATH = path.join(PROMPTS_DIR, "system_prompt.txt");
const PROMPT_DB_PATH = path.join(PROMPTS_DIR, "prompt_db.json");
const SOUL_PROMPT_PATHS = [
  path.join(PROMPTS_DIR, "soul.md"),
  path.join(__dirname, "soul.md"),
  path.join(process.cwd(), "soul.md")
];

// Supabase config
const SUPABASE_URL = readEnv("SUPABASE_URL", "");
const SUPABASE_SERVICE_ROLE_KEY = readEnv("SUPABASE_SERVICE_ROLE_KEY", "");

// RevenueCat config
const REVENUECAT_SECRET_API_KEY = readEnv("REVENUECAT_SECRET_API_KEY", "");
const REVENUECAT_WEBHOOK_AUTH = readEnv("REVENUECAT_WEBHOOK_AUTH", "");

// Token allowances per tier
const TOKEN_ALLOWANCES = { free: 0, premium: 50000, pro: 150000 };
const MEMORY_ALLOWANCES = { free: 0, premium: 100, pro: 500 };

// ===== GLOBAL DAILY SPEND CAP — protects Together.ai credits =====
const DAILY_REQUEST_CAP = Number(readEnv("DAILY_REQUEST_CAP", "200")); // max AI requests per day across ALL users
let dailyRequestCount = 0;
let dailyCapResetDate = new Date().toDateString();

function checkDailyCap() {
  const today = new Date().toDateString();
  if (today !== dailyCapResetDate) {
    dailyRequestCount = 0;
    dailyCapResetDate = today;
  }
  return dailyRequestCount < DAILY_REQUEST_CAP;
}

function incrementDailyCap() {
  const today = new Date().toDateString();
  if (today !== dailyCapResetDate) {
    dailyRequestCount = 0;
    dailyCapResetDate = today;
  }
  dailyRequestCount++;
}

// Initialize Supabase admin client (lazy — only if configured)
let supabaseAdmin = null;
function getSupabase() {
  if (supabaseAdmin) return supabaseAdmin;
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) return null;
  try {
    const { createClient } = require("@supabase/supabase-js");
    supabaseAdmin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
      auth: { autoRefreshToken: false, persistSession: false }
    });
    return supabaseAdmin;
  } catch (err) {
    console.warn("Supabase client not available:", err.message);
    return null;
  }
}

app.use(cors());
app.use(express.json({ limit: JSON_BODY_LIMIT }));

// Static legal pages
app.get("/terms", (req, res) => res.sendFile(path.join(__dirname, "pages", "terms.html")));
app.get("/privacy", (req, res) => res.sendFile(path.join(__dirname, "pages", "privacy.html")));
const promptService = createPromptService({
  systemPromptPath: SYSTEM_PROMPT_PATH,
  promptDbPath: PROMPT_DB_PATH,
  soulPromptPaths: SOUL_PROMPT_PATHS
});

const llmClient = createLlmClient({
  togetherBaseUrl: TOGETHER_BASE_URL,
  togetherApiKey: TOGETHER_API_KEY,
  togetherModel: TOGETHER_MODEL,
  ollamaUrl: OLLAMA_URL,
  ollamaModel: OLLAMA_MODEL
});

// ===== AUTH MIDDLEWARE =====
async function requireAuth(req, res, next) {
  const sb = getSupabase();
  if (!sb) {
    // Supabase not configured — pass through (dev mode)
    req.userId = null;
    return next();
  }

  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Authorization required" });
  }

  const token = authHeader.slice(7);
  try {
    const { data, error } = await sb.auth.getUser(token);
    if (error || !data?.user) {
      return res.status(401).json({ error: "Invalid or expired token" });
    }
    req.userId = data.user.id;
    req.userEmail = data.user.email;
    next();
  } catch (err) {
    return res.status(401).json({ error: "Authentication failed" });
  }
}

// Optional auth — attaches user if token present, passes through if not
async function optionalAuth(req, res, next) {
  const sb = getSupabase();
  const authHeader = req.headers.authorization;
  if (sb && authHeader && authHeader.startsWith("Bearer ")) {
    try {
      const { data } = await sb.auth.getUser(authHeader.slice(7));
      if (data?.user) {
        req.userId = data.user.id;
        req.userEmail = data.user.email;
      }
    } catch (_) {}
  }
  next();
}

// ===== TOKEN BALANCE HELPERS =====
// Maps to user_usage table: ai_tokens_limit (monthly allowance), ai_tokens_used,
// ai_tokens_bonus, storage_limit, storage_used, storage_bonus, period_reset_at
async function getTokenBalance(userId) {
  const sb = getSupabase();
  if (!sb || !userId) return null;
  const { data } = await sb.from("user_usage").select("*").eq("user_id", userId).single();
  if (!data) return null;
  // Normalize to a common shape used throughout the server
  return {
    user_id: data.user_id,
    monthly_allowance: data.ai_tokens_limit || 0,
    monthly_used: data.ai_tokens_used || 0,
    bonus_tokens: data.ai_tokens_bonus || 0,
    period_start: data.period_reset_at,
    storage_limit: data.storage_limit || 0,
    storage_used: data.storage_used || 0,
    storage_bonus: data.storage_bonus || 0,
    _raw: data
  };
}

async function getUserEntitlement(userId) {
  const sb = getSupabase();
  if (!sb || !userId) return null;
  const { data } = await sb
    .from("user_entitlements")
    .select("tier, expires_at, updated_at")
    .eq("user_id", userId)
    .single();
  return data || null;
}

async function deductServerTokens(userId, tokensUsed, source = "chat") {
  const sb = getSupabase();
  if (!sb || !userId) return;

  let bal = await getTokenBalance(userId);
  if (!bal) return;

  // Check for monthly reset
  const now = Date.now();
  const resetAt = bal.period_start ? new Date(bal.period_start).getTime() : 0;
  if (now >= resetAt) {
    bal.monthly_used = 0;
    // Next reset: first of next month
    const nextReset = new Date();
    nextReset.setMonth(nextReset.getMonth() + 1, 1);
    nextReset.setHours(0, 0, 0, 0);
    bal.period_start = nextReset.toISOString();
  }

  // Deduct from monthly first, then bonus
  const monthlyLeft = bal.monthly_allowance - bal.monthly_used;
  if (monthlyLeft >= tokensUsed) {
    bal.monthly_used += tokensUsed;
  } else {
    bal.monthly_used = bal.monthly_allowance;
    bal.bonus_tokens = Math.max(0, bal.bonus_tokens - (tokensUsed - Math.max(0, monthlyLeft)));
  }

  await sb.from("user_usage").update({
    ai_tokens_limit: bal.monthly_allowance,
    ai_tokens_used: bal.monthly_used,
    ai_tokens_bonus: bal.bonus_tokens,
    period_reset_at: bal.period_start
  }).eq("user_id", userId);
}

function estimateTokens(input, output) {
  return Math.ceil(((input || "").length + (output || "").length) / 4);
}

// ===== ROUTES =====

app.get("/api/health", (req, res) => {
  res.json({
    ok: true,
    provider: LLM_PROVIDER,
    togetherBaseUrl: TOGETHER_BASE_URL,
    togetherModel: TOGETHER_MODEL,
    togetherKeyConfigured: Boolean(TOGETHER_API_KEY),
    supabaseConfigured: Boolean(SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY),
    revenuecatConfigured: Boolean(REVENUECAT_SECRET_API_KEY),
    dailyRequests: dailyRequestCount,
    dailyCap: DAILY_REQUEST_CAP,
    promptFiles: {
      systemPrompt: fs.existsSync(SYSTEM_PROMPT_PATH),
      promptDb: fs.existsSync(PROMPT_DB_PATH),
      soulPrompt: SOUL_PROMPT_PATHS.some((filePath) => fs.existsSync(filePath))
    }
  });
});

// AI endpoint with optional token metering
async function handleAiRequest(req, res) {
  try {
    const userMessage = typeof req.body?.message === "string" ? req.body.message.trim() : "";
    const frontendSystem = typeof req.body?.system === "string" ? req.body.system : "";
    const promptProfile = typeof req.body?.promptProfile === "string" ? req.body.promptProfile : "";

    if (!userMessage) {
      return res.status(400).json({ error: "No message provided" });
    }

    // Global daily spend cap — hard stop to protect Together.ai credits
    if (!checkDailyCap()) {
      console.warn(`DAILY CAP HIT: ${dailyRequestCount}/${DAILY_REQUEST_CAP} requests today`);
      return res.status(429).json({
        error: "daily_cap_reached",
        message: "Daily AI request limit reached. Resets at midnight.",
        requests_today: dailyRequestCount
      });
    }

    // Server-side token check if user is authenticated
    if (req.userId) {
      const bal = await getTokenBalance(req.userId);
      if (bal) {
        const monthlyLeft = Math.max(0, bal.monthly_allowance - bal.monthly_used);
        const remaining = monthlyLeft + bal.bonus_tokens;
        if (remaining < 100) {
          return res.status(429).json({
            error: "tokens_exhausted",
            remaining: 0,
            message: "You've used all your tokens. Buy more or wait for your monthly reset."
          });
        }
      }
    }

    const systemPrompt = promptService.buildSystemPrompt({ userMessage, frontendSystem, promptProfile });
    const temperature = promptService.computeRequestTemperature(userMessage);
    const reply = await llmClient.generate({
      provider: LLM_PROVIDER,
      systemPrompt,
      userMessage,
      temperature
    });

    // Deduct tokens server-side if authenticated
    const tokensUsed = estimateTokens(systemPrompt + userMessage, reply);
    let tokensRemaining = null;
    if (req.userId) {
      await deductServerTokens(req.userId, tokensUsed, "chat");
      const updatedBal = await getTokenBalance(req.userId);
      if (updatedBal) {
        const ml = Math.max(0, updatedBal.monthly_allowance - updatedBal.monthly_used);
        tokensRemaining = ml + updatedBal.bonus_tokens;
      }
    }

    incrementDailyCap();
    res.json({ reply, tokens_used: tokensUsed, tokens_remaining: tokensRemaining, requests_today: dailyRequestCount });

  } catch (error) {
    console.error("LLM Error:", error.message);
    res.status(500).json({ reply: "AI service unavailable. Please try again." });
  }
}

app.post("/api/ai", optionalAuth, handleAiRequest);
app.post("/api/llama", optionalAuth, handleAiRequest);

app.get("/api/account/state", requireAuth, async (req, res) => {
  try {
    const entitlement = await getUserEntitlement(req.userId);
    const bal = await getTokenBalance(req.userId);
    const monthlyLeft = bal ? Math.max(0, bal.monthly_allowance - bal.monthly_used) : 0;

    return res.json({
      ok: true,
      user_id: req.userId,
      tier: entitlement?.tier || "free",
      expires_at: entitlement?.expires_at || null,
      usage: {
        monthly_allowance: bal?.monthly_allowance || 0,
        monthly_used: bal?.monthly_used || 0,
        bonus_tokens: bal?.bonus_tokens || 0,
        remaining_tokens: monthlyLeft + (bal?.bonus_tokens || 0),
        period_start: bal?.period_start || null,
        storage_limit: bal?.storage_limit || 0,
        storage_used: bal?.storage_used || 0,
        storage_bonus: bal?.storage_bonus || 0,
        remaining_storage: Math.max(
          0,
          (bal?.storage_limit || 0) + (bal?.storage_bonus || 0) - (bal?.storage_used || 0)
        )
      }
    });
  } catch (err) {
    console.error("Account state error:", err.message);
    return res.status(500).json({ error: "Failed to fetch account state" });
  }
});

// ===== TOKEN BALANCE ENDPOINT =====
app.get("/api/tokens/balance", requireAuth, async (req, res) => {
  try {
    const bal = await getTokenBalance(req.userId);
    if (!bal) {
      return res.json({
        ok: true,
        monthly_allowance: 0,
        monthly_used: 0,
        bonus_tokens: 0,
        remaining: 0,
        period_start: null
      });
    }
    const monthlyLeft = Math.max(0, bal.monthly_allowance - bal.monthly_used);
    return res.json({
      ok: true,
      monthly_allowance: bal.monthly_allowance,
      monthly_used: bal.monthly_used,
      bonus_tokens: bal.bonus_tokens,
      remaining: monthlyLeft + bal.bonus_tokens,
      period_start: bal.period_start
    });
  } catch (err) {
    console.error("Token balance error:", err.message);
    return res.status(500).json({ error: "Failed to fetch token balance" });
  }
});

// ===== TOKEN TOP-UP ENDPOINT (called after RevenueCat purchase confirmation) =====
app.post("/api/tokens/topup", requireAuth, async (req, res) => {
  try {
    const amount = typeof req.body?.amount === "number" ? req.body.amount : 25000;
    const sb = getSupabase();
    if (!sb) return res.status(503).json({ error: "Service not configured" });

    let bal = await getTokenBalance(req.userId);
    if (!bal) {
      // Create initial usage row
      await sb.from("user_usage").insert({
        user_id: req.userId,
        ai_tokens_used: 0,
        ai_tokens_limit: 0,
        ai_tokens_bonus: amount,
        storage_used: 0,
        storage_limit: 0,
        storage_bonus: 0
      });
      return res.json({ ok: true, bonus_tokens: amount, remaining: amount });
    }

    const newBonus = (bal.bonus_tokens || 0) + amount;
    await sb.from("user_usage").update({
      ai_tokens_bonus: newBonus
    }).eq("user_id", req.userId);

    const monthlyLeft = Math.max(0, bal.monthly_allowance - bal.monthly_used);
    return res.json({ ok: true, bonus_tokens: newBonus, remaining: monthlyLeft + newBonus });
  } catch (err) {
    console.error("Token topup error:", err.message);
    return res.status(500).json({ error: "Failed to add tokens" });
  }
});

app.post("/api/memory/topup", requireAuth, async (req, res) => {
  try {
    const amount = typeof req.body?.amount === "number" ? req.body.amount : 100;
    const sb = getSupabase();
    if (!sb) return res.status(503).json({ error: "Service not configured" });

    let bal = await getTokenBalance(req.userId);
    if (!bal) {
      await sb.from("user_usage").insert({
        user_id: req.userId,
        ai_tokens_used: 0,
        ai_tokens_limit: 0,
        ai_tokens_bonus: 0,
        storage_used: 0,
        storage_limit: 0,
        storage_bonus: amount
      });
      return res.json({ ok: true, storage_bonus: amount, remaining: amount });
    }

    const newBonus = (bal.storage_bonus || 0) + amount;
    const newRemaining = Math.max(0, (bal.storage_limit || 0) + newBonus - (bal.storage_used || 0));
    await sb.from("user_usage").update({
      storage_bonus: newBonus
    }).eq("user_id", req.userId);

    return res.json({ ok: true, storage_bonus: newBonus, remaining: newRemaining });
  } catch (err) {
    console.error("Memory topup error:", err.message);
    return res.status(500).json({ error: "Failed to add memory" });
  }
});

// ===== TOKEN RESET (Dev/Debug) =====
app.post("/api/tokens/reset", requireAuth, async (req, res) => {
  try {
    const sb = getSupabase();
    if (!sb) return res.status(503).json({ error: "Service not configured" });

    const { error } = await sb.from("user_usage").update({
      ai_tokens_used: 0
    }).eq("user_id", req.userId);

    if (error) {
      console.error("Token reset error:", error.message);
      return res.status(500).json({ error: "Failed to reset tokens" });
    }

    const bal = await getTokenBalance(req.userId);
    const remaining = bal ? Math.max(0, bal.monthly_allowance - bal.monthly_used) + (bal.bonus_tokens || 0) : 0;
    return res.json({ ok: true, monthly_used: 0, remaining });
  } catch (err) {
    console.error("Token reset error:", err.message);
    return res.status(500).json({ error: "Failed to reset tokens" });
  }
});

// ===== MEMORY DATA SYNC =====
// Save user's personalization memory (themes, moods, actions) to Supabase
app.post("/api/memory/sync", requireAuth, async (req, res) => {
  try {
    const sb = getSupabase();
    if (!sb || !req.userId) return res.status(500).json({ error: "Not available" });

    const memoryData = req.body?.memory_data;
    if (!memoryData || typeof memoryData !== 'object') {
      return res.status(400).json({ error: "Invalid memory_data" });
    }

    const { error } = await sb
      .from("profiles")
      .update({ memory_data: memoryData })
      .eq("id", req.userId);

    if (error) {
      console.error("Memory sync save error:", error.message);
      return res.status(500).json({ error: "Failed to save memory" });
    }

    res.json({ ok: true });
  } catch (err) {
    console.error("Memory sync error:", err.message);
    res.status(500).json({ error: "Failed to sync memory" });
  }
});

// Load user's personalization memory from Supabase
app.get("/api/memory/sync", requireAuth, async (req, res) => {
  try {
    const sb = getSupabase();
    if (!sb || !req.userId) return res.status(500).json({ error: "Not available" });

    const { data, error } = await sb
      .from("profiles")
      .select("memory_data")
      .eq("id", req.userId)
      .single();

    if (error) {
      console.error("Memory sync load error:", error.message);
      return res.status(500).json({ error: "Failed to load memory" });
    }

    res.json({ ok: true, memory_data: data?.memory_data || {} });
  } catch (err) {
    console.error("Memory sync error:", err.message);
    res.status(500).json({ error: "Failed to load memory" });
  }
});

// ===== REVENUECAT WEBHOOK =====
app.post("/api/webhooks/revenuecat", async (req, res) => {
  // Verify webhook auth
  if (REVENUECAT_WEBHOOK_AUTH) {
    const authHeader = req.headers.authorization;
    if (authHeader !== `Bearer ${REVENUECAT_WEBHOOK_AUTH}`) {
      return res.status(401).json({ error: "Unauthorized" });
    }
  }

  try {
    const event = req.body?.event;
    if (!event) return res.json({ ok: true });

    const appUserId = event.app_user_id;
    const eventType = event.type;

    const sb = getSupabase();
    if (!sb || !appUserId) return res.json({ ok: true });

    // Determine tier from entitlements
    const entitlements = event.entitlements || {};
    let tier = "free";
    if (entitlements.pro_access?.is_active) tier = "pro";
    else if (entitlements.premium_access?.is_active) tier = "premium";

    // Upsert entitlement state (user_entitlements table)
    await sb.from("user_entitlements").upsert({
      user_id: appUserId,
      tier,
      revenuecat_id: event.original_app_user_id || appUserId,
      expires_at: event.expiration_at_ms ? new Date(event.expiration_at_ms).toISOString() : null,
      updated_at: new Date().toISOString()
    });

    // Update token + storage allowances in user_usage
    const tokenAllowance = TOKEN_ALLOWANCES[tier] || 0;
    const storageAllowance = MEMORY_ALLOWANCES[tier] || 0;

    const existingBal = await getTokenBalance(appUserId);
    if (existingBal) {
      await sb.from("user_usage").update({
        ai_tokens_limit: tokenAllowance,
        storage_limit: storageAllowance
      }).eq("user_id", appUserId);
    } else {
      await sb.from("user_usage").insert({
        user_id: appUserId,
        ai_tokens_limit: tokenAllowance,
        ai_tokens_used: 0,
        ai_tokens_bonus: 0,
        storage_limit: storageAllowance,
        storage_used: 0,
        storage_bonus: 0
      });
    }

    console.log(`RevenueCat webhook: ${eventType} for ${appUserId} → tier=${tier}`);
    return res.json({ ok: true });
  } catch (err) {
    console.error("RevenueCat webhook error:", err.message);
    return res.status(500).json({ error: "Webhook processing failed" });
  }
});

app.listen(PORT, () => {
  console.log(`Aura AI running on http://localhost:${PORT}`);
  if (SUPABASE_URL) console.log("  Supabase: configured");
  if (REVENUECAT_SECRET_API_KEY) console.log("  RevenueCat: configured");
});
