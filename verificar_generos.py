"""
Verificar géneros específicos en el JSON y HTML
"""

import json
from pathlib import Path

# Verificar en TOP.json
ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== VERIFICANDO TOP.JSON ===")
for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        nombre = item.get('name', '')
        if 'ACCA' in nombre or 'Gunslinger Girl' in nombre or 'Heidi' in nombre:
            print(f"\n📺 {nombre[:50]}...")
            print(f"   Género: {item.get('genre', 'NO TIENE')}")

# Verificar en index.html
print("\n\n=== VERIFICANDO INDEX.HTML ===")
ruta_html = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\index.html')
with open(ruta_html, 'r', encoding='utf-8') as f:
    html = f.read()

generos_buscar = [
    'Drama, Político, Misterio',
    'Drama, Acción, Psicológico',
    'Drama, Infantil, Slice of Life',
    'Acción, Comedia, Crimen'
]

for genero in generos_buscar:
    if genero in html:
        print(f"✅ '{genero}' encontrado en HTML")
    else:
        print(f"❌ '{genero}' NO encontrado en HTML")

print(f"\n📁 Ubicación del HTML: {ruta_html}")
print(f"📊 Tamaño del HTML: {len(html):,} caracteres")
