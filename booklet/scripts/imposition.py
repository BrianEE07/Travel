"""A6 reading pages → facing preview + A4 cut/nest/fold duplex print file."""
import io
from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor


def leaf_pairs(count):
    if count < 4 or count % 4:
        raise ValueError('Booklet reading page count must be a positive multiple of 4 (at least 4).')
    return [((count - 2 * i, 1 + 2 * i), (2 + 2 * i, count - 1 - 2 * i))
            for i in range(count // 4)]


def print_mapping(count):
    leaves = leaf_pairs(count)
    result = []
    for first in range(0, len(leaves), 2):
        for side in range(2):
            result.append({'sheet': first // 2 + 1, 'side': 'front' if side == 0 else 'back',
                           'top': leaves[first][side],
                           'bottom': leaves[first + 1][side] if first + 1 < len(leaves) else (None, None)})
    return result


def folded_order(mapping):
    leaves = []
    for front, back in zip(mapping[::2], mapping[1::2]):
        for half in ['top', 'bottom']:
            f, r = front[half], back[half]
            if not any(f):
                if any(r):
                    raise ValueError('Unpaired blank leaf')
                continue
            if r[0] != f[1] + 1 or r[1] != f[0] - 1:
                raise ValueError('Incorrect reverse-side leaf pairing')
            leaves.append((f, r))
    return ([n for front, back in leaves for n in [front[1], back[0]]] +
            [n for front, back in reversed(leaves) for n in [back[1], front[0]]])


def compose(source, facing_path, print_path, title):
    reader = PdfReader(source)
    count = len(reader.pages)
    mapping = print_mapping(count)
    w, h = 105 * mm, 148 * mm
    for page in reader.pages:
        if abs(float(page.mediabox.width) - w) > .02 or abs(float(page.mediabox.height) - h) > .02:
            raise ValueError('A4 cut/fold imposition requires 105 × 148 mm artwork, no scaling.')
    facing = PdfWriter()
    pairs = [(None, 1)] + [(n, n + 1) for n in range(2, count, 2)] + [(count, None)]
    for pair in pairs:
        spread = facing.add_blank_page(2 * w, h)
        for side, number in enumerate(pair):
            if number:
                spread.merge_transformed_page(reader.pages[number - 1], Transformation().translate(tx=side * w))
    facing.add_metadata({'/Title': title + ' | Facing preview (not print imposition)', '/Author': 'Wei'})
    facing.write(facing_path)
    printing = PdfWriter()
    for side in mapping:
        page = printing.add_blank_page(210 * mm, 297 * mm)
        for half, y in [('top', 148.75 * mm), ('bottom', .25 * mm)]:
            for position, number in enumerate(side[half]):
                if number:
                    page.merge_transformed_page(reader.pages[number - 1],
                                                Transformation().translate(tx=position * w, ty=y))
        guides = io.BytesIO()
        c = canvas.Canvas(guides, pagesize=(210 * mm, 297 * mm))
        c.setStrokeColor(HexColor('#64787B'))
        c.setLineWidth(.25)
        c.setDash(2, 3)
        c.line(4 * mm, 148.5 * mm, 206 * mm, 148.5 * mm)
        c.setDash()
        for y in [0, 148.5, 297]:
            c.line(105 * mm, (y - .25) * mm, 105 * mm, (y + .25) * mm)
        c.save()
        page.merge_page(PdfReader(guides).pages[0])
    printing.add_metadata({'/Title': title + ' | A4 duplex cut/fold', '/Author': 'Wei',
                          '/Subject': 'A4 portrait, 100%, duplex long-edge; cut y=148.5mm; nest A5 leaves then fold.'})
    printing.write(print_path)
    write_print_guide(Path(print_path).parent / 'PRINTING.md', mapping, count)
    return mapping


def write_print_guide(target, mapping, count):
    lines = [f'# A6 手冊列印說明（{count} 頁）', '',
             'A4 直式、實際大小 100%、雙面長邊翻轉；關閉小冊子、多頁拼印及自動縮放。', '',
             '先試印第一張正反面，確認字體方向與配頁。沿 y=148.5 mm 水平裁半成 A5；',
             '以正面右側奇數頁 1、3、5… 由外到內疊放，整疊沿 x=105 mm 對折成 A6。',
             '沒有頁碼的空白半張不加入冊子。實體高度 148.5 mm，可最後修到 148 mm。', '',
             '| A4 紙 | 面 | 上半 | 下半 |', '| --- | --- | --- | --- |']
    for side in mapping:
        pair = lambda numbers: '｜'.join(str(n) if n else '空白' for n in numbers)
        lines.append(f'| {side["sheet"]} | {"正面" if side["side"] == "front" else "背面"} | {pair(side["top"])} | {pair(side["bottom"])} |')
    target.write_text('\n'.join(lines) + '\n', encoding='utf8')
