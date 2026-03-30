# Aura App New Mac Studio Migration Checklist

Use this checklist to move the project safely and get building quickly.

## 1. Before You Move (Old Mac)

- [ ] Commit all code changes.
- [ ] Push to remote (`main` + any active branches).
- [ ] Verify secrets are not only local and undocumented.
- [ ] Export a secure copy of credentials you will need:
  - Apple Developer account access
  - Supabase keys (anon + service role if used)
  - RevenueCat API keys / project IDs
  - Any LLM/API keys (Together, etc.)

### Commands (Old Mac)

```bash
git status
git add -A
git commit -m "Checkpoint before Mac migration"
git push origin main
```

## 2. New Mac Base Setup

- [ ] Sign into Apple ID on macOS.
- [ ] Install Xcode from App Store.
- [ ] Open Xcode once and let it install components.
- [ ] Install Command Line Tools.
- [ ] Install Homebrew.
- [ ] Install Node + CocoaPods + Git helpers.

### Commands (New Mac)

```bash
xcode-select --install

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install node
brew install cocoapods
brew install git
```

## 3. Clone Project Fresh

- [ ] Clone from remote (do not AirDrop/copy the working folder).
- [ ] Open the project root in terminal.

### Commands

```bash
git clone <YOUR_REPO_URL>
cd "<YOUR_REPO_FOLDER>/ios/App"
```

## 4. Restore JavaScript + Capacitor Dependencies

- [ ] Install Node dependencies.
- [ ] Verify Capacitor tooling is available.
- [ ] Sync web assets/plugins to iOS project.

### Commands

```bash
npm install
npx cap sync ios
```

If your setup uses Cordova/Capacitor plugins heavily, also run:

```bash
npx cap doctor
```

## 5. Restore iOS CocoaPods

- [ ] Install/update pods in the iOS workspace.
- [ ] Open the workspace (not `.xcodeproj`).

### Commands

```bash
cd App
pod install
open App.xcworkspace
```

If pods fail:

```bash
pod repo update
pod install
```

## 6. Recreate Local Secrets and Config

- [ ] Recreate any `.env`/local config files not in git.
- [ ] Verify runtime config in `App/App/public/config.js` if applicable.
- [ ] Confirm API URLs and keys are present.

Suggested minimum checks:

- [ ] Aura backend base URL correct
- [ ] Together/Supabase/RevenueCat keys present
- [ ] Production vs dev flags correct

## 7. Xcode Signing + Device Setup

- [ ] In Xcode: `Xcode > Settings > Accounts` add your Apple Developer account.
- [ ] Select project target and set Team under Signing & Capabilities.
- [ ] Confirm Bundle Identifier matches your Apple Developer/App Store Connect setup.
- [ ] Connect iPhone and trust device/computer.

## 8. First Build Validation (In Order)

- [ ] Build for iOS Simulator.
- [ ] Build for physical iPhone.
- [ ] Run app and verify key flows:
  - [ ] Draw flow
  - [ ] Reading flow
  - [ ] Chat flow
  - [ ] Settings toggles (audio/SFX/blue light)

## 9. Common Fixes If Build Fails

### A) Derived Data problems

```bash
rm -rf ~/Library/Developer/Xcode/DerivedData
```

### B) Pods out of sync

```bash
cd "<YOUR_REPO_FOLDER>/ios/App/App"
pod deintegrate
pod install
```

### C) Capacitor files stale

```bash
cd "<YOUR_REPO_FOLDER>/ios/App"
npx cap sync ios
```

### D) Wrong Xcode selected

```bash
sudo xcode-select -switch /Applications/Xcode.app/Contents/Developer
```

## 10. Release-Readiness Checks

- [ ] `APP_STORE_RELEASE_CHECKLIST.md` reviewed.
- [ ] App version/build number updated.
- [ ] App icons/splash/metadata still correct.
- [ ] TestFlight build succeeds.

## 11. Optional: One-Time Bootstrap Script

Run this after clone (from `ios/App`):

```bash
npm install && npx cap sync ios && cd App && pod install && open App.xcworkspace
```

## 12. Security Notes

- Never commit private keys or service-role secrets.
- Keep production keys in secure storage (1Password, Bitwarden, etc.).
- Prefer server-side validation for subscription entitlements.

---

If you want, create `MIGRATION_NOTES.md` beside this file with your exact values for:

- repo URL
- bundle identifier
- supabase project URL
- revenuecat project/app identifiers
- env keys required

That makes future machine setup much faster.
