#!/bin/bash
# Sync web assets from repo root into the iOS bundle.
# Run this before building in Xcode.
#
# Usage:  ./scripts/sync-ios-web.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IOS_PUBLIC="$REPO_ROOT/ios/App/App/public"
DIST="$REPO_ROOT/dist"

echo "Syncing web assets → iOS bundle..."

# Repo root → dist (Capacitor webDir)
cp "$REPO_ROOT/index.html"       "$DIST/index.html"
cp "$REPO_ROOT/public/config.js" "$DIST/config.js"

# dist → iOS runtime bundle
cp "$DIST/index.html"  "$IOS_PUBLIC/index.html"
cp "$DIST/config.js"   "$IOS_PUBLIC/config.js"

# Sync deck data if present
if [ -d "$REPO_ROOT/public/decks" ]; then
    cp -R "$REPO_ROOT/public/decks/" "$IOS_PUBLIC/decks/"
fi

echo "Done. Files synced:"
echo "  index.html  → dist/ → ios/App/App/public/"
echo "  config.js   → dist/ → ios/App/App/public/"
echo ""
echo "Now rebuild in Xcode."
