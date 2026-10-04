from pathlib import Path
import json
import pdfplumber
from pypdf import PdfReader

root = Path(__file__).resolve().parent
source = root.parent / 'output/pdf/fukuoka-2026/fukuoka-a6-sample.pdf'
reader = PdfReader(source)
assert len(reader.pages) == 5
for p in reader.pages:
    assert abs(float(p.mediabox.width) / 72 * 25.4 - 105) < .01
    assert abs(float(p.mediabox.height) / 72 * 25.4 - 148) < .01
text = '\n'.join(p.extract_text() for p in reader.pages)
for expected in ['07:43-10:02', '17:17-19:27', '17:05 / 17:25', '19:55', '20:15', '金鱗湖', '門司港站']:
    assert expected in text, f'Missing source fact: {expected}'
with pdfplumber.open(source) as pdf:
    for page in pdf.pages:
        for ch in page.chars:
            assert ch['x0'] >= -0.1 and ch['x1'] <= page.width + .1, 'Horizontal text overflow'
            assert ch['top'] >= -0.1 and ch['bottom'] <= page.height + .1, 'Vertical text overflow'
qa = json.loads((root / 'tmp/fukuoka-2026/layout-qa.json').read_text())
for index, a in enumerate(qa['text_boxes']):
    ax, ay, aw, ah = a['box']
    for b in qa['text_boxes'][index + 1:]:
        if a['page'] != b['page']:
            continue
        bx, by, bw, bh = b['box']
        overlap_x = min(ax + aw, bx + bw) - max(ax, bx)
        overlap_y = min(ay + ah, by + bh) - max(ay, by)
        assert overlap_x <= .5 or overlap_y <= .5, f'Overlapping text: {a["text"]} / {b["text"]}'
(root / 'tmp/fukuoka-2026/sample-text.txt').write_text(text)
print('QA passed: five A6 pages, source times retained, text within pages, no overlapping text blocks')
