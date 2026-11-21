import os
import urllib.request
import urllib.parse
import json
from concurrent.futures import ThreadPoolExecutor

os.makedirs('assets/avatars', exist_ok=True)

api_url = 'https://api.github.com/repos/bluejoe2008/InteractiveGraph/contents/dist/examples/images/photo'
req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as resp:
    files = json.loads(resp.read().decode('utf-8'))

print(f"Total files to check/download: {len(files)}")

def download_file(item):
    filename = item['name']
    target_path = os.path.join('assets', 'avatars', filename)
    if os.path.exists(target_path) and os.path.getsize(target_path) > 100:
        return f"Skip: {filename}"
    
    encoded_name = urllib.parse.quote(filename)
    raw_url = f"https://raw.githubusercontent.com/bluejoe2008/InteractiveGraph/master/dist/examples/images/photo/{encoded_name}"
    try:
        r = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(r, timeout=15) as res:
            data = res.read()
            with open(target_path, 'wb') as f:
                f.write(data)
        return f"OK: {filename} ({len(data)} bytes)"
    except Exception as e:
        return f"ERR: {filename} -> {e}"

with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(download_file, files))

success = sum(1 for r in results if r.startswith('OK') or r.startswith('Skip'))
print(f"Downloaded/Verified {success}/{len(files)} avatars.")
if success < len(files):
    for r in results:
        if r.startswith('ERR'):
            print(r)
