"""
Actualizar TODAS las series del archivo nuevo1.txt con coincidencias parciales
"""

import json
import re
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
ruta_txt = Path(r'c:\Users\Rafael\Desktop\nuevo1.txt')

# Leer archivo de géneros
with open(ruta_txt, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f.readlines() if line.strip()]

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

print(f"📋 Total en archivo: {len(correcciones)}")

# Cargar JSON
with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Función para normalizar nombres
def normalizar(nombre):
    # Quitar corchetes, paréntesis, años y espacios extras
    nombre = re.sub(r'\[.*?\]', '', nombre)
    nombre = re.sub(r'\(.*?\)', '', nombre)
    nombre = re.sub(r'\s+', ' ', nombre)
    return nombre.strip().lower()

# Actualizar géneros
actualizados = 0
no_encontrados = []

for nombre_txt, generos_txt in correcciones.items():
    nombre_normalizado = normalizar(nombre_txt)
    encontrado = False
    
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        if categoria not in data:
            continue
        for item in data[categoria]:
            nombre_item = item.get('name', '')
            nombre_item_normalizado = normalizar(nombre_item)
            
            # Coincidencia si uno contiene al otro
            if nombre_normalizado in nombre_item_normalizado or nombre_item_normalizado in nombre_normalizado:
                if item.get('genre') != generos_txt:
                    print(f"✅ {nombre_item[:50]}...")
                    print(f"   Antes: {item.get('genre', item.get('specificGenre', 'N/A'))}")
                    item['genre'] = generos_txt
                    print(f"   Después: {generos_txt}")
                    actualizados += 1
                encontrado = True
                break
        if encontrado:
            break
    
    if not encontrado:
        no_encontrados.append(nombre_txt)

print(f"\n📊 Actualizados: {actualizados}")
print(f"❌ No encontrados: {len(no_encontrados)}")

if no_encontrados:
    print("\nSeries no encontradas:")
    for nombre in no_encontrados[:10]:
        print(f"  - {nombre}")

# Guardar cambios
with open(ruta_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n💾 Cambios guardados")
