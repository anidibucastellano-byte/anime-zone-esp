"""
Verificar la imagen de Las Tortugas Ninja (2012)
"""

import json
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')

with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Buscar Tortugas Ninja (2012)
for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        nombre = item.get('name', '').lower()
        if 'tortugas' in nombre and 'ninja' in nombre and item.get('year') == 2012:
            print(f"Nombre: {item['name']}")
            print(f"imagen_url: {item.get('imagen_url', 'NO TIENE')}")
            print(f"imagen: {item.get('imagen', 'NO TIENE')}")
            print(f"url: {item.get('url', 'NO TIENE')}")
            break
