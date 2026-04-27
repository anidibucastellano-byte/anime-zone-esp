#!/usr/bin/env python3
import json

data = json.load(open('TOP.json', encoding='utf-8'))
total = 0
for cat in ['anime', 'dibujos', 'peliculas', 'series']:
    for i in data.get(cat, []):
        if i.get('imagen'):
            total += 1

print(f'Items con imagen: {total}')
print(f'Total items: {sum(len(data.get(c, [])) for c in ["anime", "dibujos", "peliculas", "series"])}')
