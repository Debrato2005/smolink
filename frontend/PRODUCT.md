# Product

Smolink is a URL shortener. A person pastes a long `http://` or `https://`
address and receives a short public link. This file records product truth for
design work. The root [README](../README.md) owns architecture and API
contracts. [docs/WORKFLOW.md](docs/WORKFLOW.md) owns route availability.

Facts marked _(inferred)_ come from repository documents and the October 7,
2026 redesign brief. No product-owner interview confirmed them.

## Platform

web

## Stack

React 19 single-page application with TypeScript, Vite, React Router, Base UI
primitives, and plain CSS custom properties. FastAPI backend under `/api/v1`.

## Users

- Guests who need one short link quickly, without an account. This is the
  primary audience.
- Account owners who return to manage their links and read click reports.
  _(inferred)_ They share links for projects, events, print material, and
  social posts.

## Product Purpose

Turn a long URL into a short link fast. Optionally name it with an alias and
give it an expiry. Copy it or take a QR code. Owners later find, edit, pause,
delete, and measure their links.

## Positioning

A small, direct tool with a strong personality. Speed and clarity of the
shortening task come before decoration. _(inferred)_ It must not read as a
generic SaaS landing page.

## Operating Context

Daytime, light environment, desktop and phone. Often a paste-and-go task that
takes seconds. Workspace sessions are short and scan-heavy.

## Capabilities and Constraints

Backend status, from the root README endpoint table:

- Implemented: guest or owned URL creation (`POST /api/v1/urls`) with optional
  alias and expiry; local register, login, refresh, logout, verify, resend,
  forgot, and reset.
- Not implemented: owner list, update, delete, analytics, QR, public redirect,
  and Google sign-in.
- Browser session delivery, lossless public IDs, and production origins are
  unresolved. See the frontend handoff blockers.

Design must never imply an unimplemented capability works. Production marks
missing features as coming soon. Local development data stays out of
production builds.

## Brand Commitments

- Neobrutalism defines components, Bauhaus defines composition, and Pop Art
  supplies limited accents. The root
  [frontend design system](../docs/frontend-design-system.md) pins the palette
  and font families.
- No gradients, glass, glow, soft shadows, or generic rounded SaaS styling.
- Voice: short, warm, plain. "Smol" is the brand word. Errors stay direct.
- Copy never calls the product a demo or its data a sample. Missing backend
  features are "coming soon". (User decision, October 7, 2026.)

## Evidence on Hand

No real customer quotes, metrics, logos, or screenshots exist. Do not invent
claims. Sample data stays labeled as sample data.

## Product Principles

1. The shortening task is reachable in the first viewport on every width.
2. Show the product doing its job instead of describing it.
3. Every state is explicit: loading, empty, error, unavailable, uncertain.
4. Expression at the edges, calm in the work area.

## Accessibility & Inclusion

Target WCAG 2.2 AA. Keyboard operation, visible focus, 320 px reflow, reduced
motion, and text alternatives for every chart. Color never carries meaning
alone.
