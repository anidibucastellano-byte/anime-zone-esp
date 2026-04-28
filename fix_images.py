"""
Script para corregir las imágenes de Las Tortugas Ninja (2012) y Las Supernenas (2016)
"""

import json
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')

# URLs proporcionadas
url_tortugas = "https://res.cloudinary.com/ddaxoi1n4/image/upload/v1770837461/mis_archivos_elegidos/manual_poster_tmdb_Las_Tortugas_Ninja.jpg"
url_supernenas = "https://res.cloudinary.com/ddaxoi1n4/image/upload/v1777298084/mis_archivos_elegidos/manual_poster_tmdb_Las_Supernenas.jpg"

with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Buscar y actualizar Tortugas Ninja (2012)
tortugas_encontrado = False
for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        nombre = item.get('name', '').lower()
        if 'tortugas' in nombre and 'ninja' in nombre and item.get('year') == 2012:
            item['imagen_url'] = url_tortugas
            print(f"✅ Actualizada imagen de: {item['name']}")
            tortugas_encontrado = True
            break
    if tortugas_encontrado:
        break

# Buscar y actualizar Supernenas (2016)
supernenas_encontrado = False
for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        nombre = item.get('name', '').lower()
        if 'supernenas' in nombre and item.get('year') == 2016:
            item['imagen_url'] = url_supernenas
            # También asegurarnos de que tenga imagen local
            item['imagen'] = "images\\dibujos_supernenas_2016.jpg"
            print(f"✅ Actualizada imagen de: {item['name']}")
            supernenas_encontrado = True
            break
    if supernenas_encontrado:
        break

# Guardar cambios
with open(ruta_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n📊 Resumen:")
print(f"   Tortugas Ninja (2012): {'✅ Actualizado' if tortugas_encontrado else '❌ No encontrado'}")
print(f"   Supernenas (2016): {'✅ Actualizado' if supernenas_encontrado else '❌ No encontrado'}")
print(f"\n💾 Cambios guardados en TOP.json")
