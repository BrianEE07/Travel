# Website workflow

## Project map

- `scripts/lib/trip-parser.mjs`: shared Schema parser; `parseTrip` returns public trip plus private fingerprints in memory.
- `scripts/sync-trip.mjs`: exports only the selected trip, validates local cover/briefing assets; `draft` removes that trip's existing public JSON (withdrawal, not just a preview).
- `src/data/trips/<slug>.json`: public records; homepage and dynamic routes discover these automatically.
- `src/components/{HomePage,TripPage,ChecklistPage}.astro`, `entities/`, `src/styles/`: maintained UI.
- `scripts/scan-dist.mjs`: scans JSON/static outputs; with a locally available note also checks source fingerprints. CI has no Vault, so its scan is patterns/approved-field allowances only.
- `.github/workflows/deploy.yml`: builds committed public data on GitHub Pages after push to `main`; it cannot read the private note.

## Build and adapt

1. Inspect working tree/index and resolve target note. Compare canonical and mirror. Read relevant parser/type/component code before changing a field. Do not treat the mirror as permanently current.
2. For a new trip, create assets under its slug, validate metadata against the actual note, then run the existing shared parser. Do not copy the full Fukuoka UI or hardcode a new route.
3. `TRAVEL_NOTE_PATH="/absolute/note.md" npm run build` runs sync, tests, type check, Astro build, then privacy scan. A missing asset/invalid schema must block production. Do not weaken tests just to accept malformed source.
4. Test data semantics: overview dates vs metadata; Itinerary/Daily Plan coverage; full vs summary; entity references and lodging; transport exact segment table and optional cells; Note bullets; explicit images/credits; checklist arbitrary bilingual groups; reservation optional fields; private values excluded, approved prices retained.

## UI regression cases (when UI changes)

Use real browser screenshots at representative narrow/wide widths and mobile portrait/landscape; device examples are test cases, not CSS device-name exceptions.

- Body does not scroll horizontally, including long hotel names/images/URLs. Side padding survives a non-maximized desktop window.
- Mobile landscape prose does not inflate relative to inline links; distinguish browser text autosizing from authored font sizes.
- Modal locks background, restores position immediately without smooth-scroll jumps, preserves opener focus, supports close/Esc/back, and clears the previous image before switching entities.
- Transport segment deep links open the correct tab; optional missing values disappear. Content hierarchy stays consistent across lodging/food/place/transport.
- Date navigation centers the active date and updates while scrolling; tapping a date does not flicker through intermediate selections. Return home/overview/database/top controls remain reachable.
- SVG link/check/up/external-link icons stay centered and do not become emoji on mobile. Copy feedback returns to the normal ink color.
- Intro background fades continuously; reduced-motion visitors can enter without forced animation.
- Checklist state survives reload per-trip and per-item; source updates do not silently apply another item's check state. Never write browser checks back to the note.

For content-only rebuilds, tests/build plus a targeted changed-content inspection are normally enough; don't rerun a full UI redesign.

## Publication safety

Publishing needs explicit user authorization. `npm run publish` is for a note-only update: it refuses a dirty index, non-main branch or unpublished existing commits, builds first, then stages/commits only the selected trip JSON. It intentionally will not include code, format or images. For those changes, inspect the exact diff and make a separately scoped commit; do not stage everything.

Inspect `git status`, cached diff, branch/upstream and pending commits before any push. If pushing would publish unrelated commits or staged work, stop and ask. Do not reset, amend or stash user work to get around a guard. After pushing, confirm deployment status and the intended live content when network access permits; otherwise state that live confirmation remains pending.

## Boundaries

Schema documentation can require verification that a Maps URL opens the exact place/branch. A syntactically valid URL or HTTP 200 does not prove that. Do not mark an unresolved destination verified. Changing source logistics belongs to the note-planning workflow, not a website rebuild.
