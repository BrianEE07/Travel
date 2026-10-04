"""Reviewed Fukuoka-only cover and photo spread compositions."""
from layout import *

def cover(c):
    start(c)
    x, width = 8 * mm, 89 * mm
    label(c, 'LATE SUMMER / KYUSHU', x, 10 * mm, 7.5, INK)
    paragraph(c, 'FUKUOKA', x, 18 * mm, width, size=39, leading=42, font='Baskerville', color=INK)
    paragraph(c, '福岡旅行手帖', x, 35 * mm, width, size=20, font='TCM', color=INK)
    photo(c, 'futamigaura.png', 8 * mm, 51 * mm, 89 * mm, 52 * mm, focus=(.56, .5))
    paragraph(c, '糸島・櫻井二見浦', x, 105 * mm, width, size=8, color=INK)
    credit(c, 'futamigaura.png', x, 110 * mm, width)
    paragraph(c, '八天，沿著九州的城市與山海慢慢走。', x, 118 * mm, width, size=10, color=INK)
    line(c, x, 128 * mm, width)
    label(c, '2026.08.27 - 09.03', x, 132 * mm, 9, INK, .4)
    label(c, "WEI'S TRAVEL JOURNAL", x, 139 * mm, 6.5, MUTED, .7)
    c.setFont('Arial', 7)
    c.setFillColor(INK)
    c.drawRightString(97 * mm, H - 142.5 * mm, '01')
    c.showPage()


def yufu_photos(c):
    start(c)
    x, width = 10 * mm, 87 * mm
    label(c, 'LAKE / STREETS / A SLOW AFTERNOON', x, 9 * mm, 6.5, tracking=.5)
    paragraph(c, '把步調留給山與湖', x, 15 * mm, width, size=16, font='TCM', color=INK)
    photo(c, 'kinrin-summer.jpg', x, 27 * mm, width, 49 * mm)
    paragraph(c, '金鱗湖', x, 79 * mm, width, size=11, font='TCM', color=INK)
    credit(c, 'kinrin-summer.jpg', x, 85 * mm, width)
    photo(c, 'yufuin-station.jpg', x, 94 * mm, 37 * mm, 27.8 * mm)
    paragraph(c, '由布院站', x, 123 * mm, 37 * mm, size=8.5, color=INK)
    credit(c, 'yufuin-station.jpg', x, 128 * mm, 40 * mm)
    tx = 51 * mm
    paragraph(c, '回程前，慢慢收尾', tx, 94 * mm, 46 * mm, size=10, font='TCM', color=TEAL)
    paragraph(c, '15:30 後留在車站周邊。<br/>16:30 開始往車站收斂。<br/>JR 已訂，先取實體票。',
              tx, 101 * mm, 46 * mm, size=9.5, leading=13)
    paragraph(c, '花野そば售完為止；<br/>午餐保留備案。', tx, 120 * mm, 46 * mm, size=9.5, leading=13)
    footer(c, 11, '由布院・風景與提醒')
    c.showPage()


def kitakyushu_photos(c):
    start(c)
    x, width = 10 * mm, 87 * mm
    label(c, 'HARBOUR / HERITAGE / NIGHT VIEW', x, 9 * mm, 6.5, tracking=.5)
    paragraph(c, '港町散步，山上看夜景', x, 15 * mm, width, size=14.5, font='TCM', color=INK)
    photo(c, 'mojiko.jpg', x, 25 * mm, width, 43 * mm)
    paragraph(c, '門司港站', x, 70 * mm, width, size=10, font='TCM', color=INK)
    credit(c, 'mojiko.jpg', x, 75.5 * mm, width)
    c.setFillColor(PALE)
    c.roundRect(x, H - 99 * mm, width, 17 * mm, 1.5 * mm, stroke=0, fill=1)
    paragraph(c, '接駁去程 17:05 / 17:25。<br/>下山抓 19:55 或 20:15 的接駁。<br/>天候不佳，改展望室或提早回飯店。',
              x + 3 * mm, 84 * mm, width - 6 * mm, size=9.2, leading=12.1, max_h=14 * mm)
    photo(c, 'sarakura.jpg', x, 103 * mm, width, 26 * mm, focus=(.5, .62))
    paragraph(c, '皿倉山夜景', x, 130 * mm, 40 * mm, size=8.5, color=INK)
    credit(c, 'sarakura.jpg', 52 * mm, 131 * mm, 45 * mm)
    footer(c, 15, '北九州・風景與提醒')
    c.showPage()
