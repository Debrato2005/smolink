# Smolink design system

**Owner:** Frontend visual and interaction system

## Doctrine and authority

Neobrutalism defines primitive grammar. Bauhaus defines composition. Pop Art supplies controlled accents. Usability, accessibility, content hierarchy, and task completion override all three.

This is the sole frontend owner for visual decisions. It applies root `docs/frontend-design-system.md` without changing that file. The root file pins the palette and font families. The `--sky-surface` page ground and `--hero-surface` hero ground came from direct user requests and need separately authorized root reconciliation (CB-09). [PRODUCT.md](../PRODUCT.md) records product truth.

The system follows three user-selected references: the [neobrutalism.dev](https://www.neobrutalism.dev/) light grid and boxed controls, the [neubrutalism.com](https://neubrutalism.com/) navbar, strip, and color-filled cards, and the [Medium guide](https://medium.com/@sepidy/how-can-i-design-in-the-neo-brutalism-style-d85c458042de) rules for pitch-black strokes and opaque shadows. The shortener card is the hero action. A successful result is a **ticket** that states how many characters were cut.

Product copy never says demo, sample, or synthetic. Production marks backend-missing features as **coming soon**. Local development data looks like the real product. Only the development-only Developer tools panel names it.

## Tokens and typography

[src/styles/tokens.css](../src/styles/tokens.css) is the executable source for exact values. Reference token names. Do not copy values into prose or components.

| Group     | Contract                                                                                              |
| --------- | ----------------------------------------------------------------------------------------------------- |
| Structure | Ink `#000000`, paper `#fffdf5`, muted surface and muted text                                          |
| Ground    | `--sky-surface` under the `--grid-paper` SVG tile at `--grid-size` (64px). Surfaces stay opaque paper |
| Accents   | Yellow, red (coral), blue, green. Black text on every accent                                          |
| Borders   | 2px internal rules. 3px controls and panels. 4px header edge and error emphasis                       |
| Shadows   | 3, 4, 5, or 8px positive offsets. Zero blur. Colored offsets only on ink surfaces                     |
| Shape     | Radius 0 by default. The hero permits the supplied rounded label and form treatment                   |
| Spacing   | 4px optical step, then 8, 16, 24, 32, 48, 64, and 96px                                                |
| Type      | Space Grotesk 700 headings. Inter 900 hero, 400/600 interface. Space Mono URLs and codes              |
| Motion    | 120ms press and input lift, 180ms navigation lift. One print reveal for the result ticket             |

Color roles are fixed. Yellow marks primary emphasis, the hero headline highlight, the highlights strip, and the current or hovered navigation item. Ink is the inverse action surface for the header Sign up and My links buttons. The hero Shorten button uses yellow. Feature cards use solid yellow, coral, blue, and green fills with black text. Green also marks a confirmed result and active status. Red marks errors and destructive actions. Blue marks information notices and chart series.

## Layout and intensity

Content is bounded to 1280px. Breakpoints respond to content pressure: 1150px swaps desktop navigation for the menu button, 1050px makes feature cards two columns, 900px tightens the header, 760px moves social links into the menu, 720px collapses cards, steps, forms, and tables to one column, 560px stacks the joined URL control, and 400px compacts the header.

The navbar spans the viewport with 24px horizontal padding, or 16px at widths of 900px or less. Desktop symbol and wordmark widths are 60px and 160px. Smaller widths preserve the horizontal layout on narrow screens. The browser tab uses a transparent 64px PNG from the same symbol crop.

The navbar has boxed GitHub and X links. The GitHub badge reads the repository star count from Shields.io. Shields caches the count. If the image fails, the link shows Star and the GitHub icon. Both links open a new tab. On phones, the navigation menu contains these links.

| Intensity  | Use                     | Treatment                                                                                                                          |
| ---------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| HIGH       | Public home             | Display headline with a yellow highlight, shortener card, yellow strip, color cards, step cards, boxed questions, ink closing band |
| MEDIUM     | Account pages           | Ink poster with offset link stubs. Boxed form card with Continue with Google above an email form                                   |
| CONTROLLED | Workspace and analytics | Ink side rail, three-column summary strip, flat table rows. Flat rows. Boxed panels lift slightly on hover                         |

The URL field and Shorten button must sit in the first viewport at 390 × 844. Long URLs never cause page overflow. The result ticket scales its URL text with `cqi` units. Shared inputs use `min-width: 0` so intrinsic control widths cannot widen a page.

The home hero uses a 40/60 split on desktop. The headline and description sit on the left. The form and newest result share the right panel. The hero and yellow highlights strip fill the first viewport when their content fits. The panel stays vertically centered as the result appears below the form. Taller content can extend the page. At widths of 900px or less, the columns stack in normal document flow.

The hero copy starts with a paper label and the headline Long links? Smol it. The headline uses the installed Inter 900 font through a separate family alias. This keeps other Inter weights unchanged. The second line uses a flat yellow highlight with an ink border and hard shadow.

The hero shows the example links as real text in a React component. CSS supplies the sticker borders, yellow fill, rotation, and hard shadows. Inline SVG supplies the curved arrow, ink rays, and blue backdrop. Decorative SVG stays outside the accessibility tree and ignores pointer input. On phones, the copy remains centered and the stickers scale with their container.

The user-selected hero reference permits a rounded label, 12px panel corners, and 6px input and button corners in this section. The rest of the interface keeps square corners. The hero Shorten button uses yellow with black text and a hard shadow.

The hero uses a pale blue surface with the original grid across the full section. A static blue SVG sits behind the form and ignores pointer input. On phones, the backdrop moves behind the stacked form. The grid keeps its original size and alignment. The headline highlight has a black border and hard shadow. The long-link sticker ends with /that/keeps/going/on/and/on/and/on.

The result URL receives focus and selects its text. Focus keeps the scroll position when the URL is visible. If the URL is outside the viewport or behind the header, the browser brings it into view.

## Component sources and grammar

Check current neobrutalism.dev first. Map every adopted style to Smolink tokens. The button keeps the Base UI primitive with plain CSS. Style real anchors directly when navigation needs button styling. Never render links through the Button primitive.

| Component        | Grammar                                                                                                                                                     |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Header           | Sticky paper bar, 4px ink edge. Cropped symbol and original Smolink wordmark sit side by side without a frame. Navigation and utility buttons sit at right. |
| Navigation item  | Plain text at rest with a transparent 3px border. See the state table                                                                                       |
| Shortener card   | Paper panel, 3px border, large shadow. Joined URL field and ink Shorten button. Heading kept for screen readers                                             |
| Highlights strip | Static yellow band with spark icons. Only true, live capabilities                                                                                           |
| Feature card     | Solid accent fill, 3px border, medium shadow, boxed icon. Coming soon badge in production when the backend is missing                                       |
| Step card        | Paper card with a numbered yellow circle. Numbers mark a real sequence                                                                                      |
| Ticket           | Stub and body split by a dashed rule with two notches. Green stub for results, blue stub for link details                                                   |
| Field            | Visible label, 3px border, adjacent error with an alert icon, then help text. Focus lifts with a 4px hard shadow                                            |
| Google button    | Full-width paper button with Google's multicolor G, above an or-divider                                                                                     |
| Workspace table  | 3px outer border, 2px rules, fixed column widths, flat row actions. Rows become stacked cards at 720px                                                      |
| Analytics chart  | Heading wraps inside the panel. Count and date labels wrap inside each column without clipping. Exact values stay in the daily table                        |
| Dialog           | Base UI dialog, large shadow, layered above the sticky header                                                                                               |

| State         | Required treatment                                                                            |
| ------------- | --------------------------------------------------------------------------------------------- |
| Default       | Border and hard shadow on controls. Navigation items have no box at rest                      |
| Hover         | Lift `translate(-2px, -2px)` and grow the shadow by 2px. Navigation items gain the yellow box |
| Focus-visible | Ink outline with offset. Inputs and navigation items use their lifted shadow state instead    |
| Current route | Navigation items keep the hover box (`aria-current="page"`). The header Sign in fills yellow  |
| Active        | Move into the shadow and remove it                                                            |
| Disabled      | Native disabled semantics, muted fill, no motion or shadow                                    |
| Loading       | Task-specific text, duplicate-submit prevention, stable geometry                              |
| Error         | Adjacent text, associated field, structural emphasis. Red is supplementary                    |
| Selected      | Programmatic state plus explicit text, border, or fill                                        |

Decorative shapes are limited to the brand mark, the strip's spark icons, the auth poster stubs, and the supplied hero illustrations. Do not add scattered stars or blobs.

## Motion and accessibility

CSS owns all motion. Navigation items move their transform and shadow over 180ms and their fill and border over 120ms. Buttons and inputs use the 120ms press and lift. The result ticket prints with one clip-path reveal. The highlights strip is static because continuous animation is prohibited. Avoid transitions of layout properties.

Boxed blocks lift by 2px and grow their hard shadow by 2px on hover. This applies to the bench, tickets, feature and step cards, FAQ boxes, account cards, notices, and workspace panels. The motion uses `--duration-panel` and requires a hover-capable pointer. It does not change layout or add click behavior to informational cards.

Reduced motion removes every transition, animation, and lift. Boxes and shadows stay visible, so state never depends on motion.

Target WCAG 2.2 AA. This is not a conformance claim. Require semantic landmarks, logical headings, visible labels, accessible names, associated field errors, keyboard operation, and safe live feedback. Stacked elements use `isolation: isolate` so decorative layers cannot paint above dialogs. Test zoom, WCAG text spacing, 320px reflow, keyboard, and reduced motion. Analytics labels must retain complete text under extra spacing. Do not hide overflow to pass a page-width check. Axe supports review but cannot certify conformance.

## Forbidden patterns and deferred decisions

Gradients are prohibited, including backgrounds, text, borders, masks, charts, and shaders. The page grid is an SVG tile for this reason. Also prohibit glassmorphism, blur, glow, soft elevation, rounded cards outside the hero, pervasive pills, unrequested floating blobs, random rotation, and hero-metric cards. Continuous marquee motion is prohibited.

Dark mode is `DEFERRED`. Paper Shaders is `EVALUATED_DEFERRED`. React Bits remains `REFERENCE_ONLY`. Figma synchronization is planned external work.
