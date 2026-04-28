"""Verificar género de City Hunter"""
import json
from pathlib import Path

ruta = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
with open(ruta, 'r', encoding='utf-8') as f:
    data = json.load(f)

for cat in ['anime', 'dibujos', 'peliculas', 'series']:
    for item in data.get(cat, []):
        if 'City Hunter' in item.get('name', ''):
            print(f"Nombre: {item['name']}")
            print(f"genre: {item.get('genre', 'N/A')}")
            print(f"specificGenre: {item.get('specificGenre', 'N/A')}")
            break
