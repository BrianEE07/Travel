# Approved aesthetic and folding model

Use project `booklet/references/fukuoka-approved-a6.pdf` to inspect cover, one lodging page, daily spreads and checklist. It establishes Wei's preferred white/navy/soft-teal editorial feel, not compulsory page content.

The current shared tools implement A6 artwork/A4 cut-fold only. If the user chooses another size or binding, adapt the geometry and verification deliberately; do not feed other dimensions into this imposition or claim it already supports them.

At A6, the reference uses roughly 10 pt prose, 8–8.5 pt short timing/metadata, and 6.5 pt photo attribution. Keep prose readable rather than shrinking everything to force a page count. Use source-correct photos, quiet rules, bounded highlights, inside binding margins, and outward bottom page numbers (even left, odd right). Chinese and Japanese place names require embedded verified glyph coverage. A full-day left timeline/right photo-reminders spread is a useful starting layout, not mandatory for every trip.

## Content economy

Overview: dates/destinations/page pointers. Flight/lodging pages: information repeatedly needed on site. Daily pages: essential sequence, commitments, execution reminders, selected scenery. Packing/shopping: compact source-derived groups. Don't repeat whole accommodation details under each day, or turn every entity into a separate printed page. Summary days must be labeled as tentative; don't manufacture a timeline.

## A4 → A5 → A6

For N reading pages, require N divisible by 4. Each A5 leaf carries four numbered pages; outer-to-inner leaf i (zero based):

- Front: `N−2i | 1+2i`
- Back: `2+2i | N−1−2i`

Put two consecutive A5 leaves on the top and bottom of one A4 portrait sheet, front then back. Long-edge duplex keeps the top/bottom halves paired and reverses left/right as required. If the number of leaves is odd, leave the final lower half blank; do not duplicate a numbered page to fill it. Multiples of 8 use complete A4 sheets, but aren't required.

Default artwork 105 × 148 mm sits inside each 105 × 148.5 mm physical folded half, with 0.25 mm top/bottom allowance. Cut horizontally at 148.5 mm, not vertically. Nest cut A5 leaves with odd right-side front pages 1,3,5… from outer to inner, then fold the entire stack along x=105 mm. Optional final trimming makes the physical height exactly 148 mm.

Print guide must say A4 portrait, actual size 100%, duplex long-edge; disable printer booklet/multiple-pages/scaling because this PDF is already imposed. Recommend a front/back test sheet to verify the printer's flip behavior before the full run. Facing-spread preview is never the print file.
