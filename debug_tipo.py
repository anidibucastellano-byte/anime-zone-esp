#!/usr/bin/env python3
import json

with open(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== Verificando campos 'type' y 'tipo' en TOP.json ===\n")

for cat in ['anime', 'dibujos', 'peliculas', 'series']:
    items = data.get(cat, [])
    print(f'{cat.upper()}: {len(items)} items')
    if items:
        for i, item in enumerate(items[:3]):  # Primeros 3 de cada categoría
            print(f'  [{i}] {item.get("name", "N/A")[:40]}')
            print(f'      type: {item.get("type", "---")} | tipo: {item.get("tipo", "---")}')
    print()
