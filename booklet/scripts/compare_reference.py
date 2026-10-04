"""Pixel comparison against an approved rendered reference; contact sheet for QA."""
import argparse
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument('--directory', type=Path, required=True)
parser.add_argument('--count', type=int, required=True)
args = parser.parse_args()
images = []
for page in range(1, args.count + 1):
    # Poppler zero-pads according to total page count.
    index = str(page).zfill(len(str(args.count)))
    current = Image.open(args.directory / f'reading-{index}.png').convert('RGB')
    reference = Image.open(args.directory / f'reference-{index}.png').convert('RGB')
    if current.size != reference.size or ImageChops.difference(current, reference).getbbox():
        raise ValueError(f'Layout changed from approved reference on page {page}; inspect before approval.')
    current.thumbnail((210, 296))
    images.append(current.copy())
sheet = Image.new('RGB', (6 * 230, ((args.count + 5) // 6) * 325), '#e7e7e7')
draw = ImageDraw.Draw(sheet)
for index, picture in enumerate(images):
    x, y = (index % 6) * 230 + 10, (index // 6) * 325 + 8
    sheet.paste(picture, (x, y))
    draw.text((x, y + 299), f'{index + 1:02d}', fill='#173e56')
sheet.save(args.directory / 'reading-contact.png')
print(f'PASS: all {args.count} pages pixel-identical to approved reference; contact sheet ready.')
