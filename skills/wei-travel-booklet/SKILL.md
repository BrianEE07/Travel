---
name: wei-travel-booklet
description: "Plan and produce Wei's printable travel handbooks directly from Travel Schema notes, including reading PDFs, facing previews, and verified cut/fold booklet imposition. Use for 旅行手冊、紙本行程、A6 小冊子; a built or deployed website is not required."
---

# Wei Travel Booklet

Produce a practical, edited booklet, not a printout of the website. Default project: `/Users/ywfan/Documents/Side_Projects/Travel`; use the user's supplied project if different. Shared parser/layout/imposition tools are maintained there. No Astro build, public trip JSON in `src`, running website, or deployment is required.

## Intake and plan approval

Resolve the source note and read the latest Vault canonical `99_Vault_System/AGENT/Travel Note Format.md`; compare/sync the project's mirror for this workflow. Do not rewrite the original note without permission. Export directly with `booklet/export-source.mjs` through the same parser/privacy boundary as the website; only sanitized data goes into ignored `booklet/tmp/<slug>/`.

Before full production, agree on size, folding/binding, page outline and content selection. Default for Wei: A6 artwork 105 × 148 mm; A4 portrait duplex, cut horizontally into two A5 landscape leaves, nest and fold once to A6. Page count follows content, not the Fukuoka example. Read [references/production.md](references/production.md) for commands, asset organization and QA; read [references/design-print.md](references/design-print.md) when planning layout/imposition.

## Editorial and privacy boundary

- Use the approved `booklet/references/fukuoka-approved-a6.pdf` as an aesthetic reference, not a source of facts for a different trip.
- Default to white, navy/soft teal, clear hierarchy, generous margins and accurate real-place photographs. Destination-specific titles, bilingual labels, dates, photos and page count belong to `booklet/trips/<slug>/`, not universal code or additional YAML properties.
- Avoid repeated detail: overview locates days; lodging pages hold addresses/access; daily spreads hold operational times, main moves and essential reminders. Checklist categories come from the note, never a fixed category catalog. Paper does not inherit browser checkbox state.
- Keep confirmed departures, reservations, meeting times and return cutoffs; distinguish fixed commitments from flexible plans. Never invent confirmed status, baggage allowance, address, timing or actual travel experiences. Authored summaries require source checks.
- Photos must represent the correct place/branch/season, with sources and usage basis recorded. Do not pass generated imagery off as a true photograph of a destination. Image generation for artwork requires the available imagegen skill; image research requires source verification. Attribution alone is not a redistribution license.
- Private identifiers, authentication codes and management/cancellation links stay out of PDFs, metadata, QR codes and image assets. Include prices only where current format and user intent permit them. Public distribution needs a separate image-rights check; creating a personal booklet does not authorize uploading it.

## Verification and handoff

Use the available PDF skill/runtime for generation and visual review. Freeze an approved reference before refactoring. Build reading pages first, then shared deterministic imposition. Verify source hash, operational timings, text bounds/overlap, embedded glyphs, outer-corner page numbers, image resolution, exact geometry and simulated folded reading order. Inspect rendered pages and print sides, not just extracted text. Scan text, links and metadata against source secret fingerprints held only in memory.

Deliver reading PDF, facing preview, A4 print PDF and matching print instructions. If the note changed, stop and review affected editorial text before updating the reviewed hash; never bump a hash merely to make a build pass. A successful automated check is not a substitute for visual review or an actual printer test.
