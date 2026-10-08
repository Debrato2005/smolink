# Smolink hero visual QA

**Owner:** Hero reference comparison receipt

Date: October 8, 2026.

final result: passed

## Initial target and evidence

The user requested a treatment along the supplied references. This is a style adaptation within the existing home page, not a full-page clone.

- Source visuals: `.local/hero-reference-review/reference-full.png` and `.local/hero-reference-review/reference-copy.png`.
- Source dimensions: 1993 by 849 pixels and 914 by 789 pixels. The supplied images contain no device-density metadata.
- Implementation: `.local/hero-reference-review/hero-wide.png` and `.local/hero-reference-review/copy-wide.png`.
- Implementation dimensions: 1993 by 848 pixels and 494 by 526 pixels.
- Browser viewport: 1993 by 993 CSS pixels, density 1. The hero capture excludes the existing navbar and highlights strip.
- State: public home, idle form, fixture mode, loaded fonts and artwork.
- Full comparison: `.local/hero-reference-review/comparison-0.png`.
- Focused copy comparison: `.local/hero-reference-review/comparison-1.png`.

Both comparison boards show the source and implementation together. The full images share the same width. The focused images fit their columns without distortion. The one-pixel height difference does not affect this review. Reference export density is unknown, so the review compares hierarchy and treatment rather than literal CSS dimensions.

## Required fidelity surfaces

| Surface              | Observed result                                                                                                                                                                                                                                                       |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fonts and typography | Loaded Inter 900 gives the headline the reference's heavy weight. Tight tracking and two lines preserve its hierarchy. The source does not identify its exact font. Other text keeps the installed type system.                                                       |
| Spacing and layout   | The existing 40/60 split and 1280px content limit remain. This makes the wide hero smaller than the reference. The form stays centered and the strip stays at the viewport bottom when content fits. Phone content stacks. Rounded form corners follow the reference. |
| Colors and tokens    | Black, paper, sky, and yellow use existing tokens. The headline has a flat yellow highlight. The yellow action keeps a hard black shadow. The existing grid stays visible behind the copy.                                                                            |
| Image quality        | The transparent artwork contains the long-link sticker, short-link sticker, curved arrow, and ink rays. Text remains readable at normal desktop and phone sizes. The image decoded at its natural 2172 by 724 pixels.                                                 |
| Copy and content     | The headline and description follow the reference. The URL illustration uses example text and has a descriptive alt attribute. It is separate from the generated result.                                                                                              |

## Findings and comparison history

No actionable P0, P1, or P2 findings remain within this scope. The final comparison followed the heavier type adjustment and isolated font alias. The alias keeps the added weight from changing other controls.

The wide content limit and centered phone copy are existing layout decisions. The blue background shape was added in the later user-requested refinement. The handwritten caption was not adopted. The task focuses on the hero copy and related control treatment. Existing helpers, expiry controls, and result behavior remain present.

## Interaction and responsive evidence

Six focused Chromium fixture checks passed. They cover reflow and axe at 320, 390, 768, 1024, and 1440px. They also check the centered panel, output below input, expansion in both directions, and desktop result visibility without scrolling.

The browser review found no console or page errors. The hero font loaded. Increased text spacing at 320px caused no page overflow. Receipts: `.local/hero-reference-review/checks.json` and `.local/hero-reference-review/text-spacing-320.png`.

Build and lint passed. These checks do not prove live backend integration. Firefox and WebKit did not run.

## Artwork provenance and prompt

Historical asset: `public/hero-link-stickers.png`. Natural dimensions: 2172 by 724 pixels. File size at this checkpoint: 685548 bytes. The text edit below supersedes the initial prompt. Tool mode: built-in image generation with transparent output and the supplied copy reference. No fallback CLI ran. The component conversion below removed this public asset.

Prompt:

```text
Create a transparent-background production website illustration based only on the bottom long-URL-to-short-URL sticker illustration in this reference. Isolate and redraw that illustration, not the heading, tag, paragraph, or blue background. Landscape aspect ratio about 3:1, tightly composed but keep padding so all shadows and ink strokes fit. Left a large warm-white paper sticker with thick pure black outline and hard black offset shadow, tilted slightly counterclockwise. Its exact text across two lines: 'example.com/a/very/long/link' and '/that/keeps/going'. Right a smaller bright yellow (#FFD23F) sticker, thick black outline and hard black offset shadow, tilted slightly counterclockwise, exact bold text 'smol.link/idea'. A playful curved black hand-drawn arrow points from the long-link sticker to the yellow sticker. Three short ink rays above and below the yellow sticker. Flat crisp vector-like ink drawing, zero blur, no texture, no gradient, no extra words or objects. Output actual transparent alpha, no colored background.
```

## Implementation checklist

- Reference headline, description, and label: checked.
- Sticker illustration, yellow action, and rounded panel: checked.
- Loaded font, artwork, and console: checked.
- Responsive reflow and existing result behavior: checked.

## Follow-up polish

The hero now uses a pale blue ground and a decorative blue background shape. The full original grid takes precedence over the partial grid in the later reference.

## Current refinement evidence

The latest user instructions add the longer URL, blue decoration, and black border and shadow around Smol it. They also require the original full grid.

Source images: `.local/hero-reference-review/reference-box.png` (667 by 336 pixels) and `.local/hero-reference-review/reference-blue.png` (1676 by 939 pixels). Source density is unknown. The final desktop capture is `.local/hero-reference-review/refined-desktop.png`, at 1440 by 900 CSS pixels, density 1. The phone capture is `.local/hero-reference-review/refined-phone.png`, at 390 by 844 CSS pixels, density 1. Both show the idle form.

Combined comparison boards: `.local/hero-reference-review/refinement-comparison-0.png` and `.local/hero-reference-review/refinement-comparison-1.png`. The images fit each comparison column without distortion. This checks the requested treatments within the existing layout, not a full-page clone.

The heavy type and black box match the requested treatment. The pale blue ground and blue shape follow the second reference. The grid covers the full hero with its original 64px spacing and alignment. The blue artwork sits behind the form and ignores pointer input. The URL sticker contains `/that/keeps/going/on/and/on/and/on`. The source font and page density remain unspecified. The existing navbar and highlights strip retain their prior layout.

Six focused Chromium fixture checks passed on this source state. Build and lint passed. There are no remaining P0, P1, or P2 findings in this scope. The full grid differs from the partial grid in the second reference by direct user instruction.

Historical assets: `public/hero-link-stickers.png` (2172 by 724 pixels, 685548 bytes) and `public/hero-blue-backdrop.png` (1536 by 1024 pixels, 1121812 bytes). Both used transparent output from the built-in image tool. The component conversion below removed both public assets. Exact text-edit and blue-asset prompts: `.local/hero-reference-review/refinement-prompts.json`. The original sticker is retained in `.local/hero-reference-review/stickers-before-longer-text.png`. Grid and image checks are in `.local/hero-reference-review/refinement-checks.json`.

## React component conversion — October 8, 2026

The user requested real components and research into ready-made alternatives. The URL labels now remain selectable and editable in source. The full grid, headline box, pale blue surface, 40/60 split, and centered form remain in place. The newest result still appears below the input.

Current source: `src/components/HeroArtwork.tsx`. CSS styles real text as stickers. Inline SVG draws the arrow, ink rays, and blue shape. The research receipt is in [SOURCE_LEDGER.md](docs/SOURCE_LEDGER.md#hero-reference-research).

Before capture: `.local/hero-components/before.png`. Current captures: `.local/hero-components/after-1440.png`, `after-390.png`, and `after-320.png`. Browser checks in `.local/hero-components/checks.json` confirm selectable URL text, the original full grid, no raster hero requests, and no page errors. Six existing Chromium fixture checks passed, including responsive reflow and centered panel expansion. Firefox, WebKit, and live backend checks did not run for this change.

## Blue oval layering — October 8, 2026

The user requested the blue component above the grid and closer to the new reference. The SVG now uses a broad rotated ellipse with smaller ink rays near its upper-right edge. Its fill is opaque. The grid, blue backdrop, and hero content occupy separate layers in that order. The result still appears below the input and expands around the panel center.

The current-form reference is `codex-clipboard-11eb1158-2576-46a3-8bdb-a33e3286ad28.png`. The blue-shape reference is `codex-clipboard-81d4e903-8ee6-4232-b342-649e2a186506.png`. The supplied before/after ticket image did not change the requested blue adjustment.

Current viewport captures and layer checks are in `.local/hero-blue-layer/`. Checks cover 1440 by 900, 1366 by 768, and 390 by 844 viewports. The grid keeps its original spacing and alignment.

## Three-option comparison and selection — October 8, 2026

Three candidates were rendered at desktop and phone sizes: flat tickets, rounded stickers, and a spaced hybrid. The spaced hybrid was selected. It keeps the ticket edges and labels, with a curved arrow and gentle tilt. Its wider gap separates the arrow and scissors from the text. Matching ticket height and center alignment make the pair easier to compare. Desktop spacing moves the illustration left without clipping it. The long URL has no strike-through.

The current source keeps the larger, symmetric blue oval above the grid and centered behind the form. All artwork remains React, CSS, and SVG.

| Candidate           | Comparison result                                                                |
| ------------------- | -------------------------------------------------------------------------------- |
| A: Flat tickets     | Clear sequence, but rigid compared with the supplied sticker reference           |
| B: Rounded stickers | Clean silhouette, but removes the Before and After labels and cutting cue        |
| C: Spaced hybrid    | Selected: preserves both ideas with more room between the tickets and decoration |

Comparison boards: `.local/hero-three-options/comparison-1440.png` and `.local/hero-three-options/comparison-390.png`. Candidate screenshots, the capture script, and exact CSS/SVG alternatives remain in that directory. `variants.json` records the candidates and measured gaps. Final desktop capture: `.local/hero-three-options/final-1440.png`. Final phone captures: `final-390.png` and `final-320.png`. `final-checks.json` records seven viewport checks from 320 to 1440px.

The reload regression failed before the fix because the Questions fragment returned to that section. Eight focused Chromium fixture checks now pass. Four existing Chromium production checks also pass with injected API responses. These checks do not prove live backend integration. The final browser checks confirm text fit, matching ticket height and center alignment, no strike-through, centered oval geometry, desktop clearance, and no page overflow. Firefox and WebKit did not run for this change.

Ponytail, design-taste, UI/UX Pro Max, and Playwright guidance informed the bounded change. The Impeccable engine could not load because it is not installed. Its written layout guidance and the existing product/design owners informed the comparison instead. No engine or package installation ran.

Current final result: passed

## Labels inside tickets and expanding oval — October 8, 2026

The user approved the reference with labels inside the tickets and a straight arrow. The current layout follows that reference. Both desktop columns are wider and sit farther left. The panel still expands upward and downward, with the result below the input.

The blue oval grows with the panel. Ink marks stay at the panel corner, clear of the ticket text. The original grid keeps its spacing and alignment.

The new regression check failed before the oval fix. It passed after the fix. Chromium checks cover seven viewport sizes, from 320 to 1440 pixels, in idle and result states. They confirm text fit, equal ticket height, no page overflow, the original grid, oval clearance, and no desktop scrolling. These checks use fixture data. Firefox, WebKit, and live backend checks remain open.

Captures and geometry checks: `.local/hero-ticket-inside/`. Desktop result: `result-1366.png`. Phone layout: `idle-390.png`. The capture script waits for the input focus animation before clicking. This prevents an extra scroll from browser automation during that animation.

## Rounded sticker selection — October 8, 2026

The user selected the rounded sticker version after the ticket revision. The current source uses smooth corners, hard shadows, and a curved arrow. Both stickers have equal width and height. The pair moves 16px left on desktop. The expanding oval and original grid stay in place.

## Larger stickers and corner rays — October 8, 2026

Both rounded stickers are taller, with larger text and matching dimensions. The pair sits centered beneath the hero copy. A straight arrow has matching arrowhead sides and sits halfway between the stickers. Ink rays attach to the yellow sticker's top-right corner and follow its tilt. The sticker group stays above the blue oval.

Seven viewport checks cover idle and result states. All eight focused Chromium fixture checks pass. Build, lint, formatting, and document checks pass. Firefox, WebKit, and live backend checks remain open. Current captures stay in `.local/hero-ticket-inside/`. `sticker-detail.png` shows the final pair.

## Compact stickers with larger text — October 8, 2026

The current layout follows the user's latest reference, `codex-clipboard-9d17cbd9-7eda-478f-bf51-3db0db6b5ff1.png`. The white sticker is wider, and the yellow sticker is smaller. Larger text fits compact boxes. The curved arrow floats above the gap. The pair stays shifted left on desktop.

Nine viewport checks pass from 320 to 1920 pixels in idle and result states. They confirm text fit, no page overflow, the original grid, and no desktop scrolling. The focused Chromium shortener check, build, and lint pass. These checks use fixture data. Firefox, WebKit, and live backend checks remain open. The current captures stay in `.local/hero-ticket-inside/`. `sticker-detail.png` shows the final pair.

## Reference tickets and requested controls — October 8, 2026

The hero uses equal-height tickets with matching top and bottom edges. The white ticket is wider than the yellow ticket. Both use symmetric SVG outlines and hard shadows. Before and After labels share a baseline. The arrow and dashed cut line sit in the gap. The long URL has no strike-through. Text stays clear of the ticket notches.

The larger left section moves 16px left on desktop. The ticket group matches the headline width from the L to the question mark. Phones keep the group centered. Ink rays sit outside the yellow ticket's top-right corner. The original grid and the form/result layout stay intact.

The expiry control has one calendar trigger. Its popup contains the calendar, editable date and time, timezone hint, Clear, and Done. Calendar selection preserves the time. The field error stays beside the trigger. The calendar loads only when needed and shows a skeleton during the download.

Feature cards, step cards, and question rows lift 6px and grow their hard shadow by 6px on hover. The shortener panel stays still. Other boxes keep the existing 2px lift. Reduced motion and touch-only pointers disable the lift. Loading states use bordered skeletons and accessible status text.

Eight viewport checks passed from 320 to 1600 pixels. They cover headline alignment, calendar content bounds, time input, searchable choices, sidebar collapse, no horizontal overflow, axe, and browser errors. Nine additional viewport checks passed in idle and result states. They cover ticket text fit, the original grid, oval clearance, and no desktop scrolling.

The first calendar, contact, and dropdown checks failed before implementation. The hover check failed when the shortener still moved. The full Chromium fixture suite passed 29 checks before the final hover and deferred-calendar changes. Three focused checks passed afterward. They cover calendar time preservation, searchable dropdown keyboard use, stationary shortener hover, stronger card hover, reduced motion, and touch behavior.

Build and lint passed. Browser checks use fixture data. They do not prove live accounts, owner management, analytics, or email delivery. Firefox and WebKit remain open. Root graph output stays outside the frontend write scope. The exact next task below stays unchanged.

Captures: `.local/controls-review/` and `.local/hero-ticket-inside/`. New documentation prose scored 0.31 findings per 100 words.

### Final control receipt — October 9, 2026

Four final control checks passed in the India timezone. They cover calendar time preservation, contact drafts and mobile focus, searchable choices and sidebar collapse, and pending skeletons. Both tickets have equal height and vertical center in all 18 captured idle and result states. Five calendar license notices match the installed packages and final build byte for byte.

The final production rerun did not start. Automatic approval review failed because the workspace spend cap was reached. Four production Chromium checks passed before the final mobile contact focus change. They use injected API responses. The final source passed build, lint, and four fixture control checks. Browser screenshots remain in ignored local review folders.
