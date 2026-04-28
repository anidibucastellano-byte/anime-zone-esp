"""
Actualizar géneros desde nuevo1.txt
Formato: nombre serie, línea con flecha, géneros
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
    line = lines[i]
    # Si la línea no empieza con → y la siguiente sí, es un par nombre->género
    if not line.startswith('→') and i + 1 < len(lines):
        next_line = lines[i + 1]
        if next_line.startswith('→'):
            nombre = line
            # Quitar el → y espacios
            generos = next_line.replace('→', '').strip()
            correcciones[nombre] = generos
            i += 2
            continue
    i += 1

print(f"📄 Total de correcciones a aplicar: {len(correcciones)}")

# Cargar JSON
with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Aplicar correcciones
actualizados = 0

for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        nombre_item = item.get('name', '')
        # Buscar coincidencia por nombre (sin año)
        for nombre_txt, generos in correcciones.items():
            # Extraer nombre sin año del txt
            nombre_txt_clean = nombre_txt.split('(')[0].strip().lower()
            # Extraer nombre sin corchetes del item
            nombre_item_clean = nombre_item.split('[')[0].replace('(Activo)', '').replace('(Finalizado)', '').strip().lower()
            
            if nombre_txt_clean in nombre_item_clean or nombre_item_clean in nombre_txt_clean:
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
print("🔄 Regenerando index.html...")
