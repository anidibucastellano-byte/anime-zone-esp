#!/usr/bin/env python3
"""
Corrige todas las rutas en TOP.json para que coincidan con los archivos reales
"""
import json
import os
import re

def main():
    # Cargar TOP.json
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Crear índice de archivos en la carpeta images
    archivos_disponibles = {}
    for archivo in os.listdir('images'):
        # Extraer número de tema del nombre del archivo (ej: anime_123_... o imagesanime_123_...)
        match = re.search(r'(?:images)?[a-z]+_(\d+)_', archivo)
        if match:
            tema_num = match.group(1)
            if tema_num not in archivos_disponibles:
                archivos_disponibles[tema_num] = []
            archivos_disponibles[tema_num].append(archivo)
    
    corregidas = 0
    no_corregidas = []
    
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        for item in data.get(categoria, []):
            href = item.get('href', '')
            nombre = item.get('nombre', item.get('name', 'Sin nombre'))
            imagen_actual = item.get('imagen', '')
            
            # Extraer número de tema del href
            match = re.search(r'/t(\d+)-', href)
            if not match:
                continue
            tema_num = match.group(1)
            
            # Verificar si la imagen actual existe
            if imagen_actual:
                ruta_completa = imagen_actual.replace('/', os.sep)
                if os.path.exists(ruta_completa):
                    continue  # La imagen existe, todo bien
            
            # Buscar archivo correcto
            if tema_num in archivos_disponibles:
                archivos = archivos_disponibles[tema_num]
                # Preferir jpg sobre png
                archivo_correcto = None
                for ext in ['.jpg', '.png', '.webp']:
                    for arch in archivos:
                        if arch.endswith(ext):
                            archivo_correcto = arch
                            break
                    if archivo_correcto:
                        break
                
                if not archivo_correcto:
                    archivo_correcto = archivos[0]
                
                # Actualizar ruta
                nueva_ruta = f"images/{archivo_correcto}"
                item['imagen'] = nueva_ruta
                corregidas += 1
                print(f"✅ t{tema_num}: {nombre[:50]}...")
            else:
                no_corregidas.append((tema_num, nombre))
    
    # Guardar TOP.json
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Corregidas: {corregidas}")
    print(f"   ❌ Sin archivo: {len(no_corregidas)}")
    
    if no_corregidas:
        print(f"\n⚠️ Items sin imagen:")
        for tema_num, nombre in no_corregidas[:10]:
            print(f"   - t{tema_num}: {nombre[:40]}...")

if __name__ == "__main__":
    main()
