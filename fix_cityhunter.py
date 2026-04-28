"""
Corregir género de City Hunter y otras series que no se actualizaron
"""

import json
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')

with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Lista de correcciones manual (nombre buscado, géneros)
correcciones = [
    ("City Hunter", "Acción, Comedia, Crimen"),
    ("DinoZaurs", "Acción, Infantil, Mecha"),
    ("Garfield y sus amigos", "Comedia, Infantil"),
    ("Pepper Ann", "Comedia, Slice of Life"),
    ("Sakura Mail", "Romance, Drama, Ecchi"),
    ("Ghost in the Shell: SAC_2045", "Ciencia ficción, Acción, Policial"),
]

actualizados = 0
for nombre_buscar, generos in correcciones:
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        if categoria not in data:
            continue
        for item in data[categoria]:
            nombre_item = item.get('name', '')
            if nombre_buscar in nombre_item:
                print(f"✅ {nombre_item[:60]}...")
                print(f"   Antes: {item.get('genre', item.get('specificGenre', 'N/A'))}")
                item['genre'] = generos
                print(f"   Después: {generos}")
                actualizados += 1
                break

print(f"\n📊 Actualizados: {actualizados}")

with open(ruta_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("💾 Cambios guardados")
