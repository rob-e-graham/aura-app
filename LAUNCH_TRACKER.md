# AURA — Launch Tracker

Live status of every task between now and App Store launch.
Update this doc as items move from `[ ]` → `[x]`. Keep it scannable.

For the full strategic plan + Fam's marketing brief, see `LAUNCH_PLAN.md`.

**Status:** 🟡 Beta-ready code, beta upload pending
**Next milestone:** TestFlight Internal beta (target this week)
**Public launch target:** Tue 21 May 2026

---

## ✅ Already shipped

### Brand & visual
- [x] AURA sparkle logo finalised (dramatic curve, subtle cross-tip silhouette)
- [x] Wordmark + sparkle lockups (horizontal, stacked, gold/black/white)
- [x] App icon designed + installed in Xcode (1024 PNG)
- [x] Marketing icon set generated (16 → 1024px PNGs)
- [x] Brand pack docs (`/brand/` + `preview.html`)
- [x] Pastel fashion colourway palette (`AURA_PASTEL_FASHION_COLORWAYS.md`)

### App functionality
- [x] 78-card AURA deck with one-word archetypal names
- [x] 3-card spread + single-card focus reading
- [x] AI reflection guide (RevenueCat-gated cloud LLM, optional local AI)
- [x] Personalisation onboarding (name, intention, zodiac)
- [x] Daily card with affirmation
- [x] Share → Instagram-sized 4:5 reading poster
- [x] Email + OTP authentication via Supabase
- [x] Light/Dark card toggle in Settings
- [x] Each card has unique orb personality (built from card's own 3-colour palette)
- [x] No more white-hole orb centre
- [x] Light cards pick up faint tint of the card's primary colour
- [x] Hero orb sized so it doesn't overflow phone frame
- [x] iOS glass material on all panels + buttons (one visual family)

### Subscriptions & purchases
- [x] RevenueCat integrated, tier-based feature gating
- [x] Subscription restore working
- [x] Bulletproof consumable top-ups: pending queue + idempotency contract documented
- [x] Pending Top-ups UI card in Settings (auto-shown when queue is non-empty)
- [x] "Retry now" button + 50-attempt fail-safe
- [x] Server contract docc (`PURCHASE_RELIABILITY.md`)

### Xcode / project setup
- [x] Apple Developer Program active (team `9F72SM2FBF`)
- [x] Bundle ID `com.auralife.app`
- [x] Version `1.0.0` / Build `1`
- [x] App icon installed in Assets.xcassets

### Documentation
- [x] App Store Connect listing draft (`APP_STORE_LISTING.md`)
- [x] Purchase reliability spec (`PURCHASE_RELIABILITY.md`)
- [x] Launch plan (`LAUNCH_PLAN.md`)
- [x] Pastel colourways doc
- [x] This tracker

---

## 🟡 In progress / next up

### Phase 1 — Final code polish
- [ ] iOS glass material — verify on real device after rebuild ⬅ JUST SHIPPED, NEEDS XCODE TEST
- [ ] Re-run all 78 cards in app, visual sanity check on the card-personality orbs
- [ ] Verify share poster renders correctly with new orb gradients
- [ ] Tone-of-voice doc for Fam (writing now)
- [ ] 78 card-of-the-day social posters (generating now)

### Phase 1 — Bug sweep (do a deliberate pass before TestFlight)
- [ ] Pull a 3-card spread → tap each card to highlight → panel readable?
- [ ] Open chat → send a message → response renders smoothly
- [ ] Toggle Light Cards → reload app → preference persists
- [ ] Force quit during a chat response → reopen → resumes correctly
- [ ] Settings → Restore Purchases (no purchase) → "No purchases found"
- [ ] Disable network → try chat → local-mode prompt cleanly shown
- [ ] Disable network → try to buy tokens → queues + shows pending card
- [ ] Test on iPhone 13, iPhone 15 Pro Max, iPhone SE — each renders cleanly

---

## 🔴 Blocking before TestFlight beta

### Backend (server-side — separate repo)
- [ ] Implement `topup_transactions` table on server (schema in `PURCHASE_RELIABILITY.md`)
- [ ] Update `/api/tokens/topup` for idempotency (ON CONFLICT DO NOTHING)
- [ ] Update `/api/memory/topup` for idempotency
- [ ] Set up RevenueCat webhook → server endpoint (`/api/webhooks/revenuecat`)
- [ ] Server cross-checks topup transactionId against RC webhook records
- [ ] Production Supabase project created
- [ ] Migrate dev schema to prod
- [ ] Update `index.html` env: `SUPABASE_URL`, `SUPABASE_ANON_KEY` to prod
- [ ] Test full sign-up flow end-to-end against prod Supabase
- [ ] Set up Supabase RLS policies (users can only read their own data)
- [ ] Schedule daily Supabase backup (Pro tier or pg_dump cron)

### Server reliability
- [ ] UptimeRobot or BetterStack monitoring on `/api/health`
- [ ] Sentry free tier wired up for server + client crash reports
- [ ] Privacy policy + Terms pages verified loading consistently

---

## 🔴 Blocking before App Store submission

### App Store Connect
- [ ] App Name reserved (try `AURA`, fall back to `AURA — Cards & Reflection`)
- [ ] Subtitle filled in
- [ ] Description pasted from `APP_STORE_LISTING.md`
- [ ] Promotional Text filled in
- [ ] Keywords (full 100 chars used)
- [ ] Categories: Lifestyle (primary), Health & Fitness (secondary)
- [ ] Age rating completed (12+)
- [ ] App Privacy questionnaire completed
- [ ] Privacy Policy URL verified live
- [ ] Support URL verified live
- [ ] Marketing URL filled in
- [ ] Copyright `© 2026 Rob Graham`
- [ ] Sign-in info for App Review (test account credentials)

### Screenshots (6.7" iPhone, 1290×2796)
- [ ] Set sim status bar override: `xcrun simctl status_bar booted override --time "9:41" --batteryState charged --batteryLevel 100`
- [ ] Screenshot 1: Entry screen with sparkle logo
- [ ] Screenshot 2: 3-card dark reading
- [ ] Screenshot 3: Card detail with AURA reflection
- [ ] Screenshot 4: Chat with AURA
- [ ] Screenshot 5: Light Cards mode
- [ ] Screenshot 6 (optional): Daily card

### Final pre-submit
- [ ] Validate App via Xcode → Organizer
- [ ] Submit for Review

---

## 🟢 Marketing prep (Fam's brief — runs in parallel)

### Domain & email
- [ ] Buy `aura-me.app` (or similar dedicated domain)
- [ ] Custom emails: hello@, support@, beta@, press@
- [ ] Resend or Postmark for transactional email
- [ ] Buttondown or ConvertKit for newsletter

### Social handles
- [ ] Instagram `@aura_me` (or chosen handle)
- [ ] TikTok handle
- [ ] Pinterest handle
- [ ] X / Twitter handle
- [ ] Threads handle
- [ ] YouTube channel

### Content foundations
- [ ] Tone of voice doc finalised (writing now)
- [ ] 78 card-of-the-day social posters generated (Instagram square + 4:5)
- [ ] 22 Major Arcana longform reflections (Substack-ready)
- [ ] 78 short-form TikTok scripts ("When [card] shows up…")
- [ ] Press kit page on website (logo bundle, founder bio, screenshots, contact)

### Outreach
- [ ] List of 50 mid-tier creators (10K-100K) in tarot / wellness / pastel niches
- [ ] Cold pitch template for influencers
- [ ] Press list (Refinery29, The Cut, mindbodygreen, Vogue AU, SMH lifestyle)
- [ ] Custom angle pitch for each press contact

### Launch day
- [ ] App Store live (target: Tue 21 May 2026, 10am AEST)
- [ ] Cross-post launch announcement on every social
- [ ] Email subscriber list ("AURA is live. First reading is on us.")
- [ ] Confirm influencer coverage timing
- [ ] AMA on r/tarot
- [ ] Open Discord or Substack chat for community

---

## 📅 Timeline (working back from public launch)

| Week | Dates | Focus |
|---|---|---|
| -3 | Apr 27 – May 3 | Code polish + backend hardening + TestFlight Internal beta |
| -2 | May 4 – May 10 | External TestFlight (10-30 testers) + screenshots + listing fill |
| -1 | May 11 – May 17 | Submit for review + influencer outreach + press pitches |
| 0 | May 18 – May 24 | **Public launch Tuesday May 21** + reply to every review |
| +1 | May 25 – May 31 | Iterate based on reviews + plan v1.1 |
| +2 | Jun 1 onwards | Sustained content cadence (Fam-runnable) |

---

## 🎯 Success metrics (track from day 0)

- Daily Active Users (DAU)
- 7-day retention (target: 35%+)
- 30-day retention (target: 18%+)
- Free → Premium conversion rate (target: 4%+)
- Paywall view → conversion (target: 12%+)
- Average session length (target: 4+ min)
- App Store rating (target: 4.5+)
- Most-popular reading type (3-card vs single)

---

## 📝 Decision log

Notes on big choices, when revisited.

- **2026-04-26:** Pivoted to Light/Dark card toggle (vs full app theme switch) — daughter feedback that white mode was "too brutal" full-app
- **2026-04-26:** Each of 78 cards gets unique orb gradient from its own 3-colour palette (was: family-level shared palette per slot)
- **2026-04-26:** Sparkle logo: bottom arm 14% longer than top — subtle Christian-cross silhouette under a primarily-sparkle reading
- **2026-04-27:** Settled on iOS glass material (blur 36, saturate 1.30) for both panels and buttons, same recipe — one visual family
- **2026-04-27:** Stripe deferred to v2 (after iOS launch) — RevenueCat handles iOS IAP fully; Stripe only needed for web/Android

---

*Last updated: Apr 27, 2026 — keep updating as we ship.*
