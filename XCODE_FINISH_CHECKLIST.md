# AURA — Xcode Finish Checklist
*Hand this to Claude in Xcode (Opus/Sonnet). Work through top to bottom.*

---

## Project context
- **App:** AURA — tarot / spiritual guidance iOS app
- **Stack:** Capacitor wrapping a single-page web app (`index.html`)
- **Repo:** `/Users/robgraham/Desktop/APPS/AURA app final`
- **iOS project:** `ios/App/App.xcworkspace`
- **Backend:** `https://aura-app-8va5.onrender.com` (live on Render)
- **Bundle ID:** `com.auralife.app`
- **Auth:** Supabase email OTP (no Apple Sign-In)
- **Purchases:** RevenueCat (`appl_test_bmrngPaRezJznfNKVRVFxFhBkSP` — swap for prod key before release)
- **AI:** Together.ai / DeepSeek via Render server

---

## 1. Xcode Signing & Capabilities (do first — blocks everything else)

Open `ios/App/App.xcworkspace` in Xcode.

- [ ] **Signing:** Team set, bundle ID `com.auralife.app`, provisioning profile valid
- [ ] **In-App Purchase** capability added (Signing & Capabilities tab → + Capability → In-App Purchase)
- [ ] **Push Notifications** capability added
- [ ] **Background Modes** → Remote notifications checked
- [ ] Build succeeds on physical device (not simulator) — purchases and notifications don't work on simulator

---

## 2. Sandbox purchase testing (biggest App Store blocker)

Requires physical iPhone + sandbox Apple ID (create at appstoreconnect.apple.com → Users → Sandbox Testers).

**Sign out of real Apple ID in Settings → App Store on the iPhone first.**

Test each flow:
- [ ] Tap "Chat with Aura" → paywall appears for cloud AI features
- [ ] Purchase **Premium** ($4.44/mo) — sandbox sheet appears, confirm
- [ ] After purchase: premium features unlock, token count shows
- [ ] **Restore Purchases** button works (Settings → Subscription)
- [ ] Purchase **Pro** ($11.11/mo) upgrade path works
- [ ] Token top-up consumable purchase works
- [ ] Memory expansion consumable purchase works
- [ ] Cancelling the purchase sheet doesn't crash or show error to user

**RevenueCat dashboard:** check `https://app.revenuecat.com` — sandbox purchase should appear there in real time.

---

## 3. Auth flow on device

- [ ] Fresh install — entry screen shows (AURA logo, orb, sign-in at bottom)
- [ ] Enter email → "Send Code" → OTP email arrives
- [ ] Enter 6-digit code → verified → lands on welcome screen
- [ ] Kill app and relaunch → stays logged in (session restored)
- [ ] Sign out (Settings → Sign Out) → returns to entry screen
- [ ] Sign back in → session restored, same tier/tokens as before
- [ ] "Continue without an account" → guest mode works, welcome screen loads

---

## 4. Notifications on device

Notifications require a physical device — they don't fire on simulator.

- [ ] First launch → notification permission prompt appears (or check Settings hub)
- [ ] Enable notifications in Settings hub → toggle turns on
- [ ] Test notification fires (Settings → "Send Test Notification" button)
- [ ] Daily affirmation notification scheduled (check device Settings → Notifications → AURA)
- [ ] Horoscope notification scheduled
- [ ] Tapping notification opens app to correct screen

---

## 5. Core app flow walkthrough (crash-free pass)

Run through every screen on device:

- [ ] Splash → Entry → Welcome (orb breathing, no layout issues)
- [ ] Draw Your Cards → shuffle screen → tap 3 cards → reading screen → AI interpretation loads
- [ ] Chat with Aura → chat screen → send a message → AI responds
- [ ] Daily Guidance → affirmation shows, horoscope loads, chat works
- [ ] Settings hub → all toggles present, account info shows correct tier
- [ ] Settings → Subscription → shows current plan
- [ ] Settings → Delete Account → double-confirm works, account deleted

---

## 6. Before TestFlight / App Store submission

- [ ] Swap RevenueCat test key → production key in `public/config.js`:
  ```
  window.AURA_REVENUECAT_APPLE_KEY = 'appl_YOUR_PRODUCTION_KEY';
  ```
- [ ] Run `npx vite build && npx cap copy ios` after key swap
- [ ] Set app version + build number in Xcode (General tab)
- [ ] Add app icons (all sizes) — check `ios/App/App/Assets.xcassets/AppIcon.appiconset`
- [ ] Add launch screen / splash assets
- [ ] Archive → Distribute → TestFlight
- [ ] Test on TestFlight build (not dev build) — IAP works differently in TestFlight

---

## 7. Known gotchas

- **`npx cap copy ios`** — use this (not `cap sync`) to avoid CocoaPods UTF-8 error. Pods are already installed.
- **Together.ai credit:** $5.35 remaining. Daily cap set to 200 req/day server-side. Don't test with auto-refresh dashboard.
- **RevenueCat key:** current key in config.js is a test key — must swap to prod before App Store submission.
- **Render cold start:** first request after inactivity takes ~10s. Normal behaviour.
- **Local AI fallback:** if server is unreachable, app falls back to on-device responses. This is intentional.

---

## Files to know

| File | Purpose |
|------|---------|
| `index.html` | Entire frontend — all screens, CSS, JS |
| `public/config.js` | API keys and endpoints |
| `server/server.js` | Render backend — AI proxy, auth, account |
| `ios/App/App.xcworkspace` | Open this in Xcode |
| `capacitor.config.ts` | Capacitor config |

---

*Last updated: 2026-04-21 — Claude Sonnet 4.6*
