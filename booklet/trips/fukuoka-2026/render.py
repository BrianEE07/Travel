"""24-page A6 reading edition, facing preview, and duplex A4 cut/fold imposition.

All operational times come from the parser's public snapshot. Editorial summaries
are deliberately curated; changed/missing source rows stop the build for review.
"""
import json
from xml.sax.saxutils import escape

from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.lib.units import mm

import layout as b
import artwork
W, H = b.W, b.H
WEB = None
PROVENANCE = []


def p(c, text, top, size=10, x=8, width=89, **kw):
    return b.paragraph(c, text, x * mm, top * mm, width * mm, size=size, **kw) / mm


def header(c, kicker, title, subtitle=None):
    b.start(c)
    b.label(c, kicker, 8 * mm, 9 * mm)
    p(c, title, 16, 19, font='TCM', color=b.INK)
    if subtitle:
        p(c, subtitle, 27, 8.5, color=b.MUTED)
    b.line(c, 8 * mm, 36 * mm, 89 * mm)


def end(c, title):
    b.footer(c, b.PAGE, title)
    c.showPage()


def note(c, title, text, top, size=10):
    title_h = p(c, escape(title), top, 10, font='TCM', color=b.TEAL)
    body_h = p(c, escape(text), top + title_h + 1.3, size, leading=size * 1.35)
    return top + title_h + 1.3 + body_h + 4


def entity(prefix):
    matches = [e for e in b.TRIP['entities'] if e['title'].startswith(prefix)]
    assert len(matches) == 1, f'Entity changed: {prefix}'
    return matches[0]


def source_row(d, index, expected, body=None, kind='place', record=True):
    r = d['timeline'][index]
    assert expected in r['text'], f"Review changed source: {d['date']} row {index}"
    if record:
        PROVENANCE.append({'date': d['date'], 'indices': [index], 'time': r['time']})
    return r['time'], body or r['text'], kind


def merged(d, first, last, expected_first, expected_last, body, kind='place'):
    a = source_row(d, first, expected_first, record=False)
    z = source_row(d, last, expected_last, record=False)
    t = b.range_time(a[0], z[0])
    PROVENANCE.append({'date': d['date'], 'indices': list(range(first, last + 1)), 'time': t})
    return t, body, kind


def overview(c):
    header(c, 'EIGHT DAYS / ONE LITTLE JOURNAL', '八天，一路慢慢走', '2026.08.27 - 09.03 / 前四天同行，後四天 Wei')
    names = ['抵達福岡・博多', '太宰府・LaLaport', '由布院・金鱗湖', '博多・天神',
             '小倉・門司港・皿倉山', '上色見・高千穗', '糸島・櫻井二見浦', '咖啡・採買・返台']
    for i, (d, name) in enumerate(zip(b.TRIP['days'], names)):
        y = 42 + i * 9.3
        p(c, d['date'][5:].replace('-', '/'), y + .5, 8.5, width=16, font='Arial', color=b.TEAL)
        p(c, name, y, 10, x=27, width=62, color=b.INK)
        p(c, str(6 + 2 * i).zfill(2), y + .5, 8, x=91, width=6, font='Arial', color=b.MUTED)
        b.line(c, 27 * mm, (y + 7) * mm, 70 * mm)
    p(c, '住宿 04-05　行李 22　採買 23', 121, 8.5, color=b.INK)
    p(c, '實心點與淺綠底：交通／已訂班次與餐廳。<br/>其餘時間是規劃節奏，可依現場調整。',
      127, 8, color=b.MUTED, leading=10)
    end(c, '八天總覽')


def flights(c):
    header(c, 'FLIGHTS / EVA AIR', '出發，與回家的路', '時間依原筆記；台灣與日本皆為當地時間。')
    segments = entity('台北福岡來回機票')['segments']
    for i, s in enumerate(segments):
        y = 42 + i * 27
        dt, flight, schedule = s['time']['text'].split(' ', 2)
        p(c, dt + ' / ' + s['label'], y, 9, color=b.TEAL)
        p(c, flight + '   ' + schedule, y + 6, 14, font='Arial', color=b.INK)
        p(c, escape(s['route']['text']), y + 13, 10)
        p(c, '託運 ' + ('1 件' if i == 0 else '2 件') + '，每件 23 kg；手提 1 件 7 kg。',
          y + 19, 8.5, color=b.MUTED)
        b.line(c, 8 * mm, (y + 25) * mm, 89 * mm)
    p(c, '去程 12:00 出發去桃園 T2。<br/>Wei 回程 17:00 從飯店出發去國際線。', 126, 8.5, leading=11, color=b.INK)
    end(c, '航班')


def hotels(c):
    a = entity('西鐵 CROOM 飯店 博多祇園 櫛田神社前｜8/27')
    a2 = entity('西鐵 CROOM 飯店 博多祇園 櫛田神社前｜8/31')
    x = entity('CROSS Life 博多天神')
    header(c, 'STAY / HAKATA GION', '西鐵 CROOM', '博多祇園 櫛田神社前 / 8.27 - 9.01')
    b.photo(c, 'croom.jpg', 8 * mm, 41 * mm, 89 * mm, 32 * mm, focus=(.5, .66))
    b.credit(c, 'croom.jpg', 8 * mm, 75 * mm, 89 * mm)
    p(c, '8/27-8/31　4 人 / 4 晚', 82, 10, font='TCM', color=b.INK)
    p(c, escape(a['room']['text']), 88, 9)
    p(c, '8/31-9/1　Wei / 1 晚', 95, 10, font='TCM', color=b.INK)
    p(c, escape(a2['room']['text']) + '；早上先問能否同房續住。', 101, 9)
    p(c, '入住 ' + a['checkIn']['text'] + ' / 退房 ' + a['checkOut']['text'], 112, 9, color=b.TEAL)
    p(c, escape(a['access']['text']), 119, 9)
    p(c, '6-30 Gionmachi, Hakata-ku<br/>+81-92-235-5050', 130, 8, leading=9.5, color=b.MUTED)
    end(c, '住宿・西鐵 CROOM')
    header(c, 'STAY / HAKATA TENJIN', 'CROSS Life', '博多天神 / 9.01 - 9.03')
    b.photo(c, 'cross.jpeg', 8 * mm, 41 * mm, 34 * mm, 46 * mm)
    p(c, 'Wei / 2 晚', 42, 10, x=48, width=49, font='TCM', color=b.INK)
    p(c, escape(x['room']['text']), 49, 9.5, x=48, width=49)
    p(c, '入住 15:00 後<br/>退房 11:00', 69, 9.5, x=48, width=49, color=b.TEAL)
    b.credit(c, 'cross.jpeg', 8 * mm, 89 * mm, 89 * mm)
    y = note(c, '回飯店的路', x['access']['text'], 97, size=9.5)
    p(c, '3-26-30 Haruyoshi, Chuo-ku<br/>+81-92-733-0130', y, 8.5, leading=10.5, color=b.MUTED)
    p(c, '9/1 早上用博多站置物櫃；晚間取行李入住。<br/>9/3 退房寄物，16:10 回飯店領行李。', 127, 8.5, leading=11)
    end(c, '住宿・CROSS Life')


def photo_notes(c, title, kicker, image, caption, notes, focus=(.5, .5), height=48):
    b.start(c)
    b.label(c, kicker, 10 * mm, 9 * mm, 6.5, tracking=.55)
    p(c, title, 15, 16, x=10, width=87, font='TCM', color=b.INK)
    b.photo(c, image, 10 * mm, 27 * mm, 87 * mm, height * mm, focus=focus)
    y = 27 + height
    p(c, caption, y + 2, 10, x=10, width=87, font='TCM', color=b.INK)
    b.credit(c, image, 10 * mm, (y + 8) * mm, 87 * mm)
    y += 16
    for title, text in notes:
        y = note(c, title, text, y, size=9.5)
    assert y - 4 <= 136, f'Notes overflow page {b.PAGE}: {y}'
    end(c, caption + '・提醒')


def days(c):
    d = b.day('2026-08-27')
    rows = [source_row(d, 0, '桃園', '前往桃園機場 T2', 'move'),
            source_row(d, 1, 'BR102', 'BR102 TPE → FUK', 'confirmed'),
            source_row(d, 2, '入境', '入境 / 領行李', 'buffer'),
            source_row(d, 3, '飯店', '國際線搭計程車 → CROOM', 'move'),
            source_row(d, 4, 'Check', '入住 / 放行李 / 前往大東園', 'buffer'),
            source_row(d, 5, '大東園', '大東園 本店 / 燒肉', 'confirmed')]
    b.timeline(c, d, 1, 'ARRIVAL', '抵達福岡，先吃一餐', rows, 6)
    photo_notes(c, '從博多開始的夜晚', 'ARRIVAL / A WARM FIRST EVENING', 'canal.jpg', '博多運河城', [
        ('20:00 大東園已訂位', '4 人。若出關延誤，先聯絡店家；機場到飯店以計程車最穩。'),
        ('第一晚，留一點餘裕', '運河城商店到 21:00、餐廳到 23:00。飯後超商補給，回飯店休息。')])
    d = b.day('2026-08-28')
    rows = [source_row(d, 0, 'パン', 'パンとエスプレッソと / 早餐', 'food'),
            source_row(d, 1, '太宰府', '七隈線 / 西鐵 → 太宰府', 'move'),
            source_row(d, 2, '星巴克', '參道散步 / 星巴克', 'place'),
            source_row(d, 3, '博物館', kind='place'),
            source_row(d, 4, '天滿宮', kind='place'),
            source_row(d, 5, '午餐', '一蘭 / 參道午餐 / 梅枝餅', 'food'),
            source_row(d, 7, 'LaLaport', '西鐵轉 JR → LaLaport', 'move'),
            source_row(d, 8, '鋼彈', 'LaLaport / 鋼彈 / SIDE-F', 'shopping'),
            source_row(d, 9, '前田屋', '竹下 → 博多 / 前田屋', 'move'),
            source_row(d, 10, '前田屋', '前田屋 博多店 / 牛腸鍋', 'confirmed')]
    b.timeline(c, d, 2, 'DAZAIFU', '太宰府，到鋼彈腳下', rows, 8)
    photo_notes(c, '晨光裡的鳥居', 'SHRINE / MUSEUM / GUNDAM', 'dazaifu-grounds.jpg', '太宰府天滿宮', [
        ('去程，轉車記這條', '櫛田神社前 → 薬院 → 西鉄二日市 → 太宰府。往 JR 二日市要步行轉站。'),
        ('18:00 演出，19:30 晚餐', '18:35 前離開 LaLaport。前田屋已訂 4 人；光明禪寺只當現場開放的備案。')], focus=(.5, .76))
    d = b.day('2026-08-29')
    rows = [source_row(d, 0, '早餐', '博多站集合 / 買車上早餐', 'buffer'),
            source_row(d, 1, 'Yufu 1', 'Yufu 1 → 由布院', 'confirmed'),
            source_row(d, 3, '湯之坪', '湯之坪街道散步'),
            source_row(d, 4, '金鱗湖'),
            source_row(d, 5, '花野', '花野そば / 午餐備案', 'food'),
            source_row(d, 6, 'FLORAL', '湯之坪 / FLORAL VILLAGE', 'shopping'),
            source_row(d, 7, '咖啡', '車站周邊咖啡 / 伴手禮', 'buffer'),
            source_row(d, 8, '回由布院', '回車站 / 預留候車時間', 'buffer'),
            source_row(d, 9, 'Mori 6', '由布院之森 6 → 博多', 'confirmed'),
            source_row(d, 10, '屋台', '中洲屋台 / 回飯店休息', 'food')]
    b.timeline(c, d, 3, 'YUFUIN', '由布院，山與湖之間', rows, 10)
    artwork.yufu_photos(c)
    d = b.day('2026-08-30')
    rows = [source_row(d, 0, 'FUK', 'FUK COFFEE / 慢慢開始', 'food'),
            source_row(d, 1, '櫛田'), source_row(d, 2, '川端'),
            source_row(d, 3, '一双', '博多一双 祇園店 / 午餐', 'food'),
            source_row(d, 4, 'FULL', 'FULL FULL / 外帶點心', 'food'),
            source_row(d, 5, '天神', '地下鐵 → 天神', 'move'),
            source_row(d, 6, '地下街', '天神地下街 / 逛街', 'shopping'),
            source_row(d, 7, '警固', '警固神社 / Blue Bottle', 'place'),
            source_row(d, 8, '鳥田', '地下鐵 / 步行 → 鳥田', 'move'),
            source_row(d, 9, '鳥田', '鳥田 博多本店 / 水炊雞鍋', 'confirmed')]
    b.timeline(c, d, 4, 'HAKATA / TENJIN', '把一天留給城市', rows, 12)
    photo_notes(c, '街角、神社與咖啡', 'COFFEE / LOCAL STREETS / SHOPPING', 'kushida.jpg', '櫛田神社', [
        ('今天可以慢一點', '前兩天太累，上午可延到 10:30。飯店周邊步行，午後搭地下鐵去天神。'),
        ('19:30 鳥田已訂位', '4 人，博多套餐。18:30 從天神出發，地鐵到中洲川端再步行。')])
    d = b.day('2026-08-31')
    rows = [merged(d, 0, 1, '三人組', 'checkout', '三人組返台；Wei 退房寄行李', 'buffer'),
            source_row(d, 2, '小倉', '新幹線前往小倉', 'move'),
            source_row(d, 3, '小倉城'), source_row(d, 5, '門司港', 'JR 前往門司港', 'move'),
            source_row(d, 6, '伽哩', '伽哩本舖 / 燒咖哩午餐', 'food'),
            merged(d, 7, 9, '復古', '吊橋', '復古區 → 舊海關 → 藍翼吊橋'),
            merged(d, 10, 11, '皿倉', '接駁', 'JR / 接駁 / 纜車上皿倉山', 'move'),
            source_row(d, 12, '夜景', '皿倉山日落與夜景'),
            source_row(d, 13, '下山', '下山 / 回博多', 'move'),
            source_row(d, 14, '飯店', '飯店入住 / 領行李', 'rest')]
    b.timeline(c, d, 5, 'KITAKYUSHU', '小倉、門司港與夜景', rows, 14)
    artwork.kitakyushu_photos(c)
    d = b.day('2026-09-01')
    rows = [source_row(d, 0, 'checkout', 'CROOM 退房 → 博多站', 'move'),
            source_row(d, 1, '寄行李', '置物櫃 / 買早餐與水', 'buffer'),
            source_row(d, 3, 'LAWSON', '筑紫口 / LAWSON 前集合', 'confirmed'),
            source_row(d, 4, '上色見', '一日團巴士 → 上色見', 'confirmed'),
            source_row(d, 5, '神社', '上色見熊野座神社'),
            source_row(d, 7, '高千穗', '高千穗峽 / 千穂の家午餐', 'place'),
            source_row(d, 8, '天岩戶', '天岩戶神社 / 天安河原'),
            source_row(d, 9, '返回', '一日團巴士 → 博多', 'move'),
            merged(d, 10, 11, '領行李', 'check in', '領行李 / CROSS Life 入住', 'rest'),
            source_row(d, 12, '兼虎', '兼虎 博多 Deitos / 沾麵', 'food')]
    b.timeline(c, d, 6, 'TAKACHIHO', '山林深處的一天', rows, 16)
    photo_notes(c, '沿著峽谷走一段', 'FOREST / GORGE / WATERFALL', 'takachiho.jpg', '高千穗峽・真名井瀑布', [
        ('07:40 前到集合點', 'Oriental Hotel 1F LAWSON 前，07:50 集合、08:00 出發。前晚看最新導遊通知。'),
        ('不划船，也不含午餐', '重點是瀑布觀景台與遊步道。無餐廳接駁，留時間走回停車場；回程延誤就簡單吃。')], height=45)
    d = b.day('2026-09-02')
    rows = [source_row(d, 1, '下山門', '天神 → 下山門', 'move'),
            source_row(d, 2, '壱岐', '壱岐神社 / 之後回車站'),
            source_row(d, 4, '筑前', 'JR → 筑前前原', 'move'),
            source_row(d, 5, '箱島', '北口計程車 → 箱島神社', 'move'),
            source_row(d, 6, '箱島'),
            source_row(d, 7, '塚本', '計程車 → 塚本鮮魚店', 'move'),
            source_row(d, 8, '鮮魚', '塚本鮮魚店 本店 / 午餐', 'food'),
            source_row(d, 9, '二見浦', '計程車 → 櫻井二見浦', 'move'),
            merged(d, 10, 11, '二見浦', '咖啡', '夫婦岩 / 海邊咖啡 / 回程緩衝'),
            source_row(d, 12, '巴士', '昭和西海岸巴士 → 市區', 'confirmed'),
            source_row(d, 13, '晚餐', '市區晚餐 / 彈性決定', 'food')]
    b.timeline(c, d, 7, 'ITOSHIMA', '把午後留在海邊', rows, 18)
    photo_notes(c, '海風裡，慢慢散步', 'SEA / TORII / A LONG AFTERNOON', 'futamigaura.png', '櫻井二見浦・夫婦岩', [
        ('先確認計程車', '9/1 前預約箱島、塚本、二見浦移動。不要從一貴山硬走去箱島。'),
        ('16:32 從 PALMBEACH 前回程', '昭和巴士；17:32 候補、18:37 末班。舊夫婦岩前站已廢止；看完夕陽要改計程車轉 JR。')], focus=(.55, .5), height=45)
    d = b.day('2026-09-03')
    rows = [source_row(d, 0, 'checkout', 'CROSS Life 退房 / 寄行李', 'buffer'),
            source_row(d, 1, 'REC', 'REC COFFEE 薬院駅前', 'food'),
            source_row(d, 2, 'COUNTY', 'COFFEE COUNTY', 'food'),
            source_row(d, 3, '購物', '天神購物 / 衣服 / 雜貨', 'shopping'),
            source_row(d, 4, '明太', '明太重 / 午餐備案', 'food'),
            source_row(d, 5, '博多', '移動到博多站', 'move'),
            merged(d, 6, 7, 'FUGLEN', '伴手禮', 'FUGLEN 可選 / Ming / 伴手禮', 'shopping'),
            source_row(d, 8, '行李', 'CROSS Life 領行李', 'buffer'),
            source_row(d, 9, '機場', '計程車 → 福岡國際線', 'confirmed'),
            source_row(d, 10, 'BR101', 'BR101 FUK → TPE', 'confirmed')]
    b.timeline(c, d, 8, 'COFFEE / HOME', '最後一杯，然後回家', rows, 20)
    photo_notes(c, '把福岡裝進行李', 'COFFEE / SOUVENIRS / HOME', 'county.jpg', 'COFFEE COUNTY Fukuoka', [
        ('咖啡不用三間都喝', 'REC、COUNTY、FUGLEN 可刪一間。明太重排太長，改天神地下街或 PARCO 午餐。'),
        ('16:10 收尾，17:00 出發', 'Ming / Deitos 買伴手禮，機場保底。先回飯店拿行李；18:00 前到國際線。')], height=45)


def checklist(c, key, title, kicker, combinations, captions=None):
    header(c, kicker, title, '紙上勾選，帶走需要的；完整清單也在網站。')
    y = 40
    for group_index, (group, combine) in enumerate(zip(b.TRIP['checklists'][key], combinations)):
        name = group['title'].split('｜')[-1]
        p(c, escape(name), y, 10, font='TCM', color=b.TEAL)
        y += 5.2
        for row_index, indices in enumerate(combine):
            text = ' / '.join(group['items'][i]['content']['text'] for i in indices)
            if captions:
                text = captions[group_index][row_index]
            c.setStrokeColor(b.TEAL)
            c.setLineWidth(.65)
            c.rect(8.5 * mm, H - (y + 3.2) * mm, 2.5 * mm, 2.5 * mm, stroke=1, fill=0)
            h = p(c, escape(text), y, 9.5, x=14, width=83, leading=11.6)
            y += max(h, 4.1) + .35
        y += 1.2
    assert y < 136, f'Checklist overflow: {y}'
    end(c, title)


def back(c):
    b.start(c)
    b.label(c, "WEI'S TRAVEL JOURNAL", 10 * mm, 14 * mm, 7, b.INK)
    p(c, 'Until the next trip.', 26, 24, x=10, width=85, font='Baskerville', color=b.INK)
    p(c, '把路上的片刻，留在手帖裡。', 51, 12, x=10, width=85, color=b.INK)
    b.line(c, 10 * mm, 69 * mm, 85 * mm)
    qr = QrCodeWidget(WEB, barLevel='M')
    qx, qy, qr_w, qr_h = qr.getBounds()
    qr_w -= qx
    qr_h -= qy
    size = 30 * mm
    drawing = Drawing(size, size, transform=[size / qr_w, 0, 0, size / qr_h, -qx, -qy])
    drawing.add(qr)
    renderPDF.draw(drawing, c, 8 * mm, H - 108 * mm)
    p(c, '線上旅行手帖', 82, 10, x=45, width=52, font='TCM', color=b.TEAL)
    p(c, '地圖連結、詳細資訊<br/>與可勾選的完整清單。', 89, 9.5, x=45, width=52)
    p(c, 'travel.weiweifan.com<br/>/fukuoka-2026/', 101, 8, x=45, width=52, font='Arial', leading=10, color=b.MUTED)
    c.linkURL(WEB, (8 * mm, H - 111 * mm, 97 * mm, H - 78 * mm))
    p(c, '依 2026.08.27-09.03 原筆記規劃整理。<br/>行程可能調整；現場以營運與訂位通知為準。', 115, 8.5, leading=11, color=b.MUTED)
    p(c, '照片來源見各頁標示，電子版可點擊。<br/>來源網站保留原著作權；本冊供個人旅行使用。', 126, 7.5, leading=10, color=b.MUTED)
    end(c, '封底')


def render(plan):
    global WEB
    WEB = plan['webUrl']
    PROVENANCE.clear()
    assert len(b.TRIP['days']) == 8 and all(d['publish'] == 'full' for d in b.TRIP['days'])
    b.OUT.mkdir(parents=True, exist_ok=True)
    source = b.OUT / plan['outputs']['reading']
    c = canvas.Canvas(str(source), pagesize=(W, H), pageCompression=1)
    c.setTitle('福岡旅行手帖 | A6 完整 24 頁')
    c.setAuthor('Wei')
    artwork.cover(c)
    overview(c)
    flights(c)
    hotels(c)
    days(c)
    checklist(c, 'packing', '出發前，逐項確認', 'PACKING / THE ESSENTIALS', [
        [[0], [1, 2], [3], [4, 5]], [[0, 1], [2, 3], [4, 5], [6]],
        [[0, 1], [2, 3, 4], [5], [6, 7]], [[0, 1, 2], [3], [4]]], captions=[
        ['護照', '信用卡 / 日幣現金', '交通 IC / Apple Wallet', '保險資訊 / 住宿、機票、JR、Klook 離線憑證'],
        ['上衣 / 褲子', '內衣褲 / 襪子 / 睡衣', '輕便外套 / 好走的鞋', '雨具'],
        ['iPhone / Apple Watch / AirPods', '充電器 / 行動電源 / 轉接頭', 'eSIM / 網路設定', 'Pocket 3 / 相機 / SD 卡 / 讀卡機'],
        ['常備藥 / 腸胃藥 / 止痛藥', '防曬', '口罩 / 濕紙巾']])
    checklist(c, 'shopping', '帶一點福岡回家', 'TO BUY / SMALL THINGS TO TAKE HOME', [
        [[0], [1, 2], [3, 4]], [[0], [1], [2, 3]], [[0, 1], [2]],
        [[0], [1, 2]], [[0, 1, 2]]])
    back(c)
    assert b.PAGE == plan['pageCount']
    c.save()
    return {'source_hash': b.TRIP['sourceHash'], 'text_boxes': b.BOXES, 'photos': b.IMAGE_QA,
            'timeline_sources': PROVENANCE}
