"""Download licensed illustrative photography and create local responsive WebP assets."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
import json
import requests
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist/assets/photos'
OUT.mkdir(exist_ok=True)
PHOTOS = [
    ('porsche', 'photo-1593353798398-6024b7444bb6', 'https://images.unsplash.com/photo-1593353798398-6024b7444bb6', 'Silver Porsche 911; illustrative vehicle photography'),
    ('bmw', 'photo-1647966008754-814349917adf', 'https://unsplash.com/photos/Hcg0hqn4SbU', 'Tim Vegas; black BMW 3 Series; illustrative vehicle photography'),
    ('mercedes-benz', 'photo-1605294338126-390cec44062d', 'https://unsplash.com/photos/L9W-qoRGvBk', 'Alberto Frias; white Mercedes-Benz C-Class; illustrative vehicle photography'),
]

def prepare(photo):
    name, photo_id, source, description = photo
    url = f'https://images.unsplash.com/{photo_id}?auto=format&fit=max&w=2200&q=88'
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    original = ImageOps.exif_transpose(Image.open(BytesIO(response.content))).convert('RGB')
    outputs = []
    for width in (640, 1280, 1920):
        image = original.copy()
        image.thumbnail((width, width * 2))
        path = OUT / f'{name}-{width}.webp'
        image.save(path, 'WEBP', quality=82, method=6)
        outputs.append({'file': path.relative_to(ROOT).as_posix(), 'width': image.width, 'height': image.height, 'bytes': path.stat().st_size})
    print(name, original.size, sum(item['bytes'] for item in outputs))
    return {'name': name, 'source': source, 'download': url, 'license': 'https://unsplash.com/license', 'usage': description, 'files': outputs}

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(prepare, PHOTOS))
    (ROOT / 'photography-sources.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    sheet = Image.new('RGB', (1000, 740), '#f3f1eb')
    for index, record in enumerate(records):
        im = Image.open(ROOT / record['files'][1]['file'])
        sheet.paste(ImageOps.fit(im, (490, 360)), ((index % 2) * 500, (index // 2) * 370))
    sheet.save(ROOT.parent / 'houstonauto-photo-contact-sheet.jpg')
