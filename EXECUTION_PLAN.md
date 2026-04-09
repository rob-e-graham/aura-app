# AURA — Launch-Critical Execution Plan

Status key: [x] Done | [-] In progress | [ ] Not started

---

## 1. Auth Recovery (Blocker)
- [x] Auth screen working
- [x] Send Code fires
- [x] Continue without account navigates
- [x] OTP verify works
- [x] Relaunch session restore works

## 2. Purchases & Restore (Blocker)
- [ ] Premium purchase opens Apple payment sheet (needs Sandbox Apple ID testing)
- [ ] Pro purchase works
- [ ] Restore Purchases works
- [ ] Token top-up consumable works
- [ ] Memory top-up consumable works
- [-] Server sync after purchase via `/api/account/state` (endpoint deployed, needs device test)
- [-] Server sync via `/api/tokens/topup` (endpoint deployed, needs device test)
- [-] Server sync via `/api/memory/topup` (endpoint deployed, needs device test)
- [ ] App fails closed (no free unlock if billing unavailable)

## 3. Supabase Per-User Memory Integrity (Blocker)
- [x] Memory content syncs to Supabase (memory_data column on profiles)
- [x] Memory auto-syncs on save (debounced 5s)
- [x] Merge logic on sign-in (server wins if more data)
- [ ] Verify each signed-in user reads/writes only their own data
- [ ] Memory state persists across relaunch and fresh install (needs device test)
- [x] RLS covers memory_data via existing profiles policy

## 4. AI Quality + Personalization
- [x] Cloud AI path (DeepSeek via Together) reachable and stable (tested via curl)
- [x] Tier sync bug fixed (server tier now authoritative with force:true)
- [x] Token balance resets on tier upgrade (no more "Need More Tokens" after upgrade)
- [x] Fallback behavior when API fails (graceful local fallback + timeout message)
- [x] 25s timeout on cloud AI requests
- [x] AI responses no longer always end with a question (varied endings)
- [-] Pro/Premium users get cloud AI responses (code fixed, needs device verification)
- [x] Personalization context included in prompts
- [x] Memory retained across sessions (localStorage + Supabase sync)

## 5. URLs, Deep Links, Website/Shop
- [ ] Shop website URL correct everywhere (paywall, settings, legal, CTAs)
- [ ] Open-in-browser works from iOS app
- [ ] Terms of Service link works
- [ ] Privacy Policy link works

## 6. Notifications
- [ ] Daily horoscope notification scheduling/delivery on physical iPhone
- [ ] Daily affirmation notification scheduling/delivery
- [ ] Permission states (granted/denied) reflected in UI
- [ ] Notifications survive app relaunch

## 7. Apple Approval Hardening
- [ ] In-App Purchase capability present and working
- [ ] Restore purchases visible and functional
- [ ] Accurate subscription disclosures (billing, renewal, cancellation)
- [ ] Privacy policy / terms / support links valid and reachable
- [ ] Account delete option (if required by Apple)
- [ ] No crashes or blocking runtime errors in critical flows

## 8. Go/No-Go Release Report
- [ ] Final checklist with pass/fail per flow
- [ ] Known risks documented
- [ ] Exact remaining blockers listed

---

## Completed This Session
- Added splash screen (replaces empty cosmic boot screen)
- Fixed paywall scroll cropping on small screens
- Fixed cloud AI routing (tier sync bug)
- Fixed token reset on tier upgrade
- Added dev debug panel in Settings
- Added service status dashboard (tools/dashboard.html)
- Added memory_data sync to Supabase
- Added 25s timeout on AI requests
- Improved AI response variety (not always ending with question)
- Deployed server changes to Render via GitHub push

## What Needs Testing On Device
1. Debug panel: Set Premium → chat → verify cloud AI response
2. Sign in → verify server sync shows correct tier
3. Paywall scrolling on smaller screens
4. Splash screen on cold boot
5. Sandbox Apple ID purchase flow (Phase 2 blocker)
