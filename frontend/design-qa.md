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

Saved asset: `public/hero-link-stickers.png`. Natural dimensions: 2172 by 724 pixels. Current file size: 685548 bytes. The text edit below supersedes the initial prompt. Tool mode: built-in image generation with transparent output and the supplied copy reference. No fallback CLI ran.

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

Saved assets: `public/hero-link-stickers.png` (2172 by 724 pixels, 685548 bytes) and `public/hero-blue-backdrop.png` (1536 by 1024 pixels, 1121812 bytes). Both use transparent output from the built-in image tool. Exact text-edit and blue-asset prompts: `.local/hero-reference-review/refinement-prompts.json`. The original sticker is retained in `.local/hero-reference-review/stickers-before-longer-text.png`. Grid and image checks are in `.local/hero-reference-review/refinement-checks.json`.

Current final result: passed
