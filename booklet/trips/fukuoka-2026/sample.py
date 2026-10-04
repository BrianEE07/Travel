"""Historical five-page Fukuoka design sample."""
from layout import *
from artwork import cover, yufu_photos, kitakyushu_photos

def make_sample():
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / 'fukuoka-a6-sample.pdf'
    c = canvas.Canvas(str(output), pagesize=(W, H), pageCompression=1)
    c.setTitle('福岡旅行手帖 | A6 設計樣張')
    c.setAuthor('Wei')
    cover(c)
    d = day('2026-08-29')
    t = d['timeline']
    timeline(c, d, 3, 'YUFUIN', '由布院，山與湖之間', [
        (t[0]['time'], '博多站集合 / 買早餐', 'buffer'),
        (t[1]['time'], 'Yufu 1 → 由布院', 'confirmed'),
        (t[3]['time'], '湯之坪街道散步', 'place'),
        (t[4]['time'], '金鱗湖', 'place'),
        (t[5]['time'], '花野そば / 午餐備案', 'food'),
        (t[6]['time'], '湯之坪 / FLORAL VILLAGE', 'shopping'),
        (t[7]['time'], '車站周邊咖啡 / 伴手禮', 'buffer'),
        (t[8]['time'], '回車站 / 預留候車時間', 'buffer'),
        (t[9]['time'], '由布院之森 6 → 博多', 'confirmed'),
        (t[10]['time'], '中洲屋台 / 回飯店休息', 'food'),
    ], 10)
    yufu_photos(c)
    d = day('2026-08-31')
    t = d['timeline']
    timeline(c, d, 5, 'KITAKYUSHU', '小倉、門司港與夜景', [
        (range_time(t[0]['time'], t[1]['time']), '三人組返台；Wei 退房寄行李', 'buffer'),
        (t[2]['time'], '新幹線前往小倉', 'move'),
        (t[3]['time'], '小倉城', 'place'),
        (t[5]['time'], 'JR 前往門司港', 'move'),
        (t[6]['time'], '伽哩本舖 / 燒咖哩午餐', 'food'),
        (range_time(t[7]['time'], t[9]['time']), '復古區 → 舊海關 → 藍翼吊橋', 'place'),
        (range_time(t[10]['time'], t[11]['time']), 'JR / 接駁 / 纜車上皿倉山', 'move'),
        (t[12]['time'], '皿倉山日落與夜景', 'place'),
        (t[13]['time'], '下山 / 回博多', 'move'),
        (t[14]['time'], '飯店入住 / 領行李', 'rest'),
    ], 14)
    kitakyushu_photos(c)
    c.save()
    reader = PdfReader(output)
    assert len(reader.pages) == 5
    # The spread view is for review only: cover centred, then genuine facing pairs.
    writer = PdfWriter()
    spread = writer.add_blank_page(width=2 * W, height=H)
    spread.merge_transformed_page(reader.pages[0], Transformation().translate(tx=W / 2))
    for left, right in [(1, 2), (3, 4)]:
        spread = writer.add_blank_page(width=2 * W, height=H)
        spread.merge_page(reader.pages[left])
        spread.merge_transformed_page(reader.pages[right], Transformation().translate(tx=W))
    writer.add_metadata({'/Title': '福岡旅行手帖 | 左右跨頁樣張', '/Author': 'Wei'})
    writer.write(OUT / 'fukuoka-sample-spreads.pdf')
    (TMP / 'layout-qa.json').write_text(json.dumps({'text_boxes': BOXES, 'photos': IMAGE_QA}, ensure_ascii=False, indent=2))
    print(f'Created {output.name}: 5 pages, 105 × 148 mm; spread preview: 3 pages')
    print('Photo effective DPI:', ', '.join(f"{i['file']}={i['effective_dpi']}" for i in IMAGE_QA))


if __name__ == '__main__':
    make_sample()
