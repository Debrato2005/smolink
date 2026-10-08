# Smolink frontend

**Owner:** Frontend entrypoint

Smolink's React application is a presentation layer over explicit HTTP contracts. This directory contains an executable foundation and its engineering documentation.

## Current status

The app uses a neobrutalist Smolink system built from three references: a sky-blue page grid, a sticky navbar with boxed hover, focus, and active states, a 40/60 desktop hero with text on the left and the shortener on the right, color-filled feature cards, and a result ticket. Sign-in offers Continue with Google beside email. Development data (`npm run dev`) shows every journey. Production connects guest creation only and marks QR, accounts, click stats, and redirects as coming soon until backend contracts exist.

Read the [current handoff](docs/HANDOFF.md) for observed checks and blockers. The [implementation queue](docs/BUILD_CHECKLIST.md) owns task status.

## Prerequisites

Use Node `^22.22.0 || >=24.0.0`, npm, and Python 3 for the document check. The router requires Node 22.22 or later. The lockfile is npm's `package-lock.json`. Use one package manager.

## Quick start

Run these commands from `frontend/`:

```bash
npm ci
npm run dev
```

Open [the local preview](http://127.0.0.1:3000). The port matches the backend template's frontend email-link origin. `.env.fixture` explicitly selects fixtures. No backend service is needed. The development-only Developer tools panel identifies local data. Reload clears local changes.

For live guest creation, start the backend with the [root development guide](../docs/development.md), then run:

```bash
npm run dev:live
```

The development proxy sends `/api` to `http://127.0.0.1:8000`. Live errors remain live errors. Fixtures never replace them. Redirect, QR, and owner endpoints remain unavailable. Local authentication is implemented in backend source, but frontend session integration remains blocked.

## Commands

| Command                                          | Purpose                                                           |
| ------------------------------------------------ | ----------------------------------------------------------------- |
| `npm ci`                                         | Install the exact lockfile                                        |
| `npm run dev`                                    | Start explicit fixture development on port 3000                   |
| `npm run dev:live`                               | Start live HTTP development                                       |
| `npm run typecheck`                              | Check strict TypeScript                                           |
| `npm run lint`                                   | Check JavaScript/TypeScript with zero warnings                    |
| `npm run format`                                 | Format maintained frontend files                                  |
| `npm run format:check`                           | Check formatting                                                  |
| `npm test`                                       | Run focused contract tests, including a real loopback HTTP server |
| `npm run test:watch`                             | Watch focused tests                                               |
| `npx playwright install chromium firefox webkit` | Install pinned browser runtimes                                   |
| `npm run test:e2e`                               | Run the fixture browser suite in all three engines                |
| `npm run test:e2e -- --project=chromium`         | Run the Chromium subset                                           |
| `npm run build`                                  | Typecheck and build live production assets                        |
| `SMOLINK_E2E_TARGET=production npm run test:e2e` | Check built assets with injected API failure                      |
| `npm run preview`                                | Serve the production build on port 4173                           |
| `npm run docs:check`                             | Check document structure                                          |

Set `SMOLINK_CHROMIUM_PATH` when the host cannot download the pinned Chromium. Playwright starts its own fixture server on port 3100. Production checks use port 4173. Keep those ports free; ordinary development uses port 3000. Browser installation can require host libraries. Record missing libraries as environment blockers instead of a pass.

## Environment

[.env.example](.env.example) lists public settings. Do not put secrets in `VITE_` variables. Vite embeds them in the browser bundle.

| Variable            | Default                 | Rule                                                                                       |
| ------------------- | ----------------------- | ------------------------------------------------------------------------------------------ |
| `VITE_DATA_SOURCE`  | `live` when unset       | `fixture` or `live`. Production rejects fixtures                                           |
| `VITE_API_BASE_URL` | `/api/v1`               | Same-origin path or HTTPS URL ending in `/api/v1`, without credentials, query, or fragment |
| `SMOLINK_API_PROXY` | `http://127.0.0.1:8000` | Development server only. Does not define production hosting                                |

A local override belongs in ignored `.env.local` or `.env.<mode>.local`. An inherited environment variable overrides mode files. Check the selected mode and the development-only Developer tools panel. Production builds must use live mode, even when a developer used fixtures earlier.

## Directory and document map

```text
src/app/             router, shell, navigation focus, render boundary
src/routes/          page composition and unavailable shells
src/features/shorten/ destination preview interaction
src/components/ui/   shared consumed primitives
src/lib/api/         transport, errors, contracts, adapters, gateways
src/lib/config/      explicit runtime configuration
src/styles/          canonical tokens and shared styles
tests/e2e/           browser behavior, reflow, keyboard, axe checks
docs/                canonical engineering owners and verifier
```

The [document index](docs/README.md) maps authority, read triggers, and update triggers. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) preserves adopted source and font licenses. Installed skills remain in `.agents/skills/`. They are outside formatter and application dependency scope.
