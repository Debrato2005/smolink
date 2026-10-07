# Frontend documentation index

**Owner:** Frontend document index

## Canonical owners

Each concern has one frontend owner. Root documents retain cross-stack product and API authority. They contain pre-scaffold frontend guidance that needs separately authorized reconciliation.

| Document                                             | Purpose and authority                                                       | Read trigger                         | Update trigger                                        |
| ---------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------ | ----------------------------------------------------- |
| [AGENTS.md](../AGENTS.md)                            | Frontend instructions, scope, evidence, tools, completion                   | Every frontend task                  | Agent workflow or ownership changes                   |
| [README.md](../README.md)                            | Concise startup and executable commands                                     | Setup or continuation                | Runtime, commands, environment, or layout changes     |
| This index                                           | Owner mapping and routed startup                                            | Find an owner                        | Ownership or document layout changes                  |
| [FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md) | Stable module, transport, state, privacy, and extension contracts           | Code or dependency changes           | Stable implementation boundary changes                |
| [WORKFLOW.md](WORKFLOW.md)                           | Route behavior and feature availability                                     | Journey or state changes             | User-visible behavior or backend availability changes |
| [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)                 | Visual tokens, components, motion, responsive rules, accessibility baseline | Visual or interaction work           | Deliberate visual system changes                      |
| [TESTING_AND_QUALITY.md](TESTING_AND_QUALITY.md)     | Test selection, browser matrix, quality gates, evidence limits              | Verification or testing work         | Test strategy, tooling, or gates change               |
| [BUILD_CHECKLIST.md](BUILD_CHECKLIST.md)             | Implementation order and current task status                                | Task selection or completion         | Observed acceptance or dependency changes             |
| [SOURCE_LEDGER.md](SOURCE_LEDGER.md)                 | Research, dependencies, alternatives, licenses, replacement boundaries      | External code or dependency adoption | Source, version, or adoption decisions change         |
| [HANDOFF.md](HANDOFF.md)                             | One current volatile continuation checkpoint                                | Every continuation                   | End of an authorized work session. Write last         |

## Startup routing

Read root instructions, frontend instructions, the frontend entrypoint, handoff, and exact FE task. Then read only the stable owners needed for the task. Inspect implementation and nearest tests. Use rendered browser output when layout or interaction matters.

For API work, also read root schemas, route handlers, tests, and the authentication design where relevant. For design work, use the frontend design owner and the Source Ledger. For test work, use root testing policy and the Playbook selection questions.

Do not require all documents for a small task. Do not place command receipts in stable architecture. Do not place session history in the queue. Do not duplicate token values outside CSS.

## Structural validation

Run `npm run docs:check` from `frontend/`. [verify_docs.py](verify_docs.py) checks file presence, owner labels, required sections, local links/anchors, and task structure. It rejects unclassified placeholders in stable contract documents.

This is a structure check. It does not prove semantic truth, API correctness, browser acceptance, accessibility conformance, or live integration.
