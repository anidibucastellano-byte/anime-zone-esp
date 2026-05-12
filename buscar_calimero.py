#!/usr/bin/env python3
import json

with open(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== Buscando Calimero ===\n")

for cat in ['anime', 'dibujos', 'peliculas', 'series']:
    for item in data.get(cat, []):
        name = item.get('name', '').lower()
        if 'calimero' in name:
            print(f"Categoría: {cat.upper()}")
            print(f"  Nombre: {item.get('name', 'N/A')}")
            print(f"  Año: {item.get('year', '---')}")
            print(f"  Género: {item.get('genre', '---')}")
            print(f"  Sinopsis: {item.get('sinopsis', '---')[:80]}...")
            print(f"  URL: {item.get('url', '---')}")
            print()
