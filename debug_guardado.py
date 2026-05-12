#!/usr/bin/env python3
import json

with open(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Buscar una serie específica para verificar
for cat in ['anime', 'dibujos', 'peliculas', 'series']:
    for item in data.get(cat, []):
        if 'test' in item.get('sinopsis', '').lower() or item.get('sinopsis', '') == 'PRUEBA':
            print(f"Encontrado en {cat}:")
            print(f"  Nombre: {item.get('name', 'N/A')[:50]}")
            print(f"  Sinopsis: {item.get('sinopsis', '---')[:80]}")
            print()

print("=== Serie de ejemplo (primer anime) ===")
if data.get('anime'):
    serie = data['anime'][0]
    print(f"Nombre: {serie.get('name', 'N/A')[:50]}")
    print(f"Sinopsis: {serie.get('sinopsis', '---')[:80]}")
