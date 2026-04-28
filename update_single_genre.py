"""
Actualizar género de una sola serie
"""

import json
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')

# Datos a actualizar
nombre_buscar = "Tutenstein"
nuevo_genero = "Comedia, Aventura, Fantasía, Infantil"

# Cargar JSON
with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Buscar y actualizar
encontrado = False
for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        nombre = item.get('name', '')
        if nombre_buscar.lower() in nombre.lower():
            print(f"✅ Encontrado: {nombre}")
            print(f"   Antes: {item.get('genre', 'N/A')}")
            item['genre'] = nuevo_genero
            print(f"   Después: {nuevo_genero}")
            encontrado = True
            break
    if encontrado:
        break

if not encontrado:
    print(f"❌ No se encontró '{nombre_buscar}'")
else:
    # Guardar cambios
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Cambios guardados en TOP.json")
