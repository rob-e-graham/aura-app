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
- [ ] Premium purchase opens Apple payment sheet
- [ ] Pro purchase works
- [ ] Restore Purchases works
- [ ] Token top-up consumable works
- [ ] Memory top-up consumable works
- [ ] Server sync after purchase via `/api/account/state`
- [ ] Server sync via `/api/tokens/topup`
- [ ] Server sync via `/api/memory/topup`
- [ ] App fails closed (no free unlock if billing unavailable)

## 3. Supabase Per-User Memory Integrity (Blocker)
- [ ] Each signed-in user reads/writes only their own aura_user_memory row
- [ ] Merge logic on reinstall/sign-in/sign-out/switch-account
- [ ] Memory state persists across relaunch and fresh install
- [ ] RLS and user scoping verified end-to-end

## 4. AI Quality + Personalization (Current Issue)
- [ ] Cloud AI path (DeepSeek via Together) reachable and stable under auth/premium
- [ ] Personalization context included in prompts and retained across sessions
- [ ] Fallback behavior when API fails (no crash, graceful messaging)
- [ ] Pro/Premium users get cloud AI responses, NOT local dumb responses

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

## Current Status
- **Auth**: Working (Phase 1 complete)
- **Active Issue**: Pro users still getting local/dumb AI responses instead of cloud AI
- **Next**: Fix cloud AI routing for paid tiers, then continue through Phase 2+
