"""Self-host pinned manufacturer identification marks and preserve source notices."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote
import json
import re
import xml.etree.ElementTree as ET
import requests

ROOT = Path(__file__).resolve().parents[1]
REVISION = '05c4001e83a09a189721a0851546291f71f7e31c'
BASE = f'https://raw.githubusercontent.com/cardog-ai/icons/{REVISION}/core/'
SOURCE_NAMES = {'Mercedes-Benz': 'MB', 'MINI': 'Mini', 'Land Rover': 'Landrover', 'Rolls-Royce': 'Rolls Royce'}

def download(make):
    slug = re.sub(r'[^a-z0-9]+', '-', make.lower())
    filename = f"{SOURCE_NAMES.get(make, make)} Icon.svg"
    url = BASE + 'optimized/' + quote(filename)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    if root.tag.split('}')[-1] != 'svg': raise ValueError(f'Not SVG: {make}')
    for element in root.iter():
        if element.tag.split('}')[-1] in {'script', 'foreignObject', 'image'}: raise ValueError(f'Unexpected SVG content: {make}')
        for attribute, value in element.attrib.items():
            if attribute.lower().startswith('on') or (attribute.split('}')[-1] == 'href' and not value.startswith('#')):
                raise ValueError(f'Unexpected SVG reference: {make}')
    asset = f'dist/assets/brands/{slug}-mark.svg'
    (ROOT / asset).write_bytes(response.content)
    return {'brand': slug, 'asset': asset, 'source': url, 'license': BASE + 'LICENSE',
            'usage': 'Manufacturer identification in the make gallery and menu; no affiliation implied.'}

if __name__ == '__main__':
    makes = json.loads((ROOT / 'content/makes.json').read_text(encoding='utf-8'))
    makes = [make for make in makes if make != 'Other European make']
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(download, makes))
    license_response = requests.get(BASE + 'LICENSE', timeout=30)
    license_response.raise_for_status()
    (ROOT / 'dist/assets/brands/CARDOG-LICENSE.txt').write_bytes(license_response.content)
    source_file = ROOT / 'brand-sources.json'
    old = json.loads(source_file.read_text(encoding='utf-8'))
    old = [record for record in old if record.get('usage') != records[0]['usage']]
    source_file.write_text(json.dumps(old + records, indent=2) + '\n', encoding='utf-8')
    print(f'Saved {len(records)} manufacturer marks and source/license notices.')
