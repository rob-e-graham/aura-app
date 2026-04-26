# AURA Tomorrow Launch Status

Updated: 2026-04-20
Repo: `/Users/robgraham/Desktop/APPS/AURA app final`

## What I verified tonight

### Repo / project
- Active repo found at `/Users/robgraham/Desktop/APPS/AURA app final`
- Git remote: `https://github.com/rob-e-graham/aura-app.git`
- Branch: `main`
- Latest commit: `379602e Add account deletion for Apple approval, daily screen matches chat layout`

### Web build
- `npm run build` passes cleanly
- Production assets are generated into `dist/`

### Backend / hosted service
- Hosted API base in `public/config.js`: `https://aura-app-8va5.onrender.com`
- `GET /api/health` is live and returned:
  - `ok: true`
  - provider: `together`
  - Together key configured: true
  - Supabase configured: true
  - RevenueCat configured: true
- `GET /terms` is live
- `GET /privacy` is live

### iOS wrapper
- iOS project exists:
  - `ios/App/App.xcodeproj`
  - `ios/App/App.xcworkspace`
  - `ios/App/App/App.entitlements`
- Bundle ID confirmed in Xcode project file:
  - `com.auralife.app`
- `npm run cap:sync` now passes successfully
  - Important: it required UTF-8 locale env vars
  - Working command:
    - `export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 && npm run cap:sync`

## Real blockers still requiring device / human verification

These are the things that are still not honestly "done" until tested on a physical iPhone / Xcode / sandbox Apple ID:

### RevenueCat / billing
- Premium purchase opens Apple sheet
- Pro purchase works
- Restore Purchases works
- Token top-up consumable works
- Memory top-up consumable works
- App fails closed if billing is unavailable

### Auth / account
- Fresh install on physical iPhone
- OTP sign-in end to end
- Session restore after relaunch
- Sign-out / sign-back-in test
- Continue-without-account flow on device

### Memory integrity
- Verify each user only sees their own memory data
- Verify memory persists across relaunch / reinstall / account switch

### Notifications
- Horoscope notification scheduling and delivery
- Affirmation notification scheduling and delivery
- Permission state reflected correctly in UI

### Apple approval hardening
- Verify In-App Purchase capability in Xcode Signing & Capabilities
- Confirm restore flow is visible and functional
- Final no-crash pass in key flows

## Important local repo state
There are local uncommitted changes right now:
- `index.html`
- `tools/aura-orb-generator-v4.html`
- untracked tool files and `.claude/`

The `index.html` changes look product-facing and likely relevant to launch UX.
They should be reviewed and either committed deliberately or stashed before final archive/upload work.

## One useful operational note
Local `server/.env` is not present in the repo right now.
That is not blocking the hosted Render backend, which appears healthy, but it does mean local server boot depends on recreating env vars if needed.

## Best plan for tomorrow
1. Review and commit or stash the current local UI changes.
2. Open Xcode and verify In-App Purchase capability + signing.
3. Install to physical iPhone.
4. Run auth flow.
5. Run sandbox purchase + restore flow.
6. Verify `/api/account/state` updates after purchase.
7. Do one final go/no-go pass before TestFlight / release.

## My honest read
AURA is not "imaginary" or blocked at the infrastructure layer.
The web build works, the hosted backend is up, legal pages are live, and the iOS wrapper syncs.
The remaining risk is mostly in the last-mile Apple / device / purchase verification layer.
