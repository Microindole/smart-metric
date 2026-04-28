# SmartMetric Claude-Like Workbench Redesign Design

## Goal

Upgrade the SmartMetric frontend from a basic course demo UI into a restrained Claude-like professional workbench while preserving all existing routes, API calls, metric logic, and Ant Design Vue usage.

## Selected Direction

The selected visual direction started as **A: Professional SaaS Workbench** and was refined toward a Claude-like warm neutral workbench.

Visual thesis: a calm measurement workspace with warm off-white surfaces, deep readable text, restrained clay accent, precise spacing, and dense but readable information hierarchy.

Content plan:

- Global shell: stable left navigation, concise product identity, workflow-oriented module labels.
- Home: operational overview and module launcher, not a marketing landing page.
- Metric pages: clear page header, compact input panels, result panels, and export actions.
- Report/export flow: make generated outputs feel like formal deliverables.
- Product-level details: global command palette, lightweight workflow-plugin entries, polished focus/hover/empty states.

Interaction thesis:

- Subtle hover elevation on module entries and action surfaces.
- Lightweight active-navigation treatment that improves scanning without visual noise.
- Smooth focus/transition states for upload, calculate, and export actions.

## Scope

In scope:

- Redesign `frontend/components/AppLayout.vue` as the shared app shell.
- Redesign `frontend/pages/index.vue` as a polished workbench home.
- Add global frontend polish in `frontend/app.vue` if needed for font smoothing, body background, and Ant Design surface consistency.
- Apply reusable visual rules that improve existing metric pages without changing their data flow.
- Update `agents/frontend.md` if frontend structure, visual conventions, or startup guidance changes in a way future agents need to know.

Out of scope:

- No backend API changes.
- No metric formula changes.
- No new dependencies unless clearly justified.
- No static HTML rewrite.
- No marketing-style hero page that hides the actual tool.
- No full dark-mode redesign.

## Layout Design

The app remains a left-nav workbench:

- Sidebar width increases slightly for better labels and breathing room.
- Sidebar uses a muted white surface with a stronger product header and grouped navigation.
- Main area uses a soft neutral background and a constrained content width where useful.
- Each page keeps its existing content, but the common shell provides stronger hierarchy and spacing.
- The shared shell includes a command palette for searching and opening modules, keeping quick navigation centralized.

The home page becomes a dashboard-like module launcher:

- Top strip: SmartMetric title, short utility description, and system status hints.
- Feature modules arranged as compact repeated items with metric acronym, purpose, and route.
- A small engine strip summarizes the core metric capabilities without mirroring assignment steps.
- Supporting project tools appear as lightweight workflow-plugin rows rather than a decorative plugin marketplace.

## Visual System

Palette:

- Base: `#f7f4ee`, `#fffaf4`, `#e2d9cf`.
- Text: `#191714`, `#312c26`, `#766b60`.
- Accent: `#c65f3d` / `#a94f34` with restrained use.
- Support accents may use teal/amber/rose only for categorical status, not as dominant theme.

Shape:

- Border radius should stay at 8px or less for product UI.
- Cards are allowed for repeated module entries and tool panels, not nested decorative containers.

Typography:

- Use the existing system font stack.
- Page headings should be compact and workbench-like, not hero-scale inside tool pages.
- Letter spacing should remain normal.

## Implementation Notes

Use existing Nuxt 3 and Ant Design Vue patterns:

- Keep `AppLayout` props compatible with all existing pages.
- Keep route paths unchanged.
- Use existing `$router.push` navigation behavior.
- Do not bypass `frontend/utils/api.js`.
- Prefer CSS-only polish over new component libraries.

## Validation

Required checks after implementation:

- Backend smoke remains reachable: `curl.exe --max-time 10 http://127.0.0.1:5000/api/health`.
- Frontend pages return 200 at least for `/`, `/usecase-metric`, `/loc-metric`, `/function-point`, `/oo-metric`, `/cfg-metric`, `/project-metric`, `/estimate-metric`, `/report-export`.
- Run focused backend tests if only frontend files changed is optional, but existing running backend should not be broken.
- Verify with browser or screenshots at desktop and mobile widths that text does not overlap and navigation remains usable.

## Documentation

Because this changes frontend visual structure and conventions, update `agents/frontend.md` with a short note describing the shared Claude-like workbench shell and home-page strategy.
