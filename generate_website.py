#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IoTConnect Hardware & Demo Catalog site generator (cleaned)f
- No in-code descriptions. All demo text comes from the spreadsheet.
- Catalog source can be SharePoint (public link or Graph) or local XLSX.
- Manufacturer shown above title, strong tile separation, case-insensitive search,
  lightbox image viewer, manufacturer filter, tags, team inventory (KK,ML,NM,SD,SL,ZA).
"""
import os
import io
import re
import sys
import base64
from pathlib import Path

import pandas as pd
import requests

# ---------- Paths ----------
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_FILE = SCRIPT_DIR / "Board Catalog3.xlsx"
OUTPUT_DIR = SCRIPT_DIR / "website"

# ---------- SharePoint / Graph helpers ----------
def _try_direct_download(url: str) -> bytes | None:
    if not url:
        return None
    dl = url
    dl += ("&" if "?" in dl else "?") + "download=1" if "download=" not in dl else ""
    try:
        r = requests.get(dl, allow_redirects=True, timeout=60)
        if r.ok:
            ct = r.headers.get("content-type", "")
            if r.content[:2] == b"PK" or "spreadsheetml.sheet" in ct:
                print("[catalog] downloaded via direct link")
                return r.content
    except Exception as e:
        print(f"[catalog] direct download failed: {e}")
    return None

def _download_via_graph(shared_link: str) -> bytes | None:
    tenant = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    if not (tenant and client_id and client_secret and shared_link):
        return None
    try:
        token_r = requests.post(
            f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials",
            },
            timeout=60,
        )
        token_r.raise_for_status()
        token = token_r.json()["access_token"]
        encoded = base64.urlsafe_b64encode(shared_link.encode("utf-8")).decode("utf-8").rstrip("=")
        url = f"https://graph.microsoft.com/v1.0/shares/u!{encoded}/driveItem/content"
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=60)
        r.raise_for_status()
        print("[catalog] downloaded via Microsoft Graph")
        return r.content
    except Exception as e:
        print(f"[catalog] graph download failed: {e}")
        return None

def get_catalog_bytes() -> bytes | None:
    shared_url = os.getenv("CATALOG_XLSX_URL") or os.getenv("GRAPH_SHARED_LINK")
    if shared_url:
        b = _try_direct_download(shared_url)
        if b: return b
        b = _download_via_graph(shared_url)
        if b: return b
    if DEFAULT_DATA_FILE.exists():
        print(f"[catalog] using local file: {DEFAULT_DATA_FILE}")
        return DEFAULT_DATA_FILE.read_bytes()
    print("[catalog] ERROR: no catalog source available")
    return None

# ---------- Robust header normalization ----------
def _norm(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', str(s).strip().lower())

_INV_ALIAS = {
    'Manufacturer': {'manufacturer', 'mfr'},
    'Common Name': {'commonname', 'name', 'boardname', 'title'},
    'Partnumber':  {'partnumber', 'partnum', 'partno', 'partnumb', 'pn', 'mpn'},
    'Link':        {'link', 'productlink', 'buy', 'producturl'},
    'Image':       {'image', 'boardimage', 'imageurl'},
    'URL':         {'url', 'producturl', 'weburl'},
    'GithubIndex': {'ingithubindex', 'githubindex', 'github', 'githublink', 'ingithubi'},
}
TEAM_INITIALS = ['KK','ML','NM','SD','SL','ZA']

def _normalize_inventory_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for c in df.columns:
        key = _norm(c)
        for target, keys in _INV_ALIAS.items():
            if key in keys:
                rename[c] = target
                break
    df = df.rename(columns=rename)
    if 'In Github index' in df.columns and 'GithubIndex' not in df.columns:
        df = df.rename(columns={'In Github index': 'GithubIndex'})
    return df

# ---------- Load data ----------
def load_data():
    raw = get_catalog_bytes()
    if raw is None:
        print("FATAL: could not resolve catalog source.")
        sys.exit(2)

    xl = pd.ExcelFile(io.BytesIO(raw))

    # Inventory (detect header row)
    inv_raw = xl.parse('Inventory', header=None)
    header_idx = None
    for i in range(min(10, len(inv_raw))):
        if str(inv_raw.iloc[i, 0]).strip().lower() == 'manufacturer':
            header_idx = i
            break
    if header_idx is not None:
        header = inv_raw.iloc[header_idx].fillna('').map(lambda x: str(x).strip())
        inv_df = inv_raw.iloc[header_idx + 1:].copy()
        inv_df.columns = [str(c).strip() for c in header]
    else:
        inv_df = xl.parse('Inventory')

    inv_df = _normalize_inventory_columns(inv_df)
    inv_df = inv_df.fillna('').applymap(lambda x: x.strip() if isinstance(x, str) else x)
    if 'Manufacturer' in inv_df.columns:
        inv_df = inv_df[inv_df['Manufacturer'].str.lower() != 'manufacturer']

    demos_df = xl.parse('Demos').fillna('')

    return inv_df, demos_df

# ---------- HTML helpers ----------
def generate_nav(current_page: str) -> str:
    links = {'index.html':'Home','inventory.html':'Inventory','demos.html':'Demos'}
    nav_items = []
    for page, name in links.items():
        style = ' style="text-decoration:underline"' if page == current_page else ''
        nav_items.append(f'<a href="{page}"{style}>{name}</a>')
    logo_html = ''
    if (SCRIPT_DIR / 'iotconnect_logo.png').exists():
        logo_html = '<img src="iotconnect_logo.png" alt="IoTConnect logo" class="logo">'
    return f'''<nav><div class="container">{logo_html}{' '.join(nav_items)}</div></nav>'''

def write_file(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

# ---------- CSS ----------
STYLE_CSS = """
body {
  font-family: Arial, sans-serif;
  margin: 0; padding: 0;
  background-color: #eef3f8; color: #333;
}
nav { background-color: #1a2a3a; padding: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
nav .container { display: flex; align-items: center; gap: 16px; width: 92%; margin: 0 auto; }
nav a { color: #fff; margin-right: 18px; }
nav a:hover { text-decoration: underline; }
.logo { width: 160px; height: 28px; object-fit: contain; }

.container { width: 92%; margin: 18px auto 24px; }
.controls { display: flex; gap: 12px; align-items: center; margin: 12px 0 18px; }
.controls input[type="text"] { padding: 6px 10px; font-size: 14px; }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px,1fr)); gap: 28px; }

.card {
  border: 1px solid #ccd7e0; border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.08);
  padding: 15px; display: flex; flex-direction: column; background: #fff;
}
.card h2 { font-size: 18px; margin: 0 0 10px 0; background: #1a2a3a; color: #fff; padding: 6px 8px; border-radius: 4px; }
.card img { width: 100%; height: auto; border-radius: 4px; }
.card p { margin: 8px 0; }
.card a { color: #1a67d2; text-decoration: none; }
.card a:hover { text-decoration: underline; }

.manufacturer-name { font-size: 14px; font-weight: bold; color: #1a2a3a; margin: 0 0 4px; text-transform: uppercase; }

.inventory-counts { font-size: 13px; margin: 5px 0 10px; }
.inventory-counts span { display: inline-block; margin-right: 10px; background-color: #e8edf5; padding: 2px 6px; border-radius: 4px; color: #1a2a3a; }

.tags { margin: 5px 0; }
.tags .tag { display: inline-block; background-color: #dfe7f3; color: #1a2a3a; padding: 2px 6px; margin-right: 6px; border-radius: 4px; font-size: 12px; }

.image-modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); align-items:center; justify-content:center; z-index:1000; cursor:zoom-out; }
.image-modal img { max-width:92%; max-height:92%; border-radius:6px; background:#fff; }
"""

# ---------- Pages ----------
def generate_index(inv_df: pd.DataFrame, demos_df: pd.DataFrame) -> str:
    nav = generate_nav('index.html')
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IoTConnect Catalog</title><link rel="stylesheet" href="style.css">
</head><body>{nav}
<div class="container">
  <h1>IoTConnect Hardware & Demo Catalog</h1>
  <p>Browse available hardware and demos. Use the Inventory and Demos pages to filter by manufacturer, search case-insensitively, and click images to enlarge.</p>
  <ul>
    <li><strong>{len(inv_df)}</strong> boards in inventory</li>
    <li><strong>{len(demos_df)}</strong> demos cataloged</li>
  </ul>
</div></body></html>"""

def generate_inventory(inv_df: pd.DataFrame) -> str:
    nav = generate_nav('inventory.html')
    # unique manufacturers
    mfgs = sorted({str(m).strip() for m in inv_df.get('Manufacturer', []) if str(m).strip()})
    options = ['<option value="all">All Manufacturers</option>'] + [f'<option value="{m}">{m}</option>' for m in mfgs]

    body = [f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hardware Inventory</title><link rel="stylesheet" href="style.css"></head><body>{nav}
<div class="container">
  <div class="controls">
    <label for="inventory-filter">Filter by manufacturer:</label>
    <select id="inventory-filter">{''.join(options)}</select>
    <input id="inventory-search" type="text" placeholder="Search...">
  </div>
  <div class="grid">"""]

    for _, row in inv_df.iterrows():
        manufacturer = str(row.get('Manufacturer', '')).strip()
        name = str(row.get('Common Name', '')).strip()
        part_no = str(row.get('Partnumber', '')).strip()
        link = str(row.get('Link', '')).strip()
        image = str(row.get('Image', '')).strip()
        gh_index = str(row.get('GithubIndex', '')).strip()
        # Team counts
        counts = []
        for k in sorted(TEAM_INITIALS):
            val = row.get(k, '')
            try: n = int(str(val).strip()) if str(val).strip() else 0
            except: n = 0
            counts.append((k, n))

        card = [f'<div class="card" data-manufacturer="{manufacturer.lower()}">']
        if manufacturer:
            card.append(f'  <div class="manufacturer-name">{manufacturer}</div>')
        card.append(f'  <h2>{name}</h2>')
        if image:
            card.append(f'  <img src="{image}" alt="{name}" class="enlargeable">')
        if part_no:
            card.append(f'  <p><strong>Part Number:</strong> {part_no}</p>')

        if gh_index and gh_index.lower() != 'no':
            card.append(f'  <p><a href="{gh_index}" target="_blank" rel="noopener">GitHub reference</a></p>')
        elif link:
            card.append(f'  <p><a href="{link}" target="_blank" rel="noopener">Product page</a></p>')

        # Team inventory
        counts_str = ' '.join([f'{k}: {n}' for k, n in counts])
        card.append('  <p><strong>Team inventory:</strong></p>')
        card.append(f'  <div class="inventory-counts">{" ".join([f"<span>{k}: {n}</span>" for k, n in counts])}</div>')

        card.append('</div>')
        body.extend(card)

    body.extend(["""  </div>
</div>
<div id="imgModal" class="image-modal"><img alt=""></div>
<script>
// case-insensitive search + manufacturer filter
(function(){
  const select = document.getElementById('inventory-filter');
  const search = document.getElementById('inventory-search');
  const cards  = Array.from(document.querySelectorAll('.card'));

  function applyFilters(){
    const mfg = (select.value || 'all').toLowerCase();
    const q   = (search.value || '').toLowerCase();
    cards.forEach(c => {
      const okMfg = (mfg === 'all') || (c.dataset.manufacturer === mfg);
      const okQ   = c.textContent.toLowerCase().includes(q);
      c.style.display = (okMfg && okQ) ? '' : 'none';
    });
  }
  select.addEventListener('change', applyFilters);
  search.addEventListener('input', applyFilters);

  // lightbox
  const modal = document.getElementById('imgModal');
  const modalImg = modal.querySelector('img');
  document.body.addEventListener('click', e => {
    const img = e.target.closest('img.enlargeable');
    if (img) { modalImg.src = img.src; modal.style.display = 'flex'; }
  });
  modal.addEventListener('click', () => { modal.style.display = 'none'; modalImg.src=''; });
})();
</script>
</body></html>"""])
    return '\n'.join(body)

def generate_demos(demos_df: pd.DataFrame) -> str:
    nav = generate_nav('demos.html')
    mfgs = sorted({str(m).strip() for m in demos_df.get('Manufacturer', []) if str(m).strip()})
    options = ['<option value="all">All Manufacturers</option>'] + [f'<option value="{m}">{m}</option>' for m in mfgs]

    body = [f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Demos</title><link rel="stylesheet" href="style.css"></head><body>{nav}
<div class="container">
  <div class="controls">
    <label for="demos-filter">Filter by manufacturer:</label>
    <select id="demos-filter">{''.join(options)}</select>
    <input id="demos-search" type="text" placeholder="Search...">
  </div>
  <div class="grid">"""]

    dash_cols = [f'Dashboard {i}' for i in range(1,7)]
    img_cols  = [f'Demo Image {i}' for i in range(1,6)]
    target_cols = [f'Target {i}' for i in range(1,5)]

    for _, row in demos_df.iterrows():
        manufacturer = str(row.get('Manufacturer', '')).strip()
        title = str(row.get('Demo', '')).strip()
        gh_link = str(row.get('Github Link', '')).strip()
        description = str(row.get('Demo Description', '')).strip()
        if not description:
            description = 'Description coming soon.'

        # Tags: prefer spreadsheet Tags column, else derive from title
        tags_raw = str(row.get('Tags', '')).strip()
        if tags_raw:
            tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
        else:
            words = re.split(r'[\s\-_\/]+', title)
            tags = [w for w in words if w and w.lower() not in {'the','and','for','with','demo','iot','a','an','on'}][:6]

        targets = [str(row.get(c, '')).strip() for c in target_cols if str(row.get(c, '')).strip()]
        dashboards = [str(row.get(c, '')).strip() for c in dash_cols if str(row.get(c, '')).strip()]
        demo_imgs  = [str(row.get(c, '')).strip() for c in img_cols if str(row.get(c, '')).strip()]

        card = [f'<div class="card" data-manufacturer="{manufacturer.lower()}">']
        if title:
            card.append(f'  <h2>{title}</h2>')
        if manufacturer:
            card.append(f'  <p><strong>Manufacturer:</strong> {manufacturer}</p>')
        if targets:
            card.append(f'  <p><strong>Target boards:</strong> {", ".join(targets)}</p>')
          
        card.append(f'  <p>{description}</p>')

        if gh_link:
            card.append(f'  <p><a href="{gh_link}" target="_blank" rel="noopener">GitHub repository</a></p>')

        if dashboards:
            card.append('  <div class="dash-grid">')
            for url in dashboards:
                card.append(f'    <img src="{url}" alt="Dashboard" class="enlargeable">')
            card.append('  </div>')
        if demo_imgs:
            card.append('  <div class="dash-grid">')
            for url in demo_imgs:
                card.append(f'    <img src="{url}" alt="Demo image" class="enlargeable">')
            card.append('  </div>')

        if tags:
            card.append('  <div class="tags">' + ' '.join(f'<span class="tag">{t}</span>' for t in tags) + '</div>')

        card.append('</div>')
        body.extend(card)

    body.extend(["""  </div>
</div>
<div id="imgModal" class="image-modal"><img alt=""></div>
<script>
(function(){
  const select = document.getElementById('demos-filter');
  const search = document.getElementById('demos-search');
  const cards  = Array.from(document.querySelectorAll('.card'));
  function applyFilters(){
    const mfg = (select.value || 'all').toLowerCase();
    const q   = (search.value || '').toLowerCase();
    cards.forEach(c => {
      const okMfg = (mfg === 'all') || (c.dataset.manufacturer === mfg);
      const okQ   = c.textContent.toLowerCase().includes(q);
      c.style.display = (okMfg && okQ) ? '' : 'none';
    });
  }
  select.addEventListener('change', applyFilters);
  search.addEventListener('input', applyFilters);

  const modal = document.getElementById('imgModal');
  const modalImg = modal.querySelector('img');
  document.body.addEventListener('click', e => {
    const img = e.target.closest('img.enlargeable');
    if (img) { modalImg.src = img.src; modal.style.display = 'flex'; }
  });
  modal.addEventListener('click', () => { modal.style.display = 'none'; modalImg.src=''; });
})();
</script>
</body></html>"""])
    return '\n'.join(body)

# ---------- Main ----------
def main():
    inv_df, demos_df = load_data()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # write assets
    write_file(OUTPUT_DIR / "style.css", STYLE_CSS)
    # copy logo if present
    logo = SCRIPT_DIR / "iotconnect_logo.png"
    if logo.exists():
        (OUTPUT_DIR / "iotconnect_logo.png").write_bytes(logo.read_bytes())

    # pages
    write_file(OUTPUT_DIR / "index.html",     generate_index(inv_df, demos_df))
    write_file(OUTPUT_DIR / "inventory.html", generate_inventory(inv_df))
    write_file(OUTPUT_DIR / "demos.html",     generate_demos(demos_df))
    print(f"[done] wrote site to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
