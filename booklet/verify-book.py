"""Verify one trip's geometry, content, privacy payload and folded reading order."""
import json
import sys
from pathlib import Path
from collections import Counter
from pypdf import PdfReader
import pdfplumber

sys.path.insert(0, str(Path(__file__).resolve().parent / 'scripts'))
from context import load_context, slug_argument
from imposition import folded_order, print_mapping


def main():
    root, temporary, output, plan, trip = load_context(slug_argument())
    qa = json.loads((temporary / 'book-qa.json').read_text(encoding='utf8'))
    if qa['source_hash'] != trip['sourceHash']:
        raise ValueError('Stale book QA snapshot')
    count = plan['pageCount']
    readers = {key: PdfReader(output / filename) for key, filename in plan['outputs'].items()}
    expected = {'reading': (count, 105, 148), 'facing': (count // 2 + 1, 210, 148),
                'printing': (len(print_mapping(count)), 210, 297)}
    for key, (pages, width, height) in expected.items():
        reader = readers[key]
        assert len(reader.pages) == pages, f'{key}: wrong page count'
        for page in reader.pages:
            assert abs(float(page.mediabox.width) / 72 * 25.4 - width) < .01
            assert abs(float(page.mediabox.height) / 72 * 25.4 - height) < .01
    for index, a in enumerate(qa['text_boxes']):
        ax, ay, aw, ah = a['box']
        assert ay + ah < 138 / 25.4 * 72, f'Text below safe content area on page {a["page"]}'
        for other in qa['text_boxes'][index + 1:]:
            if a['page'] != other['page']:
                continue
            bx, by, bw, bh = other['box']
            assert (min(ax + aw, bx + bw) - max(ax, bx) <= .5 or
                    min(ay + ah, by + bh) - max(ay, by) <= .5), f'Overlapping text page {a["page"]}'
    with pdfplumber.open(output / plan['outputs']['reading']) as pdf:
        for number, page in enumerate(pdf.pages, 1):
            for ch in page.chars:
                assert ch['x0'] >= -.1 and ch['x1'] <= page.width + .1
                assert ch['top'] >= -.1 and ch['bottom'] <= page.height + .1
            footer = [ch for ch in page.chars if ch['top'] > 140 / 25.4 * 72]
            outer = [ch for ch in footer if (ch['x0'] < 12 / 25.4 * 72 if number % 2 == 0
                                            else ch['x0'] > 92 / 25.4 * 72)]
            assert ''.join(ch['text'] for ch in outer) == f'{number:02d}', f'Footer page {number}'
    text = '\n'.join(page.extract_text() or '' for page in readers['reading'].pages)
    assert '\x00' not in text and '\ufffd' not in text, 'Unmapped font glyph'
    for fact in plan.get('requiredFacts', []):
        assert fact in text, f'Important source fact missing: {fact}'
    for row in qa['timeline_sources']:
        source = next(day for day in trip['days'] if day['date'] == row['date'])
        first, last = [source['timeline'][i] for i in [row['indices'][0], row['indices'][-1]]]
        expected_time = first['time'] if len(row['indices']) == 1 else first['time'].split('-')[0] + '-' + last['time'].split('-')[-1]
        assert row['time'] == expected_time and row['time'] in text, 'Source timeline time mismatch'
    assert all(photo['effective_dpi'] >= 200 for photo in qa['photos']), 'Low resolution photo'
    mapping = qa['imposition']
    assert mapping == json.loads(json.dumps(print_mapping(count))), 'Incorrect print mapping'
    assert folded_order(mapping) == list(range(1, count + 1)), 'Incorrect folded order'
    for index, side in enumerate(mapping):
        actual = readers['printing'].pages[index].extract_text() or ''
        expected_text = '\n'.join(readers['reading'].pages[n - 1].extract_text() or ''
                                  for half in ['top', 'bottom'] for n in side[half] if n)
        assert Counter(actual.split()) == Counter(expected_text.split()), f'Print side {index + 1} content mismatch'
    artifacts = []
    for key, reader in readers.items():
        links = []
        for page in reader.pages:
            for annotation in page.get('/Annots', []):
                annotation = annotation.get_object()
                action = annotation.get('/A')
                if action:
                    action = action.get_object()
                    if '/URI' in action:
                        links.append(str(action['/URI']))
        artifacts.append({'kind': key, 'text': '\n'.join(page.extract_text() or '' for page in reader.pages),
                          'links': links, 'metadata': {str(k): str(v) for k, v in (reader.metadata or {}).items()}})
    (temporary / 'book-privacy.json').write_text(json.dumps({'sourceHash': trip['sourceHash'], 'artifacts': artifacts},
                                                          ensure_ascii=False), encoding='utf8')
    (temporary / 'book-text.txt').write_text(text, encoding='utf8')
    print(f'PASS: {count} A6 pages, {len(readers["printing"].pages)} A4 sides; text/glyphs, photos, source times and folded order.')
    print('Next: export-source.mjs --note <note> --verify for private fingerprint scan, then render/visual review.')


if __name__ == '__main__':
    main()
