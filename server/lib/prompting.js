const fs = require("fs");

function readTextFile(filePath, fallback = "") {
  try {
    return fs.readFileSync(filePath, "utf8").trim();
  } catch (error) {
    console.warn(`Prompt file not found: ${filePath}`);
    return fallback;
  }
}

function readPromptDb(promptDbPath) {
  try {
    const raw = fs.readFileSync(promptDbPath, "utf8");
    return JSON.parse(raw);
  } catch (error) {
    console.warn(`Prompt DB not found or invalid JSON: ${promptDbPath}`);
    return { defaultProfile: "balanced", profiles: {}, blocks: {} };
  }
}

function firstExistingFile(filePaths = []) {
  return filePaths.find((filePath) => {
    try {
      return fs.existsSync(filePath);
    } catch (_) {
      return false;
    }
  }) || "";
}

function readOptionalSoulPrompt(soulPromptPaths = []) {
  const soulPath = firstExistingFile(soulPromptPaths);
  if (!soulPath) return "";
  return readTextFile(soulPath, "");
}

function randItem(items = []) {
  if (!Array.isArray(items) || !items.length) return "";
  return items[Math.floor(Math.random() * items.length)];
}

function inferUserSignal(userMessage = "") {
  const text = String(userMessage || "").trim();
  const words = text ? text.split(/\s+/).length : 0;
  const exclamations = (text.match(/!/g) || []).length;
  const questions = (text.match(/\?/g) || []).length;
  const emotional = /(anxious|sad|stressed|overwhelmed|lost|angry|hurt|scared|afraid|confused|burned out|lonely|grief|panic)/i.test(text);
  const positive = /(excited|happy|grateful|good|great|love|hopeful|proud|calm)/i.test(text);
  const playful = /(lol|haha|lmao|omg|mate|:)|😂|🤣|😅|✨/i.test(text);
  const flat = words > 0 && words <= 7 && !questions && !exclamations && !emotional && !positive;
  const direct = words <= 14 && !emotional;
  const heavy = emotional || /(grief|death|dying|trauma|abuse|panic|depressed|suicid|self-harm|hospital|diagnosis)/i.test(text);
  const asksDepth = /(deeper|deep dive|unpack|full reading|explain more|go deeper|why do i|what is really)/i.test(text);
  const roomy = (words >= 10 || questions > 0) && !heavy;
  return { words, exclamations, questions, emotional, positive, playful, flat, direct, heavy, asksDepth, roomy };
}

function buildAuraVariation(userMessage = "") {
  const signal = inferUserSignal(userMessage);
  const personaModes = [
    {
      key: "poetic_mystical",
      label: "poetic / mystical",
      rule: "Use a little more luminous, symbolic phrasing than usual, but stay concrete and readable."
    },
    {
      key: "intimate_human",
      label: "intimate / human",
      rule: "Sound especially human and relational, like a deeply attuned friend speaking simply."
    },
    {
      key: "direct_sharp",
      label: "direct / sharp",
      rule: "Be clean, honest, and incisive. Keep warmth, but prioritize clarity and truth over softness."
    },
    {
      key: "playful_magnetic",
      label: "playful / magnetic",
      rule: "Let a little charm or light playfulness through, but keep it elegant and never silly."
    }
  ];
  const personaMode = signal.roomy ? randItem(personaModes) : null;
  const moodPool = signal.emotional
    ? ["steady", "gentle", "grounded", "softly warm"]
    : signal.playful
      ? ["bright", "warmly playful", "light", "curious"]
      : signal.flat
        ? ["warm", "lightly animated", "inviting", "gently energizing"]
        : ["grounded", "curious", "clear", "warm"];

  const cadencePool = signal.flat
    ? ["slightly more expressive than the user's wording", "a touch more warmth and color than the user's tone", "gentle lift in energy without overdoing it"]
    : signal.direct
      ? ["clean and concise", "clear with natural warmth", "compact with one vivid phrase"]
      : ["natural and varied", "flowing but concise", "warm with a little texture"];

  const openingPool = signal.flat
    ? [
        "Open with a short human line that adds warmth before insight.",
        "Start with a concise acknowledgment, then add a little personality.",
        "Use a warmer opener than usual so the reply feels alive, not robotic."
      ]
    : [
        "Vary the opening sentence shape from your recent replies.",
        "Avoid repeating common stock openers; sound fresh and natural.",
        "Use a natural opening that matches the user's tone, not a canned phrase."
      ];

  const flavorPool = signal.playful
    ? [
        "A tiny wink of humor is allowed if it stays kind and brief.",
        "A light playful note is okay, but keep the insight grounded."
      ]
    : [
        "Use one slightly vivid phrase or image if it helps clarity.",
        "Let personality show in rhythm and phrasing, not in extra length.",
        "It is okay to sound a little more human and less polished-perfect."
      ];

  return [
    "Personality variation for this reply (keep all safety and end-question rules):",
    ...(personaMode ? [
      "- This turn has room for personality variation.",
      `- Random soul mode for this reply: ${personaMode.label}.`,
      `- ${personaMode.rule}`
    ] : [
      "- Keep the core Aura voice steady for this reply (less style variation, more attunement)."
    ]),
    `- Mood today: ${randItem(moodPool)}.`,
    `- Cadence: ${randItem(cadencePool)}.`,
    `- ${randItem(openingPool)}`,
    `- ${randItem(flavorPool)}`,
    "- Keep structure constraints, but vary sentence rhythm and word choice more than usual.",
    "- If the user is brief/flat, add warmth and gentle personality instead of mirroring flatness.",
    "- In heavy/sensitive moments, reduce stylization and prioritize steadiness."
  ].join("\n");
}

function computeRequestTemperature(userMessage = "") {
  const signal = inferUserSignal(userMessage);
  const base = signal.emotional ? 0.78 : 0.84;
  const variance = signal.flat ? 0.08 : signal.playful ? 0.1 : 0.06;
  const jitter = Math.random() * variance;
  return Math.min(0.96, Number((base + jitter).toFixed(2)));
}

function createPromptService({ systemPromptPath, promptDbPath, soulPromptPaths = [] }) {
  return {
    readPromptDb: () => readPromptDb(promptDbPath),
    computeRequestTemperature,
    buildSystemPrompt({ userMessage = "", frontendSystem = "", promptProfile = "" } = {}) {
      const basePrompt = readTextFile(
        systemPromptPath,
        [
          "You are Aura Guide — a reflective AI helping users explore themselves through symbolic card readings.",
          "Be warm but grounded, avoid medical/legal/crisis advice, and end with one reflection question."
        ].join("\n")
      );

      const promptDb = readPromptDb(promptDbPath);
      const selectedProfile = promptProfile || promptDb.defaultProfile || "balanced";
      const profileBlockKeys = promptDb.profiles?.[selectedProfile] || [];
      const sections = [basePrompt];
      const soulPrompt = readOptionalSoulPrompt(soulPromptPaths);

      profileBlockKeys.forEach((blockKey) => {
        const blockText = promptDb.blocks?.[blockKey];
        if (blockText) sections.push(`[${blockKey}]\n${blockText}`);
      });

      if (soulPrompt) sections.push(`[AURA_SOUL]\n${soulPrompt}`);
      if (userMessage) sections.push(`[AURA_VARIATION]\n${buildAuraVariation(userMessage)}`);
      if (frontendSystem && typeof frontendSystem === "string") {
        sections.push(`[APP_CONTEXT]\n${frontendSystem.trim()}`);
      }

      return sections.join("\n\n");
    }
  };
}

module.exports = {
  createPromptService
};
