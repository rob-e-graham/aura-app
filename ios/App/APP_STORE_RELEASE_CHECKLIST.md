# AURA — App Store Release Checklist

Status key: [x] Done | [-] In progress | [ ] Not started

---

## TESTFLIGHT GATE — DO THESE IN ORDER

### 1. Code + Deploy Sync
- [ ] Push latest code changes to GitHub
- [ ] Confirm Render deploy includes `/api/account/state`
- [ ] Confirm Render deploy includes `/api/memory/topup`
- [x] Run `npm run build`
- [x] Run `npx cap sync ios`
- [x] If pods changed: run `cd ios/App && pod install`

### 2. Native Capability Verification
- [ ] Open Xcode target `App` > Signing & Capabilities
- [ ] Verify `Sign in with Apple` capability is present
- [ ] Verify `In-App Purchase` capability is present
- [ ] Remove any incorrect Apple Pay merchant capability if it was added by mistake
- [ ] Confirm bundle ID is `com.auralife.app`
- [ ] Confirm the correct Team and provisioning profile are selected

### 3. Auth Verification On Physical iPhone
- [ ] Fresh install from Xcode on physical iPhone
- [ ] Email OTP sign-in works end to end
- [ ] Relaunch app and confirm session is still restored
- [ ] Sign out and sign back in successfully
- [ ] Apple Sign-In works on device
- [ ] If Apple Sign-In fails, stop and fix before testing purchases

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

### 6. Stability Gate
- [ ] Free tier works without crash
- [ ] Paid tier works without crash
- [ ] Offline mode fails gracefully
- [ ] Kill app and reopen — state persists
- [ ] No blocking console/runtime errors in Xcode logs during sign-in, purchase, restore, or chat

### 7. Archive + Upload
- [ ] Increment iOS build number
- [ ] Archive in Xcode
- [ ] Upload build to App Store Connect
- [ ] Submit to internal TestFlight
- [ ] Test on at least 2 real devices / Apple IDs
- [ ] Only after passing that, submit for external TestFlight

### Launch Blockers Right Now
- [ ] Either verify native Apple Sign-In works on device, or keep it disabled for this release
- [ ] Verify Xcode `In-App Purchase` capability is enabled correctly
- [ ] Push latest server/client persistence fixes before purchase restore testing

---

## PHASE A: Dashboard Setup ✅ COMPLETE

### Supabase
- [x] Create Supabase project (jbabssesevowywncmtcm)
- [x] Enable Email OTP auth provider
- [x] Enable Apple auth provider
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

### Apple Developer Portal
- [x] com.auralife.app has "Sign in with Apple" capability
- [x] Services ID for Supabase Apple auth callback
- [x] .p8 key generated

### Website (auraguide.com)
- [x] Terms of Service at /terms
- [x] Privacy Policy at /privacy

---

## PHASE B: Paste Keys ✅ COMPLETE

### Client config — /public/config.js
- [x] Supabase anon key set (sb_publishable key)
- [x] RevenueCat Apple key set

### Server env — Render dashboard
- [x] SUPABASE_SERVICE_ROLE_KEY
- [x] REVENUECAT_SECRET_API_KEY
- [x] REVENUECAT_WEBHOOK_AUTH
- [x] TOGETHER_API_KEY

---

## PHASE C: Code Cleanup ✅ COMPLETE

- [x] Remove "beta experiments" language from onboarding
- [x] Add Apple auto-renewal disclosure to paywall
- [x] Add Terms of Service + Privacy Policy links (paywall, entry, settings, disclaimer)
- [x] Add post-trial billing explanation
- [x] Update pricing: Premium $4.44/mo
- [x] Supabase client init + Email OTP auth flow
- [x] Apple Sign-In (native + web fallback)
- [x] RevenueCat init, purchase, restore flows
- [x] Server auth middleware + token metering
- [x] RevenueCat webhook handler
- [x] Token balance + memory tracking (client + server)
- [x] Free tier local AI responses
- [x] Settings usage bars (tokens, memory, reset countdown)
- [x] Remove legacy server stub endpoints
- [x] Remove dev-only Info.plist keys (NSAllowsLocalNetworking removed)
- [ ] Verify Xcode capabilities: In-App Purchase + Sign in with Apple

---

## PHASE D: Build & Deploy

- [x] `npm run build && npx cap sync ios` (if web assets changed)
- [x] `cd ios/App && pod install` (if Podfile changed)
- [x] Xcode build succeeds with no errors
- [x] Push server code to GitHub (rob-e-graham/aura-app.git)
- [x] Render auto-deployed from GitHub push
- [x] `https://aura-app-8va5.onrender.com/api/health` responds

---

## PHASE E: Testing on Device

- [ ] Fresh install on physical iPhone
- [ ] Email OTP sign-in works (receive code, verify, session persists)
- [ ] Apple Sign-In works (native sheet, session created)
- [ ] Free tier: card readings, local AI chat, no token count
- [ ] Subscribe to Premium via paywall — Apple payment sheet appears
- [ ] After subscription: cloud AI chat works, tokens deduct
- [ ] Token count shows in chat header and settings
- [ ] Use all tokens — "Buy More" modal appears
- [ ] Restore purchases on fresh install — tier restored
- [ ] Sign out and sign back in — session restores
- [ ] App works offline (graceful error, no crash)
- [ ] Kill app and reopen — state persists

---

## PHASE F: App Store Submission

- [ ] Archive in Xcode (Product > Archive)
- [ ] Upload to App Store Connect via Organizer
- [ ] Submit for TestFlight review first
- [ ] Test with 2-3 external beta testers
- [ ] Fix any issues found in beta
- [ ] Submit for App Review
- [ ] Respond to any reviewer questions within 24 hours

---

## Current Status

**Infrastructure is mostly in place, but this is not ready to archive yet.**

Current reality:
- Server/client state sync for subscriptions, tokens, and memory is now in better shape.
- The biggest remaining risks are native Apple Sign-In verification and Xcode capability correctness.
- Treat Phase E as a strict go/no-go gate before any archive or App Review submission.
