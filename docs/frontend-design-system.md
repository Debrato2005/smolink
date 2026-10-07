# Smolink frontend design system

**Status:** canonical visual and interaction specification  
**Effective date:** 2026-10-05  
**Implementation state:** planned. No frontend application or component library is installed.

This document defines Smolink's frontend visual language. It applies to Figma,
shared components, pages, charts, motion, and design review. The
[project README](../README.md) remains authoritative for product architecture,
API contracts, and implementation status. The [frontend engineering guide](../frontend/README.md)
owns browser, state, transport, privacy, and verification rules.

## Decision order

Use this order when requirements conflict:

1. Task completion, safety, and truthful system feedback.
2. Web Content Accessibility Guidelines (WCAG) 2.2 Level AA.
3. Content hierarchy, readable text, and familiar interaction.
4. Shared component behavior and the canonical tokens in this document.
5. The page intensity level.
6. Neobrutalist, Bauhaus, and Pop Art expression.

An aesthetic rule never justifies an unclear control, hidden state, broken
reading order, inaccessible contrast, or failed task.

## Design doctrine

Smolink uses **Neobrutalism × Bauhaus × Pop Art** as three separate layers:

- **Neobrutalism defines the component language.** It controls borders,
  corners, hard shadows, surfaces, controls, feedback, and visual weight.
- **Bauhaus defines the composition system.** It controls the grid, hierarchy,
  geometry, alignment, proportions, typography, and functional reduction.
- **Pop Art supplies controlled graphic accents.** It controls flat saturated
  color, halftone patterns, bold contours, reprographic texture, and poster-scale
  moments.

Usability, accessibility, content hierarchy, and task completion override all
three layers. Bauhaus does not mean random primary-color shapes. Pop Art does
not turn every panel into a comic frame. Neobrutalism does not make every
surface equally loud.

The visual system follows these principles:

- Show the structure. Use explicit edges, alignment, and states.
- Keep the primitive vocabulary small. Reuse tokens and shared components.
- Use asymmetry for page composition, not for form mechanics.
- Use one dominant expressive gesture in a composition.
- Keep operational text and dense data calm.
- Remove decoration that does not support hierarchy, grouping, direction, or
  brand recognition.

## Research basis

The rules below translate research into Smolink-specific constraints. They do
not copy an artwork or another brand's composition.

- [Sepideh Yazdi's neobrutalism guide](https://medium.com/@sepidy/how-can-i-design-in-the-neo-brutalism-style-d85c458042de)
  identifies flat color, black strokes, zero-blur offset shadows, large
  sans-serif type, and the noise risk in data-heavy software.
- [Neubrutalism.com](https://neubrutalism.com/) describes a repeatable grammar
  of square corners, thick borders, hard shadows, flat fills, limited accents,
  and an aligned micro-layout.
- [neobrutalism.dev](https://www.neobrutalism.dev/docs) supplies the preferred
  component source. Its current documentation lists 64 React and Tailwind v4
  components built through the shadcn workflow and Base UI. Its
  [migration guide](https://www.neobrutalism.dev/docs/migrating-to-base-ui)
  defines the current Base UI API. Its
  [changelog](https://www.neobrutalism.dev/docs/changelog) records the current
  light-only direction and September 2026 component changes.
- [MoMA's Herbert Bayer poster notes](https://www.moma.org/collection/works/5101)
  connect Bauhaus typography to a grid, asymmetric composition, sans-serif
  type, rational organization, and clarity.
- [MoMA's Bauhaus exhibition design account](https://www.moma.org/explore/inside_out/2009/11/06/bauhaus-the-graphic-design-department-goes-back-to-school/)
  warns against reducing Bauhaus to clichés. It also describes economy of
  materials and an important grid.
- [Bauhaus Dessau's account of the Bauhaus Building](https://bauhaus-dessau.de/en/venues/bauhaus-building/)
  shows functional parts with different proportions, visible structure, and
  color used for orientation.
- [MoMA's Roy Lichtenstein print notes](https://www.moma.org/collection/works/59856)
  identify regular dots and stripes, black outlines, flat primary colors, and
  simplified composition as commercial-print techniques.
- [Nielsen Norman Group's April 2025 guidance](https://www.nngroup.com/articles/neobrutalism/)
  requires clear controls, readable body type, whitespace, tested contrast,
  limited colors, hierarchy, and visible interaction feedback.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) supplies the accessibility baseline.

## Canonical tokens

These values are the source of truth for Figma variables and implementation.
Tailwind theme values or component variables must map to them. A registry
palette must not replace them.

```css
:root {
  /* Structural color */
  --ink: #000000;
  --paper: #fffdf5;
  --surface-muted: #e8e4da;
  --ink-muted: #514e47;

  /* Accent and semantic color */
  --accent-yellow: #ffd23f;
  --accent-red: #ff6b6b;
  --accent-blue: #74b9ff;
  --accent-green: #88d498;

  /* Border */
  --border-thin: 2px solid var(--ink);
  --border: 3px solid var(--ink);
  --border-thick: 4px solid var(--ink);

  /* Depth */
  --shadow-sm: 3px 3px 0 0 var(--ink);
  --shadow-md: 5px 5px 0 0 var(--ink);
  --shadow-lg: 8px 8px 0 0 var(--ink);

  /* Shape */
  --radius: 0;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 16px;
  --space-4: 24px;
  --space-5: 32px;
  --space-6: 48px;
  --space-7: 64px;
  --space-8: 96px;

  /* Type */
  --font-display: "Space Grotesk", Arial, sans-serif;
  --font-body: Inter, Arial, sans-serif;
  --font-mono: "Space Mono", "Courier New", monospace;
  --text-sm: 0.875rem;
  --text-body: 1rem;
  --text-lead: 1.125rem;
  --text-h3: 1.5rem;
  --text-h2: 2rem;
  --text-h1: clamp(2.5rem, 6vw, 4.5rem);
  --text-display: clamp(3rem, 9vw, 6rem);
  --line-body: 1.5;
  --line-heading: 1.05;

  /* Motion */
  --duration-press: 120ms;
  --duration-panel: 180ms;
  --ease-out: cubic-bezier(0.2, 0.8, 0.2, 1);
}
```

Do not add a token for one component until at least two real consumers need a
distinct value. Page-local raw colors, radii, shadow offsets, and border widths
are design-system defects.

## Color rules

Black and off-white form the primary structural palette. Accent colors identify
hierarchy, actions, or state. Use no more than two or three saturated accents
in one viewport or composition. Visible semantic states count toward this
limit. Remove decorative accents before hiding a necessary state color.

Use the semantic mapping below:

| Meaning | Fill | Required non-color cue |
|---|---|---|
| Primary emphasis | `--accent-yellow` or the page's selected accent | Label and position |
| Information | `--accent-blue` | Information icon or explicit label |
| Success | `--accent-green` | Check icon and success text |
| Warning | `--accent-yellow` | Warning icon and warning text |
| Error or destructive action | `--accent-red` | Error icon, message, and border treatment |
| Disabled or unavailable | `--surface-muted` | Disabled attribute and unavailable wording where needed |

Use black text on all canonical accent fills. Do not use white text on an
accent without a measured exception. The palette has these WCAG contrast
ratios, calculated from the hex values above:

| Combination | Ratio | Text use |
|---|---:|---|
| Ink on paper | 20.62:1 | Normal and large text |
| Ink on yellow | 14.54:1 | Normal and large text |
| Ink on red | 7.57:1 | Normal and large text |
| Ink on blue | 10.13:1 | Normal and large text |
| Ink on green | 11.92:1 | Normal and large text |
| Muted ink on paper | 8.15:1 | Secondary text |

Recheck contrast after opacity, overlays, blending, antialiasing, or a token
change. A passing token pair does not prove the rendered result.

### No gradients

Gradients are prohibited. This includes background, text, border, mask, chart,
aurora, mesh, conic, and shader gradients. A product requirement that truly
needs a gradient requires an explicit design-system change. Do not treat it as
a page-level exception.

## Typography

- Use Space Grotesk at weight 700 or 800 for major headings and display text.
- Use Inter at weight 400 to 600 for body and interface text.
- Use Space Mono only for short codes, identifiers, technical values, or code.
- Use no novelty font for body text or controls.
- Use no additional family without a documented language, brand, or technical
  need.
- Confirm each font's license, loading plan, fallback metrics, and layout effect
  before implementation.
- Create hierarchy through scale, weight, spacing, position, and contrast.
- Keep body copy calm. Do not set all text in capitals, heavy weight, or display
  scale.
- Keep paragraph line length near 45 to 75 characters when layout permits.
- Do not justify body text.

Oversized or cropped text is a high-intensity graphic device. It must not remove
meaning, break the accessible name, or replace semantic text with an image.

## Grid and layout

Use an 8 px-derived spacing rhythm. The 4 px token supports small optical
adjustments inside components. It does not define page spacing.

| Viewport class | Columns | Gutter | Outer margin |
|---|---:|---:|---:|
| Mobile | 4 | 16 px | 16 px minimum |
| Tablet | 8 | 24 px | 24 px minimum |
| Desktop | 12 | 24 px | 32 px minimum |

Limit normal page content to 1280 px. A full-bleed color or poster section can
extend beyond that container, but its readable content must return to the grid.
Choose actual breakpoints from content pressure. Do not treat the three classes
as fixed device brands.

Use strong axes, asymmetric section composition, negative space, scale
contrast, geometric blocks, and systematic repetition. Apply this rule:

> Macro layout can be asymmetric. Micro layout must remain mechanically aligned.

Labels, fields, help text, errors, table columns, filters, pagination, and
dashboard controls must align. Visual imbalance is acceptable only when the
reading direction and task order remain clear.

Use circles, rectangles, squares, and triangles only for hierarchy, grouping,
branding, or directional flow. Do not scatter them as a Bauhaus costume.

### Responsive composition

On small screens:

- Preserve semantic and task order in the document object model (DOM).
- Collapse 12 or 8 columns to the 4-column grid.
- Reduce `--shadow-lg` to `--shadow-md` when the offset causes crowding.
- Keep the 3 px default structural border.
- Remove decorative overlaps before reducing text or control space.
- Convert dense rows to an accessible table scroller or a proven card pattern.
- Prevent decorative graphics and long URLs from causing page overflow.
- Keep controls familiar and at least 44 CSS pixels high where practical.
- Simplify asymmetry before sacrificing reading order or target size.

The required WCAG 2.2 reflow check includes 320 CSS px width. A desktop poster
that is merely scaled down does not pass responsive review.

## Component grammar

### Structure

- Use `--border` for normal buttons, inputs, cards, dialogs, menus, and panels.
- Use `--border-thin` only for internal dividers, table rules, and compact
  secondary structure.
- Use `--border-thick` for selected, error, destructive, or major display
  emphasis. Do not use it as the default.
- Use square corners. The canonical radius is 0.
- Use flat opaque fills.
- Use only the three hard shadows. Shadow blur is always 0.
- Use one predictable depth direction: positive x and positive y.
- Reserve `--shadow-lg` for high-intensity heroes and overlays.
- Do not place an equally strong shadow on every item in a dense view.

### Control motion

Buttons and button-like controls share this behavior:

| State | Treatment |
|---|---|
| Default | `--border`, flat fill, and `--shadow-md` |
| Hover | Translate `-2px, -2px`. Change `--shadow-md` to `--shadow-lg`. Keep the label stable |
| Focus-visible | Add a 3 px ink outline with a 3 px offset. Use paper on an ink surround |
| Active | Translate `3px, 3px`. Remove the hard shadow |
| Disabled | No transform. No shadow. Muted fill. Native disabled semantics |

Use `--duration-press` and `--ease-out`. Apply the same physical model to
toggles, menu triggers, and compact actions when it improves affordance. Do not
move form labels, table cells, or error text.

Focus is separate from the component border and shadow. Do not remove a native
focus indicator until the replacement is visible on every adjacent fill.

### State system

Each shared component must define all states that apply to it:

| State | Required treatment |
|---|---|
| Default | Clear label, boundary, role, and hierarchy |
| Hover | Visual feedback that does not carry unique information |
| Focus-visible | Offset focus indicator that survives the thick border |
| Active | Physical press or explicit selected feedback |
| Disabled | Native semantics, muted treatment, no action, no misleading hover |
| Loading | Persistent task label, progress cue, duplicate-action prevention, live status when needed |
| Success | Text plus check or equivalent icon, with green as support |
| Warning | Text plus warning icon, with yellow as support |
| Error | Explicit message plus icon and structural emphasis, with red as support |
| Empty | Confirmed-empty explanation and a valid next action when one exists |
| Selected | Programmatic selected state plus border, mark, icon, or text change |

Loading text must name the task, such as `Shortening…`, not only `Loading…`.
The submitted URL stays visible while the request is pending. A failed request
never becomes an empty state. Nothing fails silently.

## Component source policy

Use one shared component layer. Do not copy a second visual version into a
page.

### Priority 1: neobrutalism.dev

Use a suitable [neobrutalism.dev](https://www.neobrutalism.dev/docs) component
through its shadcn registry workflow. Map its variables and variants to the
Smolink tokens. Do not accept a registry palette as a second theme.

The current site was checked on 2026-10-05. It uses React, Tailwind v4, the
shadcn workflow, and Base UI. Current components use `@base-ui/react`, the
`render` prop, and Base UI state attributes such as `data-open` and
`data-checked`. Do not write new Radix-specific instructions from older docs.

The current registry includes these Smolink-relevant components:

`Accordion`, `Alert`, `Alert Dialog`, `Button`, `Button Group`, `Card`, `Chart`,
`Checkbox`, `Combobox`, `Data Table`, `Dialog`, `Dropdown Menu`, `Empty`,
`Field`, `Form`, `Input`, `Input Group`, `Label`, `Native Select`, `Pagination`,
`Popover`, `Progress`, `Radio Group`, `Select`, `Skeleton`, `Spinner`, `Switch`,
`Table`, `Tabs`, `Textarea`, `Toast`, `Toggle`, and `Tooltip`.

The complete catalog changes over time. Check the current site before each
component adoption. Record the source URL and adoption date. Install only the
components that a current page consumes.

### Priority 2: shadcn-compatible Base UI primitive

If neobrutalism.dev lacks the required primitive, use an accessible Base UI or
shadcn-compatible primitive. Apply the canonical tokens and Smolink states. It
must not retain generic shadcn colors, radii, shadows, or spacing.

### Priority 3: custom shared primitive

Create a custom primitive only when all these conditions are true:

- No suitable current registry or Base UI primitive exists.
- Smolink needs a distinct interaction, not a distinct decoration.
- Composition from existing primitives would reduce clarity or accessibility.
- The team can define semantics, keyboard behavior, focus, states, and tests.

Put the result in the common component layer. Do not create page-local forks.

### Subordinate sources

- **React Bits:** optional. Use it only for a specific interaction that improves
  comprehension or presentation and can adopt all Smolink tokens and states.
  It is not a source of visual language.
- **Native HTML:** preferred when it supplies the complete behavior. Do not
  replace a dependable native control only to make it look unusual.
- **Icons:** use one icon system. Icons support labels and must not become the
  sole state cue.

## Smolink component rules

### Navigation and footer

- Use a paper or single-accent surface with an ink divider.
- Keep the main action obvious and keyboard reachable.
- Use the same link and button treatment on every page.
- Collapse navigation without changing its order or hiding authentication state.
- Keep the footer lower in intensity than the page hero.

### URL creation module

- Treat the long-URL field, optional alias, expiry control, and Shorten button
  as one aligned module.
- Keep labels visible. A placeholder does not replace a label.
- Keep the long-URL field conventional and full width at small sizes.
- Mark alias and expiry as optional in text.
- Explain expiry units and timezone near the control.
- Use one primary accent on the Shorten button.
- Keep validation next to its field and preserve entered values after failure.
- Show `409`, `422`, `429`, and `503` outcomes with explicit text.

### Generated-link result

- Use a shared result panel with a thick top rule or selected treatment.
- Show the returned short URL as text and a real link.
- Put Copy and QR actions in one aligned group.
- Confirm Copy only after the clipboard operation succeeds.
- Supply a manual-copy fallback.
- Do not imply that redirect or QR works until the related endpoint exists.

### Authentication

- Use medium intensity and a predictable one-column form.
- Keep password, recovery, verification, and account-lock messages calm.
- Make the Google action visually secondary until the backend flow exists.
- Never use decoration to hide token, browser-binding, or session errors.

### Dashboard, listing, and settings

- Use controlled intensity and dense, mechanically aligned layout.
- Keep search, filters, sort, pagination, and row actions in stable locations.
- Use 2 px internal table rules and a 3 px outer boundary.
- Use hard shadows only on the main panel or primary action, not every row.
- Provide text or icon support for status colors.
- Use a confirmation dialog for destructive deletion.
- Keep the destructive action red, explicit, and separate from safe actions.

### Analytics and charts

- Use flat fills and the canonical palette. Gradients are prohibited.
- Use ink axes, labels, and structural lines where they improve reading.
- Distinguish series with labels, shapes, line styles, or patterns in addition
  to color.
- Supply a text summary or accessible data table for chart meaning.
- Keep date controls conventional and keyboard operable.
- Do not add decorative halftones behind plotted data.

### Dialogs, menus, toasts, and tooltips

- Use the current Base UI behavior when the registry component supplies it.
- Preserve focus trap, dismissal, focus restoration, and accessible naming.
- Use `--shadow-lg` only for the active overlay.
- Toasts supplement an in-context result. They do not carry the only error or
  success message.
- Tooltips supply secondary help. They do not hold required instructions.

### Empty, loading, and error states

- Empty states use one simple geometric or original SVG motif at most.
- Skeletons copy final layout geometry and stop under reduced motion.
- Spinners include a visible task label or accessible status text.
- Errors state what failed and the valid recovery action.
- Preserve entered data unless security or correctness requires removal.

## Page intensity

Use the lowest level that still communicates Smolink's identity.

| Level | Pages | Required treatment | Limits |
|---|---|---|---|
| High | Landing and marketing | Strong asymmetry, display type, color blocks, poster sections, large shadows, one Pop Art gesture | Core navigation and creation task stay predictable |
| Medium | Authentication and URL creation | Clear identity, one expressive panel, medium shadows, limited accents | Forms stay one clear sequence with stable labels and errors |
| Controlled | Dashboard, analytics, settings | Square geometry, ink borders, flat palette, consistent type, explicit states | Minimal decoration, small shadows, no irregular data alignment |

Do not use high intensity as a default. A dashboard must still look like
Smolink, but it must not behave like a poster.

## Pop Art accent system

Allowed motifs include:

- Ben-Day or halftone dots.
- Regular stripes.
- Bold black contours.
- Flat primary-color panels.
- Poster-scale typography.
- Screen-print or registration-offset layers.
- Cropped labels and simple geometric illustration.

Prefer original CSS or SVG procedures. Use one dominant Pop Art gesture per
viewport or section. Keep patterns out of body-copy backgrounds, form fields,
tables, plotted data, and focus areas. Do not reproduce, trace, or closely
imitate copyrighted artworks. Commercial-print techniques are a source of
method, not permission to copy an artwork.

## Motion policy

Motion must explain interaction, hierarchy, continuity, or state change. It
must remain optional when it is not essential.

- Use CSS for button states, simple reveals, accordions, and control feedback.
- Use `--duration-press` for control motion and `--duration-panel` for small
  panels.
- Avoid continuous decorative motion.
- Do not animate layout properties when transform or opacity can express the
  same result without hiding content.
- Keep forms, tables, errors, and status text stable.
- Stop hidden or offscreen work.
- The reduced-motion version must show settled content and preserve every task.

### GSAP and Lenis

GSAP remains conditionally approved for coordinated landing-page transitions,
editorial reveals, scroll-linked poster composition, and major sequences that
CSS cannot express clearly. Do not use it for standard control states.

Lenis remains conditionally approved for a proven high-intensity scroll story.
Reject it if it harms keyboard scrolling, touch behavior, performance, browser
history restoration, anchor links, or reduced-motion behavior. Native scrolling
is the default.

If GSAP or Lenis is adopted, define one timing and scroll owner. Test reverse
scroll, restored positions, resize, arbitrary jumps, and cleanup. Do not copy
timing constants from another project.

## Accessibility requirements

Target WCAG 2.2 Level AA. This target does not create a conformance claim.

- Normal text must have at least 4.5:1 contrast.
- Large text must have at least 3:1 contrast.
- Required control boundaries, states, and meaningful graphics must have at
  least 3:1 contrast against adjacent colors.
- Color must never be the only state or information cue.
- All functionality must work with a keyboard.
- Focus must be visible and not fully obscured.
- Pointer targets must meet the 24 by 24 CSS px AA minimum. Prefer 44 by 44 CSS
  px for standalone controls.
- Use semantic HTML and the correct heading hierarchy.
- Every form control needs a programmatic and visible label.
- Validation must identify the field and describe the error in text.
- Dialogs, menus, popovers, and tooltips need correct roles and focus behavior.
- Important async state changes need an appropriate live announcement.
- Content must reflow without lost information or function at 320 CSS px.
- Do not flash content more than three times in one second.
- Respect `prefers-reduced-motion` for all nonessential motion.

Test with keyboard navigation, zoom, text spacing overrides, reduced motion,
touch, long URLs, long errors, and screen-reader navigation. Automated scans
support review but do not prove conformance.

## Forbidden patterns

Do not use these patterns unless a documented functional requirement changes
this specification:

- Any gradient, including chart and shader gradients.
- Aurora or mesh effects.
- Glassmorphism, frosted glass, or blurred translucent cards.
- Material-style soft elevation or Gaussian shadow blur.
- Arbitrary rounded cards or 12–24 px default radii.
- Pill-shaped controls as a general style.
- Generic blue-purple startup palettes.
- Glossy surfaces, excessive glow, or fake 3D SaaS illustration.
- Neumorphism.
- Ambient floating blobs.
- Decorative noise without hierarchy.
- Random rotation or unstructured geometric scattering.
- A different treatment for the same component on another page.
- Generic shadcn styling that bypasses Smolink tokens.
- Page-local copies of shared component styling.
- Decorative JavaScript when CSS is sufficient.

### Paper Shaders

Paper Shaders is deferred and is not a default dependency or visual direction.
Do not add it for atmospheric gradients, shader decoration, or ambient blobs.
A future proposal can use it only for a rare flat, poster-like effect that
obeys the no-gradient rule, has a static fallback, and passes performance and
accessibility review. That proposal requires its own approval.

## Dark mode

Dark mode is deferred. Smolink has no current product requirement for it, and
the current neobrutalism.dev implementation is light-only. Do not add
`useTheme`, `next-themes`, a theme context, or an untested inverted palette.

A future dark-mode requirement needs a separate, contrast-tested palette and
component-state review. It must not mechanically invert the light tokens.

## Figma contract

Figma remains the design-definition tool. Before frontend implementation, the
Figma library must contain:

- Color variables and the tested combinations.
- Typography styles for Space Grotesk, Inter, and Space Mono.
- The spacing scale, grid, borders, shadows, and radius.
- Default, hover, focus-visible, active, disabled, loading, success, warning,
  error, empty, and selected states.
- Button, input, field, card, dialog, toast, navigation, and footer.
- The URL creation module and generated-link result.
- An authentication form.
- A dashboard table or row pattern and analytics shell.
- Mobile, tablet, and desktop grid examples.

Figma names and coded token names must map one to one. A design change is not
complete until both systems agree. Figma does not override accessible behavior
or the current API contract.

## Correct and incorrect examples

### Correct shared control

```css
.smolink-button {
  border: var(--border);
  border-radius: var(--radius);
  background: var(--accent-yellow);
  color: var(--ink);
  box-shadow: var(--shadow-md);
  min-height: 44px;
  transition:
    transform var(--duration-press) var(--ease-out),
    box-shadow var(--duration-press) var(--ease-out);
}

.smolink-button:hover {
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow-lg);
}

.smolink-button:focus-visible {
  outline: 3px solid var(--ink);
  outline-offset: 3px;
}

.smolink-button:active {
  transform: translate(3px, 3px);
  box-shadow: none;
}
```

This example uses canonical structure, a tested text/fill pair, a real target,
shared motion, and a separate focus indicator.

### Incorrect generic SaaS control

```css
.button {
  border: 0;
  border-radius: 16px;
  background: linear-gradient(135deg, #6d5dfc, #9b8cff);
  color: white;
  box-shadow: 0 12px 32px rgb(60 50 120 / 25%);
}
```

This violates the border, radius, flat-color, palette, shadow, and contrast
review rules.

### Correct dashboard composition

- One paper data panel with a 3 px outer border.
- A 2 px table rule system.
- One blue filter accent and one yellow primary action.
- Text, icon, and border changes for selected or error states.
- No shadow on each row.

### Incorrect dashboard composition

- A different saturated fill and large shadow on every row.
- Misaligned labels and values to create visual tension.
- A halftone pattern behind chart labels.
- Color-only status dots.
- Rounded generic shadcn controls mixed with square custom controls.

## Design review checklist

- [ ] The change uses an existing shared primitive when one fits.
- [ ] The current neobrutalism.dev catalog was checked first.
- [ ] Registry or Base UI components map to Smolink tokens and states.
- [ ] Borders use 2 px, 3 px, or 4 px tokens for their defined purpose.
- [ ] Corners use 0 radius.
- [ ] Every shadow is a canonical hard, zero-blur shadow.
- [ ] No gradient, glass, glow, ambient blob, or soft elevation exists.
- [ ] The composition uses no more than two or three visible saturated accents.
- [ ] The layout follows the rational grid and clear reading order.
- [ ] Macro asymmetry does not disturb micro alignment.
- [ ] Pop Art decoration stays subordinate to content.
- [ ] Body text remains calm and readable.
- [ ] Every state uses more than color alone.
- [ ] Focus is visible outside the structural border.
- [ ] Keyboard, pointer, touch, and screen-reader behavior is defined.
- [ ] Reduced motion keeps all content and tasks available.
- [ ] Mobile preserves task order, target size, and readable content.
- [ ] Dashboard and table density remains useful.
- [ ] Charts use flat colors and redundant series identification.
- [ ] The component looks like Smolink, not generic shadcn.
- [ ] No page-local styling duplicates a shared primitive.
- [ ] Figma and code use the same token names and values.

A hard-rule violation is a documented architecture inconsistency. Fix it or
record an approved design-system change. Do not accept silent exceptions.

## Decisions still outside this specification

The visual system is complete enough for design and component work. These
product or platform decisions remain separate:

- Token storage, refresh coordination, and Google browser binding.
- Same-origin deployment or an explicit cross-origin policy.
- Lossless browser handling for Snowflake integer IDs.
- The supported browser matrix and formal accessibility test matrix.
- A product requirement and separate palette for dark mode.
- A measured use case for GSAP, Lenis, React Bits, or Paper Shaders.

Do not invent these contracts during visual implementation.
