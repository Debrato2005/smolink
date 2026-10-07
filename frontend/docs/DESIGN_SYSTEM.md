# Smolink design system

**Owner:** Frontend visual and interaction system

## Doctrine and authority

Neobrutalism defines primitive grammar. Bauhaus defines composition. Pop Art supplies controlled accents. Usability, accessibility, content hierarchy, and task completion override all three.

This is the sole frontend owner for visual decisions. It reconstructs the useful specification in root `docs/frontend-design-system.md` without changing that file. The [Source Ledger](SOURCE_LEDGER.md) records checked research. Root product/API authority remains intact.

Use flat fills, structural black outlines, square corners, and zero-blur hard shadows. Build asymmetric macro composition on strong axes. Keep labels, fields, errors, tables, and controls mechanically aligned. Geometry must improve hierarchy, grouping, direction, or recognition.

## Tokens and typography

[src/styles/tokens.css](../src/styles/tokens.css) is the executable source for exact token values. Reference its names instead of maintaining another CSS specification in prose.

| Group     | Contract                                                                                 |
| --------- | ---------------------------------------------------------------------------------------- |
| Structure | Ink `#000000`, paper `#fffdf5`, muted surface and text                                   |
| Accents   | Yellow `#ffd23f`, red `#ff6b6b`, blue `#74b9ff`, green `#88d498`                         |
| Borders   | Thin 2px internal rules. Default 3px controls/panels. Thick 4px emphasis/error           |
| Shadows   | 3px, 5px, or 8px positive x/y offsets. Zero blur                                         |
| Shape     | Radius 0 by default. Semantic circles or geometric motifs can have deliberate exceptions |
| Spacing   | 4px optical step, then 8, 16, 24, 32, 48, 64, and 96px                                   |
| Type      | Space Grotesk 700 headings. Inter 400/600 text. Space Mono 400 codes/results only        |
| Motion    | 120ms CSS control transition. Native scrolling                                           |

The selected Space Grotesk family supports weight 700. Do not synthesize the older draft's suggested 800 weight. Fonts load from pinned Fontsource packages. Only Latin faces and consumed weights enter this bundle. Fontsource CSS includes WOFF2 and WOFF fallbacks. Extend script coverage only for an actual content requirement. Preserve OFL notices.

Keep body text calm, left aligned, and near 45–75 characters per line. Use scale, weight, spacing, and position for hierarchy. Do not use novelty body fonts, pervasive capitals, or excessive monospace.

Use black text on accent surfaces. Applicable contrast targets are 4.5:1 normal text, 3:1 large text, and 3:1 meaningful non-text boundaries/states. Contrast must use actual rendered combinations. Do not infer conformance from palette intent.

## Layout and intensity

The conceptual grid uses 12 desktop, 8 tablet, and 4 mobile columns. Content is bounded to 1280px. Current breakpoints at 1050px and 720px respond to the form and heading fit. They are content decisions, not device promises.

| Intensity  | Use                            | Limits                                                                               |
| ---------- | ------------------------------ | ------------------------------------------------------------------------------------ |
| HIGH       | Public marketing               | Strong asymmetry, large type, poster composition, one print motif. CTA remains clear |
| MEDIUM     | Shortening and auth            | One primary task, conventional forms, limited accents, aligned errors                |
| CONTROLLED | Dashboard, analytics, settings | Small shadows, flat surfaces, regular rows. Data scanning dominates decoration       |

Use no more than two or three saturated accents in a viewport. Remove decoration before hiding a necessary state cue. Pop Art can use original SVG halftones, stripes, bold contours, flat panels, or offset print layers. One expressive gesture is enough. Keep patterns out of body text, fields, tables, and chart data. Do not trace or copy artwork.

On smaller widths, preserve DOM order, collapse columns, simplify asymmetry, and remove overlap before reducing content space. Preserve the 3px structural border and comfortable controls. Long URLs must wrap or use an accessible read-only field. Test 390, 768, 1024, and 1440px, plus 320px reflow.

## Component sources and grammar

Check current neobrutalism.dev first. Adopt suitable shared recipes manually or through the shadcn registry after source review. Map every style to Smolink tokens. The consumed button retains the current Base UI primitive and uses plain CSS instead of installing Tailwind/cva utilities solely for that recipe.

If the registry lacks the required interaction, compose a Base UI primitive with the same tokens. Use a custom shared primitive only for an unmet, consumed interaction with defined accessible behavior. Native labeled inputs remain appropriate for the complete native URL-input interaction.

Current Base UI uses `render`, not old Radix `asChild` recipes. Its Button enforces button semantics. Style real anchors/router links directly when navigation needs button styling. Do not render links through the Button primitive. Future dialogs, menus, and popovers must preserve library focus, naming, dismissal, and restoration behavior.

| State         | Required treatment                                                                          |
| ------------- | ------------------------------------------------------------------------------------------- |
| Default       | Hard shadow, 3px boundary, clear label and hierarchy                                        |
| Hover         | Small counter-shadow translation and lift. No unique information                            |
| Focus-visible | Separate ink outline with offset, visible beyond border and shadow                          |
| Active        | Translation toward the shadow and shadow collapse                                           |
| Disabled      | Native disabled semantics, muted fill, no motion or shadow                                  |
| Loading       | Task-specific status, duplicate-submit prevention, stable geometry                          |
| Error         | Adjacent text, associated field where applicable, structural emphasis. Red is supplementary |
| Selected      | Programmatic state and explicit text, border, or mark                                       |

No isolated page copies of shared controls. Loading/success/error feedback must stay visible in context. Tooltips and toasts cannot carry the sole required instruction or result. Clipboard success requires actual operation success.

## Motion and accessibility

CSS owns simple control motion. No continuous animation, persistent render loop, scroll hijack, or GPU layer exists. Reduced motion removes control transitions and displacement. Settled content remains available. Future motion needs a purpose, cleanup, and reduced-motion behavior. GSAP/Lenis require a measured interaction before adoption.

Target WCAG 2.2 AA. This is not a conformance claim. Require semantic landmarks, logical headings, visible labels, accessible names, associated field errors, keyboard operation, and safe live feedback. Focus must remain visible and unobscured. AA pointer targets require 24px sizing or an applicable exception. Prefer at least 44px standalone targets. Current form controls are at least 48px high.

Dialogs require focus trap/restoration. Forms remain conventional. Confirm success and distinguish empty, error, blocked, unknown outcome, and unavailable states. Color alone never communicates meaning. Test zoom, text spacing, 320px reflow, keyboard, reduced motion, and assistive technology. Axe supports review but cannot certify conformance.

## Forbidden patterns and deferred decisions

Gradients are prohibited, including backgrounds, text, borders, masks, charts, and shaders. Also prohibit glassmorphism, blur panels, glow, soft elevation, glossy surfaces, arbitrary rounded cards, pervasive pills, floating blobs, random rotation, and generic blue-purple SaaS styling.

Dark mode is `DEFERRED`. It needs an actual requirement and a separate contrast-tested palette. Paper Shaders is `EVALUATED_DEFERRED`. React Bits remains `REFERENCE_ONLY`. Native scrolling is the default. No visual package defines Smolink's system.

Figma synchronization is planned external design work. It does not block this explicitly authorized executable foundation. A future library must map token names and component states one to one. Root guidance that requires a complete Figma library before any implementation needs separately authorized reconciliation.
