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

The hero uses equal-height tickets with matching top and bottom edges. The white ticket takes 46% of the group width. The yellow ticket takes 40%. Labels sit above each ticket's center. The vertical cut line sits at the group's center, with upright scissors between equal dashed sections. The arrow points toward the yellow ticket. Text has no strike-through and stays clear of the notches.

The left section moves 16px left on desktop. The ticket group matches the headline width. The ticket group moves up to 20px left on desktop, independently of the headline's left edge. Narrow desktop widths use a smaller offset to keep the border visible. The long URL uses three balanced lines with larger text. Rounded stroke joins and a smaller hard shadow keep the notches clear. The yellow highlight aligns with the headline's left edge on desktop. Supporting text stays centered. Phones keep the highlight and ticket group centered. Ink rays sit outside the yellow ticket's top-right corner.

Decorative SVG stays outside the accessibility tree and ignores pointer input. On phones, the stickers scale with their container. The desktop columns use more width and less space on the left.

The user-selected references permit small rounded corners on the hero, shared controls, popup panels, skeletons, and sidebar avatar. Large landing cards remain square. The hero Shorten button uses yellow with black text and a hard shadow.

The hero uses a pale blue surface with the original grid across the full section. The blue oval stays centered behind the form. It grows with the panel when the result appears below the input. Its diagonal follows opposite panel corners. It stays above the grid and below the form. Ink marks stay at the panel corner, clear of the ticket text. The grid keeps its original spacing and alignment. On phones, the backdrop stays behind the stacked form. The headline highlight has a black border and hard shadow. The long-link sticker ends with /that/keeps/going/on/and/on/and/on.

The result URL receives focus and selects its text. Focus keeps the scroll position when the URL is visible. If the URL is outside the viewport or behind the header, the browser brings it into view.

Home reload starts at the top of the hero. Normal section links and initial deep links still scroll to their targets.

The QR skeleton uses three muted corner markers and soft blocks inside the fixed square frame. A gentle pulse shows progress. Reduced motion keeps it still. The download control stays disabled during generation.

The frame keeps the same size when the image appears. The short URL and disabled download control reserve their final space during loading. Download becomes available after generation.

## Footer

The footer uses one compact row on desktop. A smaller original logo sits beside the GitHub creator credit and copyright. Contact, OnlyChai, and Ko-fi are the only actions. The headline, description, navigation columns, repository button, and large creator card were removed because they repeated existing content. Phones stack the brand and actions, with equal columns for the support buttons. The fixture-only Developer tools remain available.

The OnlyChai button opens the supplied support URL in a new tab. Ko-fi remains disabled until the user supplies a profile URL.

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

## Requested controls

The expiry control has one calendar trigger. Its popup contains the calendar, editable date and time, timezone hint, Clear, and Done. Calendar selection preserves the time. The field error stays beside the trigger. The calendar loads only when needed and shows a skeleton during the download.

The workspace uses a paper sidebar with grouped navigation, a yellow current-page marker, and a collapse control. Collapsed desktop navigation keeps accessible link names. Mobile collapse hides the workspace navigation until expansion. Status and analytics ranges use Base UI Select. Sort uses a searchable Base UI Combobox. Query parameters still own filter state.

Contact me opens a dialog with Name, Email, and Message fields. Open email draft prepares a mailto link to debrato2005@gmail.com. The visitor sends the message from their email app. The interface never claims delivery. Contact values stay in memory.

## Motion and accessibility

CSS owns all motion. Navigation items move their transform and shadow over 180ms and their fill and border over 120ms. Buttons and inputs use the 120ms press and lift. The result ticket prints with one clip-path reveal. The highlights strip is static because continuous animation is prohibited. Avoid transitions of layout properties.

Feature cards, step cards, and question rows lift 6px and grow their hard shadow by 6px on hover. The shortener panel stays still. Other boxes keep the existing 2px lift. Reduced motion and touch-only pointers disable the lift. Loading states use bordered skeletons and accessible status text.

Reduced motion removes every transition, animation, and lift. Boxes and shadows stay visible, so state never depends on motion.

Target WCAG 2.2 AA. This is not a conformance claim. Require semantic landmarks, logical headings, visible labels, accessible names, associated field errors, keyboard operation, and safe live feedback. Stacked elements use `isolation: isolate` so decorative layers cannot paint above dialogs. Test zoom, WCAG text spacing, 320px reflow, keyboard, and reduced motion. Analytics labels must retain complete text under extra spacing. Do not hide overflow to pass a page-width check. Axe supports review but cannot certify conformance.

## Forbidden patterns and deferred decisions

Gradients are prohibited, including backgrounds, text, borders, masks, charts, and shaders. The page grid is an SVG tile for this reason. Also prohibit glassmorphism, blur, glow, soft elevation, unrequested rounded landing cards, pervasive pills, unrequested floating blobs, random rotation, and hero-metric cards. Continuous marquee motion is prohibited.

Dark mode is `DEFERRED`. Paper Shaders is `EVALUATED_DEFERRED`. React Bits remains `REFERENCE_ONLY`. Figma synchronization is planned external work.
