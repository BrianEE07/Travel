# Production workflow

## Layout and source ownership

`booklet/scripts/` holds shared layout, imposition and verification. `booklet/trips/<slug>/book-plan.json` records reviewed hash, expected date range/page count, output names, font files and important facts; `render.py` holds that trip's curated composition. `photo-sources.json` and `assets/` belong to that trip. `booklet/references/` is a frozen approved visual baseline. Generated source/QA/renders go in ignored `booklet/tmp/<slug>/`; final PDFs go in `output/pdf/<slug>/`, outside website `public` and `dist`.

There is no all-trips one-click editorial engine: a new trip gets its own reviewed plan/renderer using shared primitives. Do not copy Fukuoka dates, baggage claims, reminders or fixed number of days. Keep layout mechanics out of the destination recipe where practical.

## Commands

Resolve a Python runtime with reportlab, Pillow, pypdf and pdfplumber (use the product's workspace-dependency discovery rather than assuming a machine path). From the project root:

```sh
node booklet/export-source.mjs --note "/absolute/旅程.md"
python3 booklet/build-book.py --slug <slug>
python3 booklet/verify-book.py --slug <slug>
node booklet/export-source.mjs --note "/absolute/旅程.md" --verify
pdftoppm -scale-to 1500 -png output/pdf/<slug>/facing-spreads.pdf booklet/tmp/<slug>/spread
pdftoppm -scale-to 1500 -png output/pdf/<slug>/print-a4.pdf booklet/tmp/<slug>/print-side
```

Output basenames are set in the plan, so use the actual names rather than assuming the examples. Export only validates/parses notes; it does not check website assets or write `src/data/trips`. A source hash change stops building until editorial review; do not disable this safeguard. `--verify` requires extracted artifact payload and matching source hash, re-reads the note, scans public text/URLs/metadata with approved prices/images, and doesn't overwrite the reviewed snapshot.

## New trip or content update

1. Read live canonical format; export note; inspect only sanitized snapshot for layout planning. Private data must not be copied into plans, manifests or screenshots.
2. Draft page outline and duplication budget. Agree on a sample spread/design if no approved style applies. Decide fixed vs flexible timeline markers based on evidence.
3. Select assets and record place, source page, credit, original image URL and intended personal/public use. Verify seasonal/geographic correctness and crop subject. Check effective DPI at the intended placement (200 minimum for this small personal book, 300 preferable). Do not overwrite originals.
4. Author destination recipe using `layout` primitives. Fonts are configured in the plan; missing font/glyph is an error, not a silent replacement. Preserve font licenses. Local system-font paths may be used when available but are not portable defaults.
5. Bind curated rows to source indices plus expected text or stronger IDs. Record time provenance and essential facts. Highlight classes should have a clear legend; green does not automatically mean every move is reserved.
6. Build → automated verify → fingerprint scan → render/inspect each page and every print side. If a source update affects a route, hotel or reminder, review its curated text as well as timestamps before updating `reviewedSourceHash`.
7. Deliver PDFs and current print guide. Only mark visual QA complete after inspection, and physical print QA complete after an actual printer test.

## Verification checklist

- Reading/facing/print dimensions, expected page count and source hash.
- Content/footer safe areas, no overlapping text, no missing glyph/NUL/replacement characters, outer page numbers.
- Critical facts and source timing provenance retained, no stale summary from another note.
- Photo resolution and source records; inspect whether crop is compositionally correct.
- Each numbered page appears once in print mapping; simulate nested leaves and require 1..N reading order, including optional blank A4 half.
- PDF text, metadata and link destinations scanned; visual assets checked for visible private information.
- Inspect all rendered reading/facing pages and print sides. Mechanical verification cannot certify factual accuracy, image rights or legibility by itself.
