"""
Actualizar géneros desde nuevo1.txt
Formato: Nombre (año) en línea impar, géneros en línea par (sin →)
Usar el PRIMER género de la lista para clasificación
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

print(f"📋 Total de series en el archivo: {len(correcciones)}")

# Cargar JSON
with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Función para limpiar nombre (extraer solo nombre sin año)
def limpiar_nombre(nombre):
    # Quitar año entre paréntesis
    nombre_sin_año = re.sub(r'\s*\(\d{4}\)\s*$', '', nombre).strip()
    return nombre_sin_año.lower()

# Actualizar géneros
actualizados = 0
no_encontrados = []

for nombre_txt, generos_txt in correcciones.items():
    nombre_txt_clean = limpiar_nombre(nombre_txt)
    primer_genero = generos_txt.split(',')[0].strip()
    
    encontrado = False
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        if categoria not in data:
            continue
        for item in data[categoria]:
            nombre_item = item.get('name', '')
            # Limpiar nombre del item (quitar [Castellano], [Activo], etc.)
            nombre_item_clean = nombre_item.split('[')[0].replace('(Activo)', '').replace('(Finalizado)', '').strip()
            nombre_item_clean = re.sub(r'\s*\(\d{4}\)\s*$', '', nombre_item_clean).lower()
            
            # Comparar
            if nombre_txt_clean == nombre_item_clean or nombre_txt_clean in nombre_item_clean or nombre_item_clean in nombre_txt_clean:
                print(f"✅ {nombre_item[:50]}...")
                print(f"   Antes: {item.get('genre', item.get('specificGenre', 'N/A'))}")
                item['genre'] = generos_txt
                print(f"   Después: {generos_txt}")
                print(f"   Primer género (clasificación): {primer_genero}")
                actualizados += 1
                encontrado = True
                break
        if encontrado:
            break
    
    if not encontrado:
        no_encontrados.append(nombre_txt)

print(f"\n📊 Actualizados: {actualizados}/{len(correcciones)}")
if no_encontrados:
    print(f"\n❌ No encontrados ({len(no_encontrados)}):")
    for nombre in no_encontrados[:10]:
        print(f"   - {nombre}")

# Guardar cambios
with open(ruta_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n💾 Cambios guardados en TOP.json")
