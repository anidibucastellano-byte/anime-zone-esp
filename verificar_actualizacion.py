"""
Verificar qué series del archivo nuevo1.txt NO se actualizaron
"""
import json
import re
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
ruta_txt = Path(r'c:\Users\Rafael\Desktop\nuevo1.txt')

# Leer archivo de géneros
with open(ruta_txt, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f.readlines() if line.strip()]

# Crear diccionario de correcciones esperadas
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

# Cargar JSON
with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Verificar cuáles se actualizaron y cuáles no
actualizados = 0
no_actualizados = []

for nombre_txt, generos_esperados in correcciones.items():
    nombre_txt_clean = re.sub(r'\s*\(\d{4}\)\s*$', '', nombre_txt).strip().lower()
    encontrado = False
    actualizado = False
    
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        if categoria not in data:
            continue
        for item in data[categoria]:
            nombre_item = item.get('name', '')
            nombre_item_clean = nombre_item.split('[')[0].replace('(Activo)', '').replace('(Finalizado)', '').strip()
            nombre_item_clean = re.sub(r'\s*\(\d{4}\)\s*$', '', nombre_item_clean).lower()
            
            if nombre_txt_clean in nombre_item_clean or nombre_item_clean in nombre_txt_clean:
                encontrado = True
                # Verificar si tiene el género actualizado
                if item.get('genre') == generos_esperados:
                    actualizado = True
                    actualizados += 1
                else:
                    no_actualizados.append((nombre_txt, nombre_item, item.get('genre', 'N/A'), generos_esperados))
                break
        if encontrado:
            break
    
    if not encontrado:
        no_actualizados.append((nombre_txt, "NO ENCONTRADO", "N/A", generos_esperados))

print(f"=== RESULTADOS ===\n")
print(f"✅ Actualizados correctamente: {actualizados}/{len(correcciones)}")
print(f"❌ No actualizados: {len(no_actualizados)}\n")

if no_actualizados:
    print("=== SERIES QUE NO SE ACTUALIZARON ===\n")
    for nombre_txt, nombre_item, genero_actual, genero_esperado in no_actualizados[:20]:
        print(f"Esperado: {nombre_txt}")
        print(f"Encontrado: {nombre_item[:50]}...")
        print(f"Género actual: {genero_actual}")
        print(f"Género esperado: {genero_esperado}")
        print()
