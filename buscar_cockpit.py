#!/usr/bin/env python3
import json

with open(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== Buscando The Cockpit ===\n")

for cat in ['anime', 'dibujos', 'peliculas', 'series']:
    for item in data.get(cat, []):
        name = item.get('name', '').lower()
        if 'cockpit' in name:
            print(f"ENCONTRADO en {cat.upper()}:")
            print(f"  Nombre: {item.get('name', 'N/A')}")
            print(f"  type: {item.get('type', '---')}")
            print(f"  genre: {item.get('genre', '---')}")
            print(f"  specificGenre: {item.get('specificGenre', '---')}")
            print()
