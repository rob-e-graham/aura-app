# AURA — Launch Plan

Single source of truth for getting AURA from "running on TestFlight" to
"launched on the App Store with paying users". Owners and ETAs are
placeholder — fill in as you go.

Phases run mostly serially (1 → 7), but **Phase 6 (Marketing) runs
in parallel** from the moment you start TestFlight beta.

---

## Phase 0 — Where we are right now (Apr 27)

- ✅ App builds, runs on simulator + device
- ✅ Apple Developer account active (team `9F72SM2FBF`)
- ✅ Bundle ID `com.auralife.app`, Version `1.0.0`, Build `1`
- ✅ App icon in Xcode (gold sparkle on brand night)
- ✅ Brand pack done (sparkle mark, wordmark, stacked, app icon, all in `/brand/`)
- ✅ Supabase auth working (email + OTP)
- ✅ RevenueCat integrated for subscriptions
- ✅ Bulletproof consumable top-ups (pending queue, idempotency contract documented)
- ✅ Light/Dark card toggle in Settings
- ✅ Card-personality orbs (each of 78 cards has unique palette)
- ✅ Listing draft in `APP_STORE_LISTING.md`
- ✅ Server contract in `PURCHASE_RELIABILITY.md`
- 🟡 iOS glass styling on text boxes / buttons (paused mid-edit)
- 🔴 Server-side topup idempotency table not yet implemented
- 🔴 Production Supabase keys not yet in place
- 🔴 Stripe not set up
- 🔴 No screenshots taken yet
- 🔴 No marketing assets shipped

---

## Phase 1 — Code-complete (target: 1-3 days)

### 1.1 Remaining UI polish
- [ ] **iOS glass material on text boxes + buttons** — same recipe both, blur(36px) saturate(1.25), ~65% alpha, inner top highlight, soft edge
- [ ] Test the new card-personality orbs across all 78 cards (visual sanity check)
- [ ] Verify the share poster still renders correctly with new orb gradients
- [ ] Verify Light Cards toggle still works with the new tinted card backgrounds
- [ ] Test on at least 3 device sizes: iPhone 15 Pro Max, iPhone 13, iPhone SE

### 1.2 Bug sweep (do a deliberate test pass)
- [ ] Pull a 3-card spread → tap each card to highlight → does panel become readable?
- [ ] Open chat → send a message → wait for response → ensure animation is smooth
- [ ] Toggle Light Cards → reload app → verify toggle persists
- [ ] Force quit during a chat response → reopen → verify chat resumes correctly
- [ ] Settings → Restore Purchases (with no purchase) → should show "No purchases found"
- [ ] Disable network → try to chat → should show local-mode prompt cleanly
- [ ] Disable network → try to buy tokens → should queue + show "Purchase pending" card

### 1.3 Performance
- [ ] Profile Time-to-Interactive on cold launch (target: <2s on iPhone 13)
- [ ] Check memory usage during a 50-message chat session (target: <200MB)
- [ ] Animations stay at 60fps (use Xcode Instruments → Core Animation)

---

## Phase 2 — Backend hardening (target: 1-2 days)

### 2.1 Production Supabase
- [ ] Create production Supabase project (separate from dev)
- [ ] Migrate schema: users, readings, memory entries, topup_transactions
- [ ] Update `index.html` env vars: `SUPABASE_URL`, `SUPABASE_ANON_KEY` to production
- [ ] Test sign-up + sign-in against prod Supabase
- [ ] Set up Supabase Row-Level Security (RLS) policies — users can only read their own data
- [ ] Set up daily database backup (Supabase Pro tier, or pg_dump cron)

### 2.2 Topup idempotency (CRITICAL — see PURCHASE_RELIABILITY.md)
- [ ] Create `topup_transactions` table on server (schema in PURCHASE_RELIABILITY.md)
- [ ] Update `/api/tokens/topup` endpoint to:
    - INSERT with `ON CONFLICT (transaction_id) DO NOTHING`
    - Only credit user when INSERT actually inserted a row
    - Return current balance regardless (so retry calls return same data)
- [ ] Same logic for `/api/memory/topup`
- [ ] Test: hit endpoint twice with same transactionId → user credited only once

### 2.3 RevenueCat receipt validation
- [ ] In RevenueCat dashboard, set up webhook → server endpoint `/api/webhooks/revenuecat`
- [ ] Server records all `INITIAL_PURCHASE` and `NON_RENEWING_PURCHASE` events
- [ ] `/api/tokens/topup` cross-checks: only credits if RC webhook has confirmed the transactionId
- [ ] Without this, anyone with a JWT could fake transactionIds to get free tokens

### 2.4 Stripe (future-proofing for web/Android)
- [ ] Open Stripe account, complete business verification
- [ ] Connect Stripe to RevenueCat (Settings → Payment Providers → Stripe)
- [ ] Mirror your iOS products as Stripe products (same prices, same identifiers)
- [ ] **Note: not blocking for iOS launch** — Stripe is for web/Android v2
- [ ] When ready: web build can call RC's web SDK → uses Stripe under the hood

### 2.5 Server reliability
- [ ] Set up uptime monitoring (UptimeRobot or BetterStack — free tier fine)
- [ ] Alert email on 5xx errors or downtime
- [ ] Set up error reporting (Sentry free tier)
- [ ] Verify privacy policy + terms pages load consistently

---

## Phase 3 — TestFlight beta (target: 3-7 days)

### 3.1 First upload
- [ ] In Xcode: Archive → Distribute → App Store Connect → Upload
- [ ] Wait for processing (~10-30 min, email confirmation)
- [ ] In App Store Connect → TestFlight → fill out:
    - Beta App Description (text in `APP_STORE_LISTING.md`)
    - "What to Test" instructions
    - Contact email
- [ ] Add yourself + 2-3 family members as Internal Testers
- [ ] Verify install works end-to-end on real device

### 3.2 Internal beta (3-5 days)
- [ ] Use the app yourself daily for a week — pull a reading every morning
- [ ] Have your daughter (and any other internal testers) use it daily
- [ ] Track issues in a shared note or Notion page
- [ ] Categorise: 🔴 critical bug / 🟡 polish / 🟢 nice-to-have
- [ ] Fix all 🔴 before opening external beta

### 3.3 External beta (7-14 days)
- [ ] In App Store Connect → submit beta info for Apple's beta review (~24h first time)
- [ ] Once approved → invite 10-30 external testers via TestFlight email or public link
- [ ] Recruit testers from: friends, social media followers, r/tarot, /r/CalTrenton beta-testing community
- [ ] Set a clear feedback channel (a dedicated email like beta@aura-me.app or a shared form)
- [ ] Daily review of TestFlight crashes in App Store Connect → Crashes tab
- [ ] Iterate on top complaints
- [ ] Final build to TestFlight before App Store submission — bump build number

---

## Phase 4 — App Store submission prep (target: 1-2 days)

Use `APP_STORE_LISTING.md` for all the copy.

### 4.1 Screenshots (6.7" iPhone, 1290×2796)
- [ ] Boot iOS 17 Pro Max simulator → set status bar override:
      `xcrun simctl status_bar booted override --time "9:41" --batteryState charged --batteryLevel 100`
- [ ] Capture (Cmd+S in sim, saves to Desktop):
    1. Entry screen — sparkle logo, AURA wordmark, atmospheric orb
    2. 3-card spread (dark) — fresh reading
    3. Single card detail with AURA reflection panel
    4. Chat with AURA — mid-conversation
    5. Light Cards mode — same 3-card spread on white cards
    6. Daily card with affirmation
- [ ] Optional: prep marketing-style screenshots with overlay text in Figma/Canva
- [ ] Upload all 5-6 in App Store Connect → Screenshots → 6.7" iPhone

### 4.2 App Store Connect listing
- [ ] App Name: try `AURA` first, fall back to `AURA — Cards & Reflection`
- [ ] Subtitle: `Card readings & AI reflection`
- [ ] Promo Text, Description, Keywords — paste from `APP_STORE_LISTING.md`
- [ ] Categories: Lifestyle (primary), Health & Fitness (secondary)
- [ ] Age rating: 12+ (mild mystical themes per questionnaire)
- [ ] Privacy: see App Privacy section in `APP_STORE_LISTING.md`
- [ ] Support URL + Privacy Policy URL — verify both URLs load
- [ ] Copyright: `© 2026 Rob Graham`
- [ ] Sign-In info for App Review (test account they can use)

### 4.3 Final pre-submit checks
- [ ] Hit every paywall flow once: see paywall → close → buy → restore
- [ ] Hit every top-up flow once with a test purchase (sandbox)
- [ ] Verify pending top-ups card appears + clears correctly
- [ ] Run app through Xcode Organizer → Validate App
- [ ] Submit for Review

---

## Phase 5 — Submit & wait (~1-3 days)

- [ ] Apple reviews the build
- [ ] Possible rejection reasons + how to handle:
    - "Need a test account" → already provided in listing
    - "Subscriptions don't restore" → already implemented + tested
    - "Description mentions 'tarot' / 'fortune telling'" → may need to soften wording (we deliberately avoided "fortune telling" in copy)
    - "App crashes on launch" → check Crashes report, fix, resubmit (build number +1)
- [ ] Once approved: choose immediate or scheduled release
- [ ] Recommend scheduled release on a **Tuesday or Wednesday morning** (best App Store algorithm window)

---

## Phase 6 — Marketing (runs in parallel from Phase 3 onwards)

**This is Fam's brief.** Everything below should be ownable by an autonomous
agent given the right access (social accounts, email tool, copy bank).

### 6.1 Brand & content foundations (Week -3 from launch)

- [ ] Reserve handles on every social: `@aura_me`, `@auracards`, `@auralife`
    - Instagram, TikTok, X/Twitter, Pinterest, Threads, YouTube
- [ ] Set up a domain: `aura-me.app` or similar (currently on `aura-me.square.site` — upgrade to dedicated domain pre-launch)
- [ ] Set up email infrastructure:
    - Custom domain emails: hello@, support@, beta@, press@
    - Transactional email (Resend or Postmark)
    - Marketing email (Buttondown or ConvertKit)
- [ ] Build a "press kit" page on the website with:
    - High-res app icons + sparkle logos (already in `/brand/`)
    - Founder photo + bio (Rob Graham)
    - One-pager describing AURA in 200 words
    - Screenshots of the app
    - Press contact email

### 6.2 Pre-launch buildup (Weeks -3 to -1) — Fam-runnable

**Weekly content cadence:**
| Day | Channel | Content |
|---|---|---|
| Mon | Instagram | Card of the week — beautiful orb image + 2-line affirmation |
| Mon | TikTok | "Pulling tomorrow's energy" 30s reading + voiceover |
| Tue | Pinterest | Quote graphic with affirmation pulled from Major Arcana |
| Wed | Substack/blog | Longform reflection: "What does Bloom mean for you?" |
| Thu | Instagram | Behind the scenes: design of the orb / colour theory |
| Fri | TikTok | "Three signs you need a reset" — engagement bait, soft sell |
| Sat | Email | Weekly card pull for subscriber list |
| Sun | All | Sunday reset — quote graphic + TestFlight invite link |

**Content bank** Fam should generate from the existing card data:
- 78 individual card cards (orb + name + affirmation) — Instagram + Pinterest format
- 22 longform reflections (one per Major Arcana) — Substack/blog
- 78 short TikToks — "When [card name] shows up in your reading…" 30s vertical

### 6.3 Influencer outreach (Week -2)

- [ ] Pull a list of 50 mid-tier (10K-100K followers) creators in:
    - Tarot / oracle (e.g. @ohcindyq, @astroleyte)
    - Pastel wellness aesthetic (e.g. @soft.living)
    - Spiritual self-development (e.g. @themadnomad)
- [ ] Cold pitch: free Pro tier + £50 Amazon voucher for an honest review
- [ ] Provide them with: app icon, sparkle SVG, screenshots, talking points
- [ ] Track responses in a sheet; aim for 5-10 confirmed reviews around launch week

### 6.4 Press list (Week -1)

- [ ] Email pitch + press kit to:
    - Refinery29 (spirituality vertical)
    - The Cut (lifestyle)
    - mindbodygreen
    - Well+Good
    - Vogue Australia (spirituality + wellness section)
    - Local press (Sydney Morning Herald lifestyle)
- [ ] Offer: "First Australian-made AI-powered tarot app, designed by an Aussie dad for his daughter"
- [ ] Custom angle for each pub — see press kit notes

### 6.5 Launch day (Day 0) — Fam-runnable

- [ ] App goes live on App Store at 10am AEST (Tuesday)
- [ ] Cross-post launch announcement: IG, TikTok, X, Pinterest, Substack
- [ ] Email subscriber list: "AURA is live. First reading is on us."
- [ ] Reach out to influencers + press to confirm coverage timing
- [ ] Open a public Discord or Substack chat for community
- [ ] AMA on r/tarot

### 6.6 Post-launch (Weeks 1-4)

- [ ] Daily monitor: App Store reviews, social mentions, support email
- [ ] Reply to every review (within 24h)
- [ ] Track: installs, free→paid conversion %, churn at day 7 / 30
- [ ] Iterate on the top complaint each week
- [ ] Plan v1.1: 1-2 quality-of-life features driven by reviews

---

## Phase 7 — Post-launch operations (ongoing)

### 7.1 Customer support
- [ ] Triage flow:
    - Tier 1: FAQ-driven auto-reply
    - Tier 2: Founder reads + replies (Rob, daily)
    - Tier 3: Escalation for billing / account issues
- [ ] Common cases to pre-write responses for:
    - "I bought tokens but they didn't arrive" → check pending queue + topup_transactions table → manually credit if needed
    - "Restore Purchases doesn't work" → guide them through TestFlight install
    - "App crashes on X device" → request crash log
- [ ] Refund policy clearly stated in app + website

### 7.2 Analytics + product
- [ ] Track key metrics weekly:
    - Daily active users
    - 7-day retention
    - Free → Premium conversion rate
    - Paywall views vs. paywall conversions
    - Average session length
    - Most-popular reading type (3-card vs single)
- [ ] Use TelemetryDeck or simple PostHog free tier
- [ ] Quarterly product review based on data

### 7.3 Content + community ops (Fam continues)
- [ ] Weekly card-of-the-week email + IG post
- [ ] Monthly community spotlight (anonymised reader story)
- [ ] Quarterly capsule release (chemo-care palette, Major Arcana posters, etc.)
- [ ] Engage with every comment for the first 6 months — algo trust comes from reciprocity

---

## What "Fam" needs from you to start

Give the OpenClaw agent:
1. ✅ This document (`LAUNCH_PLAN.md`)
2. ✅ The brand pack (`/brand/`)
3. ✅ The card data (78 cards, names, affirmations, palettes — already in `index.html`)
4. ✅ The colourway doc (`AURA_PASTEL_FASHION_COLORWAYS.md`)
5. ⚠️ Social account logins (or app passwords / OAuth)
6. ⚠️ Email tool API key (Resend, Buttondown — your choice)
7. ⚠️ Influencer outreach budget approval (~£500-1500 for first wave)
8. ⚠️ Tone of voice document (write this — see notes below)

**Tone of voice for Fam to follow** — write a 1-pager covering:
- AURA speaks calmly, never excitedly
- Uses lowercase often (it's softer)
- Never uses exclamation marks except sparingly in emails
- Talks about "reflection", not "predictions"
- Values: gentleness, curiosity, autonomy, beauty, restraint
- Forbidden words: "fate", "fortune", "destiny", "psychic" (App Store hostile + brand off)

---

## The single most important thing

**Get to TestFlight this week.** Everything else can be sequenced after.
A real beta with 20 humans using it daily will surface more useful changes
in 5 days than another month of polish in isolation. The door to App Store
review opens the moment your beta is stable and your listing is filled in.

Submit Day target: **roughly 14 days from today (mid-May)** — assuming
internal beta starts Mon Apr 28, external beta opens Wed May 7, App Store
submission goes in Mon May 12, public launch Tue May 21.

That's the realistic timeline. Tighter is possible but introduces risk;
wider is fine but the energy is here right now — ride it.

---

*Last updated: Apr 27, 2026. Update this doc as plans evolve.*
