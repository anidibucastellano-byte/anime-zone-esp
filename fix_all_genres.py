"""
Actualizar géneros - versión ultra flexible
Busca coincidencias por palabras clave del título
"""

import json
import re
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
ruta_txt = Path(r'c:\Users\Rafael\Desktop\nuevo1.txt')

# Leer archivo
with open(ruta_txt, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f.readlines() if line.strip()]

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

# Extraer palabras clave (solo letras, mínimo 3 caracteres)
def palabras_clave(nombre):
    # Limpiar
    nombre = re.sub(r'\[.*?\]', '', nombre)
    nombre = re.sub(r'\(.*?\)', '', nombre)
    nombre = nombre.replace('(Activo)', '').replace('(Finalizado)', '')
    # Extraer palabras
    palabras = re.findall(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]{3,}', nombre.lower())
    return set(palabras)

actualizados = 0
no_encontrados = []

for nombre_txt, generos_txt in correcciones.items():
    palabras_buscadas = palabras_clave(nombre_txt)
    if not palabras_buscadas:
        continue
    
    # La palabra principal es la más larga o la primera significativa
    palabra_principal = max(palabras_buscadas, key=len)
    
    encontrado = False
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        if categoria not in data:
            continue
        for item in data[categoria]:
            nombre_item = item.get('name', '')
            palabras_item = palabras_clave(nombre_item)
            
            # Coincidencia si comparten la palabra principal
            if palabra_principal in palabras_item:
                if item.get('genre') != generos_txt:
                    print(f"✅ {item['name'][:60]}...")
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

print(f"\n📊 Actualizados: {actualizados}/{len(correcciones)}")

if no_encontrados:
    print(f"\n❌ No encontrados ({len(no_encontrados)}):")
    for nombre in no_encontrados[:20]:
        print(f"  - {nombre}")

# Guardar
with open(ruta_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n💾 Cambios guardados")
