#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

incompletas = []
for cat in ['anime', 'series', 'dibujos', 'peliculas']:
    for item in data.get(cat, []):
        sinopsis = item.get('sinopsis', '')
        if sinopsis:
            last_char = sinopsis[-1] if sinopsis else ''
            # No termina en punto final
            if last_char not in ['.', '!', '?', '"', '”']:
                incompletas.append({
                    'nombre': item.get('nombre_limpio', item.get('name', 'N/A')),
                    'fin': sinopsis[-30:] if len(sinopsis) > 30 else sinopsis,
                    'url': item.get('url', ''),
                    'cat': cat
                })

print(f'TOTAL sinopsis sin punto final: {len(incompletas)}')
print()

# Guardar lista
with open('lista_incompletas.txt', 'w', encoding='utf-8') as f:
    f.write(f'TOTAL: {len(incompletas)}\n\n')
    for i, item in enumerate(incompletas, 1):
        line = f"{i}. {item['nombre']}\n   ...{item['fin']}\n\n"
        f.write(line)
        print(line.strip())

print(f'\n✅ Lista guardada en lista_incompletas.txt')
