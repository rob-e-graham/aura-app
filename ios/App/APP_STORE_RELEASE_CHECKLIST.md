# AURA — App Store Release Checklist

Status key: [x] Done | [-] In progress | [ ] Not started

---

## TESTFLIGHT GATE — DO THESE IN ORDER

### 1. Code + Deploy Sync
- [x] Push latest code changes to GitHub
- [ ] Confirm Render deploy includes `/api/account/state`
- [ ] Confirm Render deploy includes `/api/memory/topup`
- [x] Run `npm run build`
- [x] Run `npx cap sync ios`
- [x] If pods changed: run `cd ios/App && pod install`
- [x] Sync script: `./scripts/sync-ios-web.sh`

### 2. Native Capability Verification
- [ ] Open Xcode target `App` > Signing & Capabilities
- [ ] Verify `In-App Purchase` capability is present
- [ ] Confirm bundle ID is `com.auralife.app`
- [ ] Confirm the correct Team and provisioning profile are selected

### 3. Auth Verification On Physical iPhone
- [ ] Supabase "Confirm email" setting is ON (so OTP codes are sent)
- [ ] Fresh install from Xcode on physical iPhone
- [ ] Email OTP sign-in works end to end
- [ ] Relaunch app and confirm session is still restored
- [ ] Sign out and sign back in successfully
- [ ] "Continue without account" works (guest mode)

### 4. RevenueCat + Subscription Verification
- [ ] Sign in before opening paywall
- [ ] Premium purchase opens Apple payment sheet
- [ ] Purchase completes and tier changes from `free` to `premium`
- [ ] `/api/account/state` reflects paid tier after purchase
- [ ] Cloud AI chat works after purchase
- [ ] Tokens deduct after cloud chat
- [ ] Token count matches server after app relaunch
- [ ] Restore purchases works on fresh install

### 5. Consumables / Add-Ons Verification
- [ ] Buy 25k token top-up while signed in
- [ ] Confirm `/api/tokens/topup` increments server bonus tokens
- [ ] Buy +100 memory expansion while signed in
- [ ] Confirm `/api/memory/topup` increments server storage bonus
- [ ] Reinstall or relaunch app and confirm token/memory purchases are restored from server state

### 6. Supabase Per-User Memory Integrity
- [ ] Each signed-in user reads/writes only their own aura_user_memory row
- [ ] Merge logic works on reinstall/sign-in/sign-out/switch-account
- [ ] Memory state persists across relaunch and fresh install
- [ ] RLS and user scoping verified end-to-end

### 7. AI Quality + Personalization
- [ ] Cloud AI path (DeepSeek via Together) is reachable and stable
- [ ] Personalization context is included in prompts and retained across sessions
- [ ] Fallback behavior when API fails (no crash, graceful messaging)

### 8. Stability Gate
- [ ] Free tier works without crash
- [ ] Paid tier works without crash
- [ ] Offline mode fails gracefully
- [ ] Kill app and reopen — state persists
- [ ] No blocking console/runtime errors in Xcode logs

### 9. URLs, Deep Links, Website/Shop
- [ ] Shop website URL correct everywhere (paywall, settings, legal, CTAs)
- [ ] Open-in-browser works from iOS app
- [ ] Terms of Service link works
- [ ] Privacy Policy link works

### 10. Notifications
- [ ] Daily horoscope notification scheduling/delivery on physical iPhone
- [ ] Daily affirmation notification scheduling/delivery
- [ ] Permission states (granted/denied) reflected in UI
- [ ] Notifications survive app relaunch

### 11. Apple Approval Hardening
- [ ] In-App Purchase capability present and working
- [ ] Restore purchases visible and functional
- [ ] Accurate subscription disclosures (billing, renewal, cancellation)
- [ ] Privacy policy / terms / support links valid and reachable
- [ ] Account delete option (if required by Apple)
- [ ] No crashes or blocking runtime errors in critical flows

### 12. Archive + Upload
- [ ] Increment iOS build number
- [ ] Archive in Xcode
- [ ] Upload build to App Store Connect
- [ ] Submit to internal TestFlight
- [ ] Test on at least 2 real devices / Apple IDs
- [ ] Submit for external TestFlight, then App Review

---

## PHASE A: Dashboard Setup — COMPLETE

### Supabase
- [x] Create Supabase project (jbabssesevowywncmtcm)
- [x] Enable Email OTP auth provider
- [x] Run database schema SQL
- [x] Enable Row Level Security on user_usage and user_entitlements tables
- [x] Anon key set in config.js
- [x] Service role key set on Render

### RevenueCat
- [x] Create project, add iOS app (com.auralife.app)
- [x] Add Apple App Store Connect API key
- [x] Create entitlements: `premium_access`, `pro_access`
- [x] Create products (premium.monthly, pro.monthly, tokens.25k, memory.100)
- [x] Map products to entitlements
- [x] Create "default" offering
- [x] Set webhook URL
- [x] Keys set in config.js and Render

### App Store Connect
- [x] Create app record for com.auralife.app
- [x] Create subscription group "Aura Subscriptions"
- [x] Add subscription + consumable products
- [x] Generate Shared Secret, paste into RevenueCat
- [x] Fill in app metadata
- [x] Upload screenshots
- [x] Set privacy policy + support URLs

### Website (auraguide.com)
- [x] Terms of Service at /terms
- [x] Privacy Policy at /privacy

---

## PHASE B: Keys — COMPLETE

### Client config — /public/config.js
- [x] Supabase anon key set
- [x] RevenueCat Apple key set

### Server env — Render dashboard
- [x] SUPABASE_SERVICE_ROLE_KEY
- [x] REVENUECAT_SECRET_API_KEY
- [x] REVENUECAT_WEBHOOK_AUTH
- [x] TOGETHER_API_KEY

---

## PHASE C: Code Cleanup — COMPLETE

- [x] Apple Sign-In removed (email OTP is sole auth method)
- [x] Horoscope section collapsible with lux styling
- [x] Separate horoscope/affirmation notification toggles
- [x] Birth time/location skippable in onboarding
- [x] Dead code and unused CSS removed
- [x] Sync script created (scripts/sync-ios-web.sh)
- [x] RevenueCat init, purchase, restore flows
- [x] Server auth middleware + token metering
- [x] RevenueCat webhook handler
- [x] Token balance + memory tracking (client + server)
- [x] Free tier local AI responses
- [x] Settings usage bars (tokens, memory, reset countdown)
- [x] Terms/Privacy links on paywall, entry, settings, disclaimer
