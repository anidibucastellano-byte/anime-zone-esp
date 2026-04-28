"""
Actualizar géneros en TOP.json desde archivo .txt
Formato: nombre serie, línea, géneros, línea, nombre serie, etc.
"""

import json
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
ruta_txt = Path(r'c:\Users\Rafael\Desktop\nuevo1.txt')

# Leer archivo de géneros
with open(ruta_txt, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f.readlines()]

# Crear diccionario de correcciones
correcciones = {}
i = 0
while i < len(lines):
    nombre = lines[i]
    if i + 1 < len(lines):
        generos = lines[i + 1]
        correcciones[nombre] = generos
        i += 2
    else:
        i += 1

print(f"📄 Total de correcciones a aplicar: {len(correcciones)}")

# Cargar JSON
with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Aplicar correcciones
actualizados = 0
no_encontrados = []

for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        nombre_item = item.get('name', '')
        # Buscar coincidencia limpiando el nombre
        for nombre_txt, generos in correcciones.items():
            if nombre_txt.lower() in nombre_item.lower() or nombre_item.lower() in nombre_txt.lower():
                print(f"✅ {nombre_item[:60]}...")
                print(f"   Antes: {item.get('genre', 'N/A')}")
                item['genre'] = generos
                print(f"   Después: {generos}")
                actualizados += 1
                break

print(f"\n📊 Resumen:")
print(f"   Actualizados: {actualizados}/{len(correcciones)}")

# Guardar cambios
with open(ruta_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n💾 Cambios guardados en TOP.json")
