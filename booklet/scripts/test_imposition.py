"""Exercise real PDF placement and page-order invariants at several lengths."""
import tempfile
import unittest
from pathlib import Path
from collections import Counter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pypdf import PdfReader
import pdfplumber
from imposition import compose, folded_order, print_mapping, leaf_pairs


class ImpositionTest(unittest.TestCase):
    def test_lengths_and_blank_half(self):
        for count in [4, 8, 12, 16, 20, 24, 28, 32, 40]:
            with self.subTest(count=count):
                mapping = print_mapping(count)
                self.assertEqual(folded_order(mapping), list(range(1, count + 1)))
                counts = Counter(n for side in mapping for half in ['top', 'bottom'] for n in side[half] if n)
                self.assertEqual(counts, Counter(range(1, count + 1)))
                self.assertEqual(mapping[-1]['bottom'] == (None, None), count % 8 == 4)

    def test_invalid_lengths(self):
        for count in [0, 1, 5, 6, 7, 23]:
            with self.assertRaises(ValueError):
                leaf_pairs(count)

    def test_actual_pdf_sides(self):
        with tempfile.TemporaryDirectory(prefix='travel-impose-') as temporary:
            root = Path(temporary)
            for count in [4, 12, 24, 32]:
                source, facing, printing = [root / name for name in ['reading.pdf', 'facing.pdf', 'print.pdf']]
                c = canvas.Canvas(str(source), pagesize=(105 * mm, 148 * mm))
                for page in range(1, count + 1):
                    c.drawString(30, 200, f'PAGE-{page:02d}')
                    c.showPage()
                c.save()
                mapping = compose(source, facing, printing, 'Test booklet')
                self.assertEqual(len(PdfReader(facing).pages), count // 2 + 1)
                reader = PdfReader(printing)
                self.assertEqual(len(reader.pages), len(mapping))
                for page, side in zip(reader.pages, mapping):
                    self.assertEqual(Counter(page.extract_text().split()),
                                     Counter(f'PAGE-{n:02d}' for half in ['top', 'bottom'] for n in side[half] if n))
                    self.assertAlmostEqual(float(page.mediabox.height) / mm, 297, places=3)
                with pdfplumber.open(printing) as document:
                    for page, side in zip(document.pages, mapping):
                        for word in page.extract_words():
                            half = 'top' if word['top'] < 148.5 * mm else 'bottom'
                            position = 0 if word['x0'] < 105 * mm else 1
                            self.assertEqual(word['text'], f'PAGE-{side[half][position]:02d}')


if __name__ == '__main__':
    unittest.main()
