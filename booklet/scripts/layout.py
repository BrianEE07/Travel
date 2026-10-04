"""Shared A6 primitives. Call configure() before importing a trip composition."""
from pathlib import Path
import json
import re
from xml.sax.saxutils import escape

from PIL import Image
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader

W, H = 105 * mm, 148 * mm
INK = HexColor('#173E56')
TEXT = HexColor('#253F46')
MUTED = HexColor('#64787B')
TEAL = HexColor('#438779')
RULE = HexColor('#D4E0DF')
PALE = HexColor('#EDF5F2')
ROOT = OUT = ASSETS = TMP = None
SOURCES = {}
TRIP = {}
BOXES = []
IMAGE_QA = []
PAGE = 0

def configure(root, output, temporary, trip, fonts):
    global ROOT, OUT, ASSETS, TMP, TRIP, SOURCES, PAGE
    ROOT, OUT, TMP = Path(root), Path(output), Path(temporary)
    ASSETS = ROOT / 'assets'
    TRIP = trip
    sources = json.loads((ROOT / 'photo-sources.json').read_text())
    SOURCES = {entry['file']: entry for entry in sources}
    if len(SOURCES) != len(sources):
        raise ValueError('Duplicate photo source filename')
    for entry in sources:
        candidate = (ASSETS / entry['file']).resolve()
        if not candidate.is_relative_to(ASSETS.resolve()):
            raise ValueError('Photo path escapes trip assets')
        if not entry.get('source') or not entry.get('credit'):
            raise ValueError('Every photo requires source and credit')
    for name in ['TC', 'TCM', 'Baskerville', 'Arial', 'JP']:
        file = Path(fonts[name]).expanduser()
        if not file.is_absolute():
            file = ROOT / file
        if not file.is_file():
            raise FileNotFoundError(f'Missing {name} font: {file}; configure book-plan.json fonts')
        pdfmetrics.registerFont(TTFont(name, str(file), subfontIndex=0))
    BOXES.clear()
    IMAGE_QA.clear()
    PAGE = 0
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)


def supported_text(text, font):
    """Embed missing Japanese glyphs; never silently draw a .notdef square."""
    widths = pdfmetrics.getFont(font).face.charWidths
    fallback = pdfmetrics.getFont('JP').face.charWidths
    pieces = re.split(r'(<[^>]+>)', text)
    for i in range(0, len(pieces), 2):
        result = []
        for char in pieces[i]:
            if ord(char) in widths:
                result.append(char)
            elif ord(char) in fallback:
                result.append('<font name="JP">' + char + '</font>')
            else:
                raise ValueError(f'No font glyph for {char!r}')
        pieces[i] = ''.join(result)
    return ''.join(pieces)


def paragraph(c, text, x, top, width, size=10, leading=None, font='TC', color=TEXT, max_h=None):
    style = ParagraphStyle('booklet', fontName=font, fontSize=size, leading=leading or size * 1.35,
                           textColor=color, wordWrap='CJK', spaceBefore=0, spaceAfter=0)
    text = supported_text(text, font)
    p = Paragraph(text, style)
    _, height = p.wrap(width, H)
    if max_h is not None and height > max_h + 0.1:
        raise ValueError(f'Page {PAGE}: text needs {height:.1f}pt, available {max_h:.1f}pt: {text}')
    if x < 0 or x + width > W + 0.1 or top < 0 or top + height > H:
        raise ValueError(f'Text outside page {PAGE}: {text}')
    p.drawOn(c, x, H - top - height)
    BOXES.append({'page': PAGE, 'text': text, 'box': [x, top, width, height], 'size': size})
    return height


def label(c, text, x, top, size=7.5, color=TEAL, tracking=1.2):
    c.saveState()
    c.setFillColor(color)
    ob = c.beginText(x, H - top - size)
    ob.setFont('Arial', size)
    ob.setCharSpace(tracking)
    ob.textOut(text)
    c.drawText(ob)
    c.restoreState()


def line(c, x, top, width, color=RULE):
    c.setStrokeColor(color)
    c.setLineWidth(.45)
    c.line(x, H - top, x + width, H - top)


def photo(c, name, x, top, width, height, focus=(.5, .5)):
    # Crop in the PDF clipping path only; original photos are kept unchanged.
    path = ASSETS / name
    with Image.open(path) as im:
        iw, ih = im.size
    scale = max(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    c.saveState()
    clip = c.beginPath()
    clip.rect(x, H - top - height, width, height)
    c.clipPath(clip, stroke=0)
    c.drawImage(ImageReader(str(path)), x - (dw - width) * focus[0],
                H - top - height - (dh - height) * focus[1], dw, dh)
    c.restoreState()
    dpi = 72 / scale
    IMAGE_QA.append({'page': PAGE, 'file': name, 'effective_dpi': round(dpi)})
    if dpi < 200:
        raise ValueError(f'Photo {name} is too small for this placement ({dpi:.0f} dpi)')


def credit(c, name, x, top, width):
    src = SOURCES[name]
    paragraph(c, '照片：' + escape(src['credit']), x, top, width, size=6.5, color=MUTED)
    c.linkURL(src['source'], (x, H - top - 9, x + width, H - top), relative=0)


def footer(c, n, name):
    line(c, 8 * mm, 138 * mm, 89 * mm)
    label(c, "WEI'S TRAVEL JOURNAL", (17 if n % 2 == 0 else 8) * mm, 141 * mm, 6, MUTED, .6)
    c.setFont('Arial', 7)
    c.setFillColor(INK)
    if n % 2 == 0:
        c.drawString(8 * mm, H - 142.5 * mm, f'{n:02d}')
    else:
        c.drawRightString(97 * mm, H - 142.5 * mm, f'{n:02d}')
    c.bookmarkPage(name)
    c.addOutlineEntry(name, name)


def start(c):
    global PAGE
    PAGE += 1
    c.setFillColor(white)
    c.rect(0, 0, W, H, stroke=0, fill=1)


def timeline(c, day, number, english, title, rows, printed_page):
    start(c)
    x, width = 8 * mm, 87 * mm
    label(c, f'DAY {number:02d} / {english}', x, 9 * mm)
    paragraph(c, title, x, 16 * mm, width, size=19, font='TCM', color=INK)
    weekdays = {'Mon': '週一', 'Tue': '週二', 'Wed': '週三', 'Thu': '週四',
                'Fri': '週五', 'Sat': '週六', 'Sun': '週日'}
    paragraph(c, f"{day['date'][5:7]}/{day['date'][8:]} · {weekdays[day['weekday']]}",
              x, 27 * mm, width, size=9, color=MUTED)
    line(c, x, 36 * mm, width)
    y = 42 * mm
    node_x, body_x = 32 * mm, 38 * mm
    sizes = []
    for time, body, kind in rows:
        style = ParagraphStyle('measure', fontName='TC', fontSize=10, leading=12.4, wordWrap='CJK')
        _, h = Paragraph(escape(body), style).wrap(57 * mm, H)
        sizes.append(max(h, 12.4) + 2 * mm)
    if y + sum(sizes) > 127 * mm:
        raise ValueError(f'{title}: timeline does not fit at 10pt')
    line_end = y + sum(sizes[:-1]) + 5
    c.setStrokeColor(RULE)
    c.setLineWidth(.7)
    c.line(node_x, H - y - 5, node_x, H - line_end)
    for (time, body, kind), height in zip(rows, sizes):
        if kind == 'confirmed':
            c.setFillColor(PALE)
            c.roundRect(6 * mm, H - y - height + 1 * mm, 91 * mm, height, 2 * mm, stroke=0, fill=1)
        paragraph(c, escape(time), x, y + .2, 22 * mm, size=8, leading=11, font='Arial', color=INK)
        c.setFillColor(TEAL if kind in ('move', 'confirmed') else white)
        c.setStrokeColor(TEAL)
        c.setLineWidth(.7)
        c.circle(node_x, H - y - 5, 1.05 * mm, fill=1, stroke=1)
        paragraph(c, escape(body), body_x, y, 57 * mm, size=10, leading=12.4,
                  font='TCM' if kind == 'confirmed' else 'TC', color=INK if kind == 'confirmed' else TEXT)
        y += height
    line(c, x, 130 * mm, width)
    paragraph(c, '今晚住　' + escape(day['stay']), x, 132 * mm, width, size=8.5, color=INK)
    footer(c, printed_page, title)
    c.showPage()


def day(date):
    return next(d for d in TRIP['days'] if d['date'] == date)


def range_time(first, last):
    return first.split('-')[0] + '-' + last.split('-')[-1]
