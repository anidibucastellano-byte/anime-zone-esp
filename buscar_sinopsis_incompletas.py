#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

# Cargar TOP.json
with open('TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Buscar sinopsis que no terminen en punto
incompletas = []
for cat in ['anime', 'series', 'dibujos', 'peliculas']:
    for item in data.get(cat, []):
        sinopsis = item.get('sinopsis', '')
        if sinopsis and not sinopsis.endswith('.'):
            # También verificar si termina en "..." o está cortada
            if sinopsis.endswith('...') or sinopsis.endswith('desc') or len(sinopsis) < 100:
                incompletas.append({
                    'nombre': item.get('nombre_limpio', item.get('name', 'N/A')),
                    'sinopsis': sinopsis[:100] + '...',
                    'url': item.get('url', ''),
                    'cat': cat
                })

print(f"📊 Sinopsis incompletas encontradas: {len(incompletas)}\n")

for i, item in enumerate(incompletas[:20], 1):  # Mostrar primeras 20
    print(f"{i}. {item['nombre']}")
    print(f"   Sinopsis: {item['sinopsis']}")
    print(f"   URL: {item['url']}")
    print()

# Guardar lista para procesar
with open('sinopsis_incompletas.json', 'w', encoding='utf-8') as f:
    json.dump(incompletas, f, ensure_ascii=False, indent=2)

print(f"✅ Lista guardada en sinopsis_incompletas.json")
