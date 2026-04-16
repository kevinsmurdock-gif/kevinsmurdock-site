# Kevin Murdock — Full Session Context

_Last updated: 2026-04-14_

This file is the master context dump for new Claude chat sessions. Fetch via:
```
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://serene-purpose-production-3ff4.up.railway.app/api/admin/context
```

---

## Who I Am

- **Kevin S. Murdock** — Healthcare entrepreneur, Greenville, SC
- **The Citadel, Class of 1992** — Gold Star, walk-on soccer, early graduate
- **25+ companies founded**, primarily in healthcare
- Email: `kmurdock@precisiondxgroup.com` / `kevinsmurdock@gmail.com`
- Cell: (864) 386-4683
- LinkedIn: https://www.linkedin.com/in/kevin-murdock-7a64a229/
- Personal site: https://kevinsmurdock.com

## Current Ventures (Precision DX Group holding)

- **RepOS** — AI operating system for independent medical reps (live at app.rep-os.ai)
- **TruView Diagnostics** — CLIA-certified, 207-cancer detection panel
- **GoHigh.AI** — AI voice agents for healthcare
- **BibleAI** — Faith-based AI
- **Precision DX Group** — parent holding company

## Prior Ventures

- **Premier Medical Laboratory Services** (2007–2023) — First SC FDA-validated COVID lab. Up to 300,000 tests/day with pooling. DiabetesPredict exclusive. Lindsey Graham press conference. Yale SalivaDirect designated. 2M+ specimens, 6M kits manufactured.
- **Diversified Medical Healthcare** — holding company, 5 labs across SC/NC/TX/UT/FL, 450 peak employees
- **AstraZeneca** (2001–04) — top national sales territory, launched Nexium + Crestor

---

## Railway Project — GHL Automation Server

- **Repo**: `C:\Users\murkev\ghl-automation-server`
- **URL**: https://serene-purpose-production-3ff4.up.railway.app
- **App domain**: https://app.rep-os.ai
- **Platform**: Node.js / Express on Railway
- **DB**: SQLite on Railway persistent volume (`/data/db/app.db`)
- **6 GHL sub-accounts**: precisiondxgroup, truviewdx, bibleai, sj-skincare, onparo, gohigh (55 total)

### Deploy

```bash
# Clear stale token, then push
unset RAILWAY_TOKEN
cd C:\Users\murkev\ghl-automation-server
MSYS_NO_PATHCONV=1 railway up --detach

# Health check
curl https://serene-purpose-production-3ff4.up.railway.app/health

# Tail logs
MSYS_NO_PATHCONV=1 railway logs -n 30
```

Build takes ~60 seconds. **Always** prefix Railway CLI commands with `MSYS_NO_PATHCONV=1` on Windows Git Bash.

### Key environment vars

- `GHL_API_KEY`, `GHL_LOCATION_ID`
- `ANTHROPIC_API_KEY`
- `ADMIN_TOKEN` — controls access to `/admin/*` and `/api/admin/*`
- `SMS_MODE=test` (test = immediate, production = daily AI summary)
- `BRIEFING_EMAIL`, `BRIEFING_PHONE`

---

## Canonical URLs

### Public

- `/kevinsmurdock` — canonical Kevin profile (RepOS-hosted at `public/KevinMurdock.html`)
- `/KevinMurdock`, `/kevinmurdock`, `/kevin-murdock` — 301 → `/kevinsmurdock`
- `/blueprint` — platform overview
- `/recovery` — universal wound-care recovery page
- `/lp/:slug` — rep landing pages (e.g. `/lp/jan-estes`, `/lp/jennifer-roberts`)
- `/v/:slug` — vendor landing pages

### Admin (require `ADMIN_TOKEN` or admin/manager session)

- `/admin/command-center` — tile grid homebase
- `/admin/reputation-pr` — PR Tracker + Book Project tabs (v3.28)
- `/admin/playbook` — live ops playbook
- `/admin/leads`, `/admin/drip-control`, `/admin/health`, `/admin/enrichment-dashboard`
- `/admin/recovery`, `/admin/templates`, `/admin/analysis-tracker`, `/admin/analysis-signups`
- `/api/admin/context` — this file (v3.29)

### Webhooks

- `POST /webhooks/inbound` — GHL appointment webhooks → AI briefings
- `POST /webhook/sms-forward` — iOS SMS forwarding
- `POST /webhook/sms-forward/productive-call` — call logging
- `POST /webhook/sms-contact-enrich` — iOS Shortcut contact enrichment + NPI lookup

---

## Current Version: v3.29

### Recent Work (April 2026)

- **v3.27** — landing hero rewrite, Sarah Hull NPI fix, playbook audit row
- **v3.28** — /kevinsmurdock profile page launch on RepOS
  - Senator visits (Graham + Scott), charity section, 35+ press outlets
  - Attorney on-record statement, video embed → click-to-watch thumbnail
  - Formspree contact form (ID `xgorwrnb`)
  - Added /admin/reputation-pr with PR Tracker (90-day checklist) + Book Project ("First In", 10 chapters)
  - Standalone `kevinsmurdock.com` site built at `C:\Users\murkev\kevinsmurdock-site\index.html`
- **v3.29** — `/api/admin/context` endpoint for new-session bootstrap

### 90-Day PR Plan (live at /admin/reputation-pr)

- Budget: $2,500
- Phase 1 (days 1-30) Foundation — profile launch, press archive, senator quotes, attorney statement, video embed, SEO audit, LinkedIn/Crunchbase/Google Business
- Phase 2 (days 31-60) Amplification — 3 LinkedIn articles, Citadel alumni feature, PR consultant, UBJ profile, video testimonials, conference speaking
- Phase 3 (days 61-90) Sustain — Google Alerts, weekly content, reputation monitoring, SEO refresh, 90-day retrospective

### Book Project: "First In"

Chapters: The Lab Nobody Believed In · First Responders · The Senators Showed Up · Three Hundred Thousand Tests a Day · N95s and Night Shifts · Profit Share · Fifty-One Million Dollars · The Consent Judgment · What I Built Next · First In, Last Out

Chapter 1 draft complete (April 2026).

---

## Critical Lessons (don't re-learn these)

- **Never redeclare let/const with var across script blocks** — killed login for hours
- **Firebase SDK is self-hosted** — CDN blocked by ad blockers
- **DB seeds must be idempotent** — unconditional UPDATEs overwrote API fixes
- **NPI is master key — never overwrite** — NPI immutable, GHL is child, enrichment additive
- **Always commit, push, deploy at end of session** — no orphaned changes
- **Windows Git Bash** — always prefix Railway CLI with `MSYS_NO_PATHCONV=1`
- **`railway run` uses ephemeral containers** — DB inserts via `railway run` don't persist. Use idempotent seeds in `reposDb.js` or hit live admin endpoints.
- **AI Picks exclusion must happen in BOTH endpoints**: `/briefing` (home preview) AND `/follow-up-picks` (full view)
- **Inline onclick in HTML templates is dangerous** — use data attributes + delegated listeners

---

## Key Files

### Entry + config

- `index.js` — Express entry point, mounts all routers
- `src/config/companies.js` — 6 company configs
- `src/config/brandConfig.js` — product-based routing for outreach (Kevin's cell `(864) 386-4683`)
- `src/config/partners.js` — briefing partners (currently Mark Heiser)

### Core services

- `src/shared/webhooks/eventDispatcher.js` — normalizes 3 GHL payload formats
- `src/shared/handlers/handleAppointmentBooked.js` — appointment → enrichment → AI briefing
- `src/shared/services/briefingGenerator.js` — V7 HTML email + SMS builder
- `src/shared/services/contactEnrichment.js` — GHL + Outscraper + Apollo enrichment
- `src/shared/services/anthropicClient.js` — AI prompt builder
- `src/shared/services/briefingScheduler.js` — triple-send (immediate, T-30, T-15)
- `src/shared/services/smsDebrief.js` — post-call SMS debrief (v2.63, "THE MOAT")
- `src/shared/services/nightlySync.js` — 2 AM ET cross-account reconciliation

### Admin

- `src/shared/admin/commandCenter.js` — `/admin/command-center` grid + `/admin/reputation-pr`
- `src/shared/admin/healthDash.js` — `/admin/health` live dashboard
- `src/shared/admin/adminRouter.js` — admin endpoints router

### Rep portal

- `src/repos/repRoutes.js` — rep portal API (dashboard, AI Picks, dialer, calendar)
- `src/repos/reposDb.js` — SQLite schema + seeds (idempotent!)
- `src/repos/repAuth.js` — rep portal session auth
- `src/repos/calendarOAuth.js` — Google + Microsoft OAuth
- `public/rep/index.html` — single-page frontend (all HTML/CSS/JS in one file)

### Public pages

- `public/KevinMurdock.html` — personal profile page (served at `/kevinsmurdock`)
- `public/admin/reputation_command_center.html` — 90-day PR checklist (iframed)
- `public/blueprint/index.html` — platform blueprint
- `public/lp/jan-estes.html`, `public/lp/jennifer-roberts.html` — rep landing pages

### Standalone

- `C:\Users\murkev\kevinsmurdock-site\index.html` — self-contained kevinsmurdock.com site (not in repo)

---

## GHL API Patterns

- Base URL: `https://services.leadconnectorhq.com`
- Auth: `Authorization: Bearer {PIT_KEY}`, `Version: 2021-07-28`
- Contact search by phone: `GET /contacts/search/duplicate?number=+1XXXXXXXXXX` — returns `res.data.contact` (singular)
- Contact search by name/email: `POST /contacts/search` with `{ locationId, query, pageLimit }` (NOT `limit`)
- Contact create: `POST /contacts/` — returns 400 with `meta.contactId` if duplicate exists
- Contact update: `PUT /contacts/{id}` — does NOT accept `title` field
- Notes: `POST /contacts/{id}/notes` with `{ body, userId }` — use `_skipLocationId: true`
- Notes `dateAdded` is NOT writable — always server-set
- Tasks: `POST /contacts/{id}/tasks` with `{ title, body, dueDate, completed }`
- Opportunities: `GET /contacts/{id}/opportunities` with `location_id` (underscore) + `_skipLocationId: true`
- Conversation inbound: `POST /conversations/messages/inbound` with `{ type: 'SMS', contactId, message, date }`
- Conversation inbound `type: 'Call'` requires `conversationProviderId` — use `SMS` type instead
- Send SMS: `POST /conversations/messages` with `{ type: 'SMS', contactId, message }` — triggers AI chatbot
- Send Email: `POST /conversations/messages` with `{ type: 'Email', contactId, subject, html }`
- LocationId auto-injected by `ghlClient` interceptor — bypass with `{ _skipLocationId: true }`

---

## Cross-Account Sync

- `syncContactAcrossAccounts(sourceContact, sourceSlug)` — searches/creates in all other sub-accounts
- Tag merge: union (additive, case-insensitive dedup) — never removes
- Field fill: blanks only — never overwrites
- Sync filter: bibleai + sj-skincare blocked from all sync
- Medical sync network: precisiondxgroup ↔ truviewdx ↔ onparo ↔ gohigh (all 4 sync freely)
- Nightly reconciliation: 2 AM ET, paginates all contacts, indexes by phone (primary) + email (secondary)
- ContactUpdate propagation: 60s debounce per contactId, 120s loop prevention per phone

---

## Pre-Call Briefing (v3 current)

Triple-send model:
1. **Immediate** — full briefing within seconds of booking
2. **T-30** — 30 min before, fresh re-enrichment + new AI
3. **T-15** — 15 min before, fresh re-enrichment + new AI

Only scheduled if > 10 min out. Reschedule cancels all 3 timers. SMS via GHL Conversations API (not Twilio — A2P 10DLC blocked).

---

## Auth Tokens / Test Credentials

- Admin token: set via `ADMIN_TOKEN` env var
- Rep portal login: `kmurdock@precisiondxgroup.com` / `Repos2026!`

---

## Next Session Priorities

1. Verify SEO indexing of kevinsmurdock.com (Google Search Console)
2. Finish PR Tracker Phase 1 tasks (LinkedIn/Crunchbase/Google Business profiles)
3. Book Project — draft Chapter 2 ("First Responders")
4. iPhone test SMS debrief end-to-end (v2.63)
5. Jennifer Roberts contact card — tappable phone/email
6. Mark Heiser Power Dialer onboarding

---

## How to Bootstrap a New Claude Session

1. Hit `/api/admin/context` with the admin token to get this file
2. Read `CLAUDE.md` in the repo root for project-specific rules
3. Check `git log -20` for recent work
4. Check `memory/MEMORY.md` index for topic-specific memories
5. Check `/admin/playbook` for current P0/P1 action items
