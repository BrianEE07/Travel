---
name: wei-travel-website
description: "Build, update, verify, and publish Wei's travel website from Obsidian Travel Schema notes. Use for 旅遊網頁、行程網站、更新筆記後重建 or adding a trip to the Travel project; not for planning the trip or producing a printed booklet."
---

# Wei Travel Website

Use the existing shared static website, not a separate website per trip. Default project: `/Users/ywfan/Documents/Side_Projects/Travel`; use the user's supplied checkout if different. Read the project's README and relevant instructions before changes. Maintained parser/components live in the project, not copied into this skill.

## Source and scope

- Read the current Vault canonical `99_Vault_System/AGENT/Travel Note Format.md` and compare with project `TRAVEL_NOTE_FORMAT.md`; synchronize the mirror when updating. Default Vault: `/Users/ywfan/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecondBrain`. Do not change the canonical or original itinerary without authorization. If parser support differs, adapt and test it rather than silently dropping fields.
- Resolve the exact source note; always set `TRAVEL_NOTE_PATH` when building. `trip_slug` determines JSON/routes, not the note's filename. Preserve other trips. New public assets go under `public/images/trips/<slug>/`; keep existing published asset URLs working.
- Parse through `scripts/lib/trip-parser.mjs`. Only allowlisted sections are public; unknown sections and `Private` stay private. Do not upload source Markdown, screenshots of bookings, or secret fingerprints. Explicit schema-approved prices are public; that does not make payment evidence or identifiers public.
- Read [references/workflow.md](references/workflow.md) for implementation, verification, or deployment. Building is not permission to push. Deploy only when requested; stop on validation failures or ambiguous Git scope.

## Product defaults

Preserve the cream/ink/low-saturation travel-journal visual language, readable Chinese hierarchy, responsive spacing, and consistent SVG icons. Homepage lists trips; `/<slug>/` contains itinerary and entity modals; optional `/<slug>/checklists/` is generated from dynamic categories. Do not add YAML properties for presentation details that can be derived or authored in project code.

Images use explicit `Image` references and `ImageCredit`, not official-site preview scraping. Modal image state resets before a new entity loads; image failure hides the visual while retaining information. Transportation stays one entity with per-segment folder tabs and heading links to specific segments; compact cards currently use the first segment unless a new selection rule is explicitly implemented.

## Delivery

Run schema/regression tests, type checks, static build and public-output privacy checks. For UI edits, use a real browser and relevant mobile/desktop cases from the reference. Report what changed, tests actually run, and whether deployment was performed and confirmed. Do not label a local build as live.
