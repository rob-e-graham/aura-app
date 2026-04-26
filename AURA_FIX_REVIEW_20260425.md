# AURA Fix + Review — 2026-04-25

## What I fixed

### Navigation / settings
- Patched `index.html` (root source of truth) so the welcome-screen primary controls are explicitly bound and routed:
  - Draw → `goToDrawScreen()`
  - Chat → `openAuraChat()`
  - Daily Guidance → `goTo('dailyScreen')`
  - Settings cog → `goToSettingsHub()`
- Added `bindPrimaryNavigation()` to bind those controls at runtime as a second layer of protection against bad/stale inline routing.
- Hardened `goToSettingsHub()` so helper failures do **not** block the actual screen transition.
- Updated in-screen nav buttons to use the wrapper routes (`goToReadingScreen()` / `goToDrawScreen()`) instead of raw screen jumps where that was causing inconsistent behavior.

### Orb rendering
- Disabled the extra global screen orb on the Daily Guidance screen with:
  - `.daily-screen::before { content: none; }`
- This should stop the doubled-orb effect on the daily/insight screen.

### Purchase flow
- Fixed dev/test unlock flow so it now respects the recorded return screen after purchase/unlock.
- `resolvePostPurchaseReturnScreen()` now runs in the dev fallback path too, not only the RevenueCat native path.

## Build / sync status
- `npm run build` ✅
- `npx cap copy ios` ✅ but **not reliable enough by itself in this repo**
- `./scripts/sync-ios-web.sh` ✅

### Important repo-specific finding
This repo already includes a custom sync script:
- `scripts/sync-ios-web.sh`

Use that after editing `index.html`.

It correctly forces:
- `index.html` → `dist/index.html` → `ios/App/App/public/index.html`
- `public/config.js` → `dist/config.js` → `ios/App/App/public/config.js`

After running the script I verified:
- root `index.html` == `dist/index.html` == `ios/App/App/public/index.html`

## Remaining release blockers / review findings

### 1) RevenueCat key is still test/dev
File:
- `public/config.js`

Current value:
- `window.AURA_REVENUECAT_APPLE_KEY = ... 'test_bmrngPaRezJznfNKVRVFxFhBkSP'`

This must be replaced with the real production Apple public SDK key before release/TestFlight validation.

### 2) Apple Sign-In entitlement still present
File:
- `ios/App/App/App.entitlements`

Current entitlement still includes:
- `com.apple.developer.applesignin`

That conflicts with the documented direction that Apple Sign-In was removed and email OTP is the sole auth method.

### 3) Notifications are still web-style, not native iPhone notifications
In `index.html`, notification logic still uses browser APIs:
- `Notification.requestPermission()`
- `new Notification(...)`

I did **not** find native Capacitor notification usage such as:
- `LocalNotifications`
- `PushNotifications`

So notifications are still likely not production-correct on iPhone and need a native pass.

## Recommended next test in Xcode
1. Stop the current run
2. Product → Clean Build Folder
3. Delete AURA from the device
4. Rebuild and run from `ios/App/App.xcworkspace`

## Source of truth reminder
Edit only:
- `index.html`

Then sync with:
- `npm run build`
- `bash ./scripts/sync-ios-web.sh`

Do **not** hand-edit:
- `ios/App/App/public/index.html`
