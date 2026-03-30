# AURA

AURA is a mobile-first self-reflection app built around card draws, guided prompts, conversational AI, and premium subscription features.

This repository is for the AURA app only. It is separate from the ARCHAI project and should be presented as its own product, codebase, and GitHub presence.

## What Is In This Repo

- `index.html`: the main single-page frontend
- `ios/App`: Capacitor iOS wrapper and Xcode project
- `server/server.js`: Node backend for AI, auth-aware metering, and purchase-related state
- `server/prompts`: editable AI prompt files and prompt profiles
- `public`: static assets, decks, and frontend config
- `tools/aura-orb-generator-v4.html`: standalone orb generator used to create artwork for t-shirts, posters, cards, and related AURA visuals

## Core Stack

- Capacitor iOS app shell
- Supabase for authentication and backend data
- RevenueCat for subscriptions and purchase handling
- Together AI for cloud model access
- Express-based Node server for app API routes

## Main Product Areas

- card-based reflection experience
- conversational AI guidance
- free and paid tiers
- token and memory allowances for premium users
- iPhone app build and App Store/TestFlight workflow

## Creative Tools

The repo includes a supporting creative production tool:

- `tools/aura-orb-generator-v4.html`

Use it to generate orb artwork for:

- t-shirts
- posters
- cards
- other AURA brand and product assets

To use it:

1. Open `tools/aura-orb-generator-v4.html` in a browser.
2. Generate and refine the orb artwork.
3. Export the resulting visual for print or design workflows.

## Local Development

### Install dependencies

```bash
npm install
```

### Run the frontend locally

```bash
npm run dev
```

### Run the backend locally

```bash
npm run start:api
```

### Build and sync the iOS app

```bash
npm run ios
```

This runs:

- `npm run build`
- `npx cap sync ios`
- `npx cap open ios`

## Environment Setup

### Frontend config

Edit `public/config.js` for hosted app settings such as:

- API base URL
- Supabase public config
- RevenueCat public Apple key

### Server config

Copy:

```bash
cp server/.env.example server/.env
```

Then configure:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `REVENUECAT_SECRET_API_KEY`
- `REVENUECAT_WEBHOOK_AUTH`
- `TOGETHER_API_KEY`

## AI Prompt Editing

You can tune the app’s AI behavior by editing:

- `server/prompts/system_prompt.txt`
- `server/prompts/prompt_db.json`
- `server/prompts/soul.md`

## iOS Release Notes

For iPhone builds and release prep, see:

- `ios/App/APP_STORE_RELEASE_CHECKLIST.md`

## License

This repository is licensed under Apache 2.0. See `LICENSE`.
