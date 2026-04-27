#!/usr/bin/env python3
"""
Corrige las rutas de imágenes en TOP.json que apuntan a archivos inexistentes
"""
import json
import os
import re

def safe_filename(nombre):
    """Crear nombre de archivo seguro"""
    nombre = re.sub(r'[<>:"/\\|?*]', '', nombre)
    nombre = nombre[:80]
    return nombre.strip()

def encontrar_archivo_correcto(categoria, item_id, nombre, href):
    """Buscar el archivo correcto en la carpeta images"""
    safe_name = safe_filename(nombre)
    
    # Buscar en la carpeta images
    archivos_encontrados = []
    
    # Extraer número del tema del href (ej: t1318)
    tema_num = None
    if href:
        match = re.search(r'/t(\d+)-', href)
        if match:
            tema_num = match.group(1)
    
    for archivo in os.listdir('images'):
        # Ignorar archivos con "images" al principio (nombres corruptos)
        if archivo.startswith("images"):
            continue
            
        # Verificar si el archivo contiene el ID o el número del tema
        if item_id and (f"_{item_id}_" in archivo or f"-{item_id}-" in archivo or archivo.startswith(f"{categoria}_{item_id}")):
            archivos_encontrados.append(archivo)
        elif tema_num and tema_num in archivo:
            # También buscar por número del tema en el nombre
            archivos_encontrados.append(archivo)
    
    if archivos_encontrados:
        # Preferir .jpg sobre .png si ambos existen
        for ext in ['.jpg', '.png', '.webp']:
            for archivo in archivos_encontrados:
                if archivo.endswith(ext):
                    return f"images/{archivo}"
        return f"images/{archivos_encontrados[0]}"
    
    return None

def extraer_id_de_href(href):
    """Extraer ID numérico del href, ej: /t1318-... -> 1318"""
    if not href:
        return None
    match = re.search(r'/t(\d+)-', href)
    if match:
        return match.group(1)
    return None

def main():
    # Cargar TOP.json
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    corregidas = 0
    no_corregidas = []
    
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        for item in data.get(categoria, []):
            item_id = item.get('id', '')
            nombre = item.get('nombre', item.get('name', 'Sin nombre'))
            imagen_actual = item.get('imagen', '')
            href = item.get('href', '')
            
            # Si no hay ID, extraer del href
            if not item_id:
                item_id = extraer_id_de_href(href)
            
            # Verificar si la imagen actual existe
            if imagen_actual:
                ruta_completa = imagen_actual.replace('/', os.sep)
                if os.path.exists(ruta_completa):
                    continue  # La imagen existe, no hay problema
            
            # La imagen no existe, buscar el archivo correcto
            archivo_correcto = encontrar_archivo_correcto(categoria, item_id, nombre, href)
            
            if archivo_correcto:
                item['imagen'] = archivo_correcto
                corregidas += 1
                print(f"✅ Corregida: {nombre}")
                print(f"   Antes: {imagen_actual}")
                print(f"   Después: {archivo_correcto}\n")
            else:
                no_corregidas.append({
                    'nombre': nombre,
                    'id': item_id,
                    'categoria': categoria,
                    'ruta_actual': imagen_actual
                })
    
    # Guardar TOP.json actualizado
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Resumen:")
    print(f"   Corregidas: {corregidas}")
    print(f"   Sin archivo disponible: {len(no_corregidas)}")
    
    if no_corregidas:
        print(f"\n⚠️ Items sin imagen disponible (mostrando primeros 10):")
        for item in no_corregidas[:10]:
            print(f"   - {item['nombre']} (ID: {item['id']})")

if __name__ == "__main__":
    main()
