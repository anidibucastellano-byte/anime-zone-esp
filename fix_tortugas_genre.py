"""
Corregir el género de Las Tortugas Ninja (2012)
"""

import json
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')

# Nuevos géneros correctos
nuevos_generos = "Acción, Comedia, Aventura, Artes marciales, Ciencia ficción, Infantil"

with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Buscar y actualizar Tortugas Ninja (2012)
encontrado = False
for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        nombre = item.get('name', '').lower()
        if 'tortugas' in nombre and 'ninja' in nombre and item.get('year') == 2012:
            print(f"Encontrado: {item['name']}")
            print(f"Género anterior: {item.get('genre', 'NO TIENE')}")
            item['genre'] = nuevos_generos
            print(f"Género nuevo: {item['genre']}")
            encontrado = True
            break
    if encontrado:
        break

if encontrado:
    # Guardar cambios
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Género actualizado correctamente en TOP.json")
else:
    print(f"\n❌ No se encontró Las Tortugas Ninja (2012)")
