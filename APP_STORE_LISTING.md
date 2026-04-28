# AURA — App Store Connect Listing

Everything you need to paste into App Store Connect. Sections map 1:1 to the
form fields. Anything in `[brackets]` is a choice you make.

---

## Build settings (already done in Xcode)

| Field | Value |
|---|---|
| Bundle ID | `com.auralife.app` |
| Version | `1.0.0` |
| Build | `1` (auto-increment for each upload) |
| Team | Rob Graham (9F72SM2FBF) |

> **First upload:** Build = 1. Each subsequent archive must use a **higher**
> build number even if version stays the same. Bump it to `2`, `3`, etc.
> before each `Product → Archive`.

---

## App Information (App Store Connect → App Information)

### Name (max 30 characters)
> Apple requires this to be unique across the App Store. Three options in
> case "AURA" alone is taken — **try them in this order**:

1. `AURA` *(if available, take it)*
2. `AURA — Cards & Reflection` *(28 chars)*
3. `AURA Self Discovery` *(19 chars)*

### Subtitle (max 30 characters)
> Aligned with the locked tagline (`MARKETING_COPY.md`):
> *"AURA - Unlock AI with Timeless Wisdom & Self Reflection."*

Primary: `AI · Wisdom · Reflection` *(24 chars)*

Alternates:
- `Calmer AI · Timeless Wisdom` *(27 chars)*
- `AI guided by Wisdom & Cards` *(27 chars)*
- `Card readings & AI reflection` *(29 chars — original)*

### Bundle ID
`com.auralife.app` *(already set in Xcode)*

### Primary Category
**Lifestyle**

### Secondary Category
**Health & Fitness**

### Age Rating
**12+** — questions on the age-rating questionnaire:
- *Infrequent/Mild Mature/Suggestive Themes:* **Yes** *(mystical / divinatory themes)*
- *Infrequent/Mild Medical/Treatment Information:* **No** *(disclaimer makes clear it's not medical)*
- Everything else: **No**

---

## Pricing & Availability

- **Price:** Free *(monetised via in-app subscription through RevenueCat)*
- **Availability:** All territories *(or restrict if you want; Worldwide is fine)*

---

## App Privacy (very important — Apple gates the upload on this)

Click **App Privacy → Get Started** in App Store Connect.

### Data collected

- **Email Address** — Linked to user, used for: *App Functionality (account login)*
- **User Content (chat with AURA Guide)** — Linked to user, used for: *App Functionality* — **Note: not used for tracking**
- **Crash Data** — Not linked to user *(if you enable Apple's analytics)*

### Data NOT collected
- Health
- Location
- Contacts
- Photos
- Browsing history
- Advertising data
- Identifiers for advertising

### Tracking
- **Does the app track users?** **No**

---

## Version Information (App Store tab → 1.0.0 Prepare for Submission)

### Promotional Text (max 170 characters — can update anytime without review)
> Unlock AI with Timeless Wisdom and Self Reflection. Pull a card, hear yourself think, and chat with AURA through a calm daily ritual.

*(141 chars — fits)*

### Description (max 4000 characters)

**Core positioning line to keep consistent across launch materials:**
> AURA - Unlock AI with Timeless Wisdom & Self Reflection.

```
AURA is a calm, beautiful self-discovery app for everyday reflection.

Pull a card. Sit with the colour. Read the message. Chat with AURA — your AI reflection guide — about what came up.

Each card is paired with a chromotherapy colour palette, an archetypal name, a meaning, and a quiet affirmation. Three-card spreads (Past · Present · Future), single-card focus readings, and a daily card give you a different rhythm for whatever the day asks for.

WHY AURA IS DIFFERENT

· 78 cards reimagined with one-word archetypal names — Leap, Bloom, Stillness, Threshold — built from the wisdom of the traditional tarot but reframed for modern self-reflection
· Every card has its own three-colour chromotherapy palette and a luminous orb that holds your attention while you read
· An AI reflection guide responds in your tone, remembers your reading, and asks the next question instead of giving you advice
· Beautifully animated — but designed for stillness, not stimulation
· Optional Light Cards mode for daytime / accessible reading

WHAT YOU CAN DO

· Pull a daily card every morning
· Lay a Past · Present · Future spread when something is unclear
· Talk to AURA about your reading in plain language
· Save and share readings as Instagram-ready posters
· Personalise your guide with your name, intention, and zodiac for warmer reflections

A NOTE ON SAFETY

AURA supports self-reflection. It is not therapy, medical advice, or crisis support. If you're struggling, please reach out to a qualified professional or your local crisis line.

PRIVACY

· No tracking, no advertising
· Your messages and readings are private — used only to power your reading and conversation
· Free tier: full card readings + a generous AI quota
· Premium tier: unlimited AI conversation, memory across sessions
· Pro tier: optional on-device AI for full privacy

Made with care, for people who want a quieter way to know themselves.
```

*(~1850 chars — well under the 4000 limit, leaves room to expand later)*

### Keywords (max 100 characters total, comma-separated)
> Use the entire 100-char budget — these drive discovery. **No spaces between commas.**

```
tarot,oracle,cards,reading,reflection,journal,meditation,mindfulness,daily,affirmation,self,aura
```

*(98 chars)*

### Support URL
`https://aura-me.square.site/`
*(or your actual support page — make sure the URL is live before submitting)*

### Marketing URL (optional but recommended)
`https://aura-me.square.site/`

### Privacy Policy URL (required)
`https://aura-app-8va5.onrender.com/privacy`

### Copyright
`© 2026 Rob Graham`

### Sign-In Information (only if reviewer needs to log in)
- Username: *create a test account, e.g. `apple-review@aura-me.test`*
- Password: *(provide one)*
- Notes: *"Sign in with email + 6-digit code. The code is sent to the address above; you can also use 'Continue without an account' to skip auth entirely and access all reading features."*

---

## What to Test (TestFlight tab → Test Information)

### Beta App Description (max 4000 chars — shown to testers in TestFlight app)
```
AURA is a calm self-reflection app — pull a card, sit with the colour, talk to your AI guide.

This is the first beta. Things should mostly work, but if you hit anything weird I'd love to hear about it.
```

### What to Test (max 4000 chars)
```
Thanks for testing AURA. Here's what would help most:

DAILY USE
· Pull a daily card each morning. Does it feel like a calm 30-second ritual?
· Try a 3-card spread (Past · Present · Future). Does the AURA reflection at the bottom feel personal?

CARDS
· Try the Light Cards toggle in Settings → Card Style. Does the reading feel easier on the eyes?
· Tap on individual cards to highlight them. Are the panels readable?

CHAT
· Talk to AURA about a card you pulled. Does it feel like a conversation, not a lecture?
· Free tier gets a daily quota — let me know if you hit it sooner than feels fair.

SHARING
· Tap the share button after a reading. Does the generated image look good in your camera roll? Try sharing to Instagram or saving for later.

ANYTHING ELSE
· Anything that looked broken, slow, ugly, or confusing — tell me.
· Anything that made you smile — also tell me.

Crashes are sent automatically. For everything else, reply to this TestFlight invite or message me directly.
```

### Email
`[your contact email]`

### Phone (optional)
`[your number]`

### Privacy Policy URL
`https://aura-app-8va5.onrender.com/privacy`

### License Agreement
*Use Apple's standard EULA (default).*

---

## Screenshots (App Store tab → 6.7" Display)

> **Required:** 6.7" iPhone screenshots (1290×2796px). Apple uses these for
> all iPhone sizes. **Optional:** iPad screenshots only if you support iPad.

### What to capture (5–6 screenshots is the sweet spot)

1. **Entry screen** — AURA wordmark + sparkle logo + atmospheric purple orb
2. **3-card spread (dark)** — the moment after pulling, all three cards visible with their orbs
3. **Card detail with AURA reflection** — scrolled down, showing the AI reflection panel
4. **Chat with AURA** — mid-conversation
5. **Light Cards mode** — same 3-card spread but with white cards (shows the toggle range)
6. *(optional)* **Daily card** with affirmation

### How to capture them

**On a real iPhone 15 Pro Max / 16 Pro Max / 17 Pro Max:**
- Press Volume Up + Side Button → screenshot saves to Photos
- These are exactly the right resolution

**In iPhone simulator:**
- Run on iPhone 15 Pro Max or larger simulator
- `Cmd+S` saves screenshot to Desktop
- File → Save Screen — also works

**Pro tips:**
- Hide the status bar / use clean status (full battery, full signal, 9:41 — the legendary Apple-marketing time) by running in simulator with `xcrun simctl status_bar booted override --time "9:41" --batteryState charged --batteryLevel 100 --cellularBars 4 --wifiBars 3`
- App Store Connect lets you also drop **gradient backgrounds with text overlays** if you want polished marketing screenshots — but raw app screenshots are 100% acceptable for first launch

---

## Final pre-submission checklist

Before clicking **Submit for Review** in App Store Connect:

- [ ] App icon shows up correctly in `Assets.xcassets/AppIcon` *(✓ already done)*
- [ ] Version `1.0.0` / Build `1` *(✓ already done)*
- [ ] Bundle ID `com.auralife.app` matches App Store Connect *(✓ already done)*
- [ ] Build successfully archived and uploaded via Xcode → Organizer
- [ ] Privacy Policy URL loads (https://aura-app-8va5.onrender.com/privacy)
- [ ] Support URL loads
- [ ] Test account created (if reviewer needs to log in)
- [ ] At least 1 screenshot uploaded (6.7" iPhone, 1290×2796)
- [ ] All required fields above filled in

---

## TestFlight flow (the order things happen)

1. **You:** Archive in Xcode → Distribute → App Store Connect → Upload
2. **Apple:** Processes the build (~10–30 min). Email when ready.
3. **You:** Add Internal Testers (up to 100) — your Apple ID + family. **No review needed.** They install instantly.
4. **You:** When ready for wider beta, add External Testers and submit beta info. **Apple does a brief beta review** — first time can take ~24h, after that it's usually minutes.
5. **You:** Get a public TestFlight link to share anywhere.
6. **Testers:** Install **TestFlight** from the App Store → tap your link → install AURA.

You don't need to fill out the full App Store Description / Screenshots / etc. just to test on TestFlight — only **Beta App Description** and **What to Test** (above). The full listing is only required when you click **Submit for Review** to go live on the App Store.

---

## After your first internal test passes — go live

When you're ready to actually launch:

1. Fill in everything under **App Store** tab in App Store Connect (description, keywords, screenshots, all the above)
2. Click **Submit for Review** on the 1.0.0 build
3. Apple reviews (~24–72 hours typical for first submission)
4. Approved → choose immediate or scheduled release
5. AURA appears on the App Store

---

*Generated alongside Build 1 of AURA. Update this doc as the listing evolves.*
