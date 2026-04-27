#!/usr/bin/env python3
"""
Corrige TODAS las rutas de imágenes en TOP.json que apuntan a archivos inexistentes
"""
import json
import os
import re

def extraer_numero_tema(href):
    """Extraer número del tema del href, ej: /t1236-... -> 1236"""
    if not href:
        return None
    match = re.search(r'/t(\d+)-', href)
    if match:
        return match.group(1)
    return None

def encontrar_archivo_por_tema(numero_tema, categoria):
    """Buscar archivo que contenga el número del tema en su nombre"""
    if not numero_tema:
        return None
    
    for archivo in os.listdir('images'):
        # Ignorar archivos corruptos que empiezan con "images"
        if archivo.startswith("images"):
            continue
        # Buscar el número del tema en el nombre
        if numero_tema in archivo and archivo.startswith(categoria):
            return f"images/{archivo}"
    return None

def main():
    # Cargar TOP.json
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    corregidas = 0
    no_corregidas = []
    
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        for item in data.get(categoria, []):
            nombre = item.get('nombre', item.get('name', 'Sin nombre'))
            href = item.get('href', '')
            imagen_actual = item.get('imagen', '')
            
            # Verificar si la imagen actual existe
            if imagen_actual:
                ruta_completa = imagen_actual.replace('/', os.sep)
                if os.path.exists(ruta_completa):
                    continue  # La imagen existe, todo bien
            
            # La imagen no existe, buscar por número de tema
            numero_tema = extraer_numero_tema(href)
            archivo_correcto = encontrar_archivo_por_tema(numero_tema, categoria)
            
            if archivo_correcto:
                item['imagen'] = archivo_correcto
                corregidas += 1
                print(f"✅ {nombre}")
                print(f"   Tema: t{numero_tema}")
                print(f"   → {archivo_correcto}\n")
            else:
                no_corregidas.append({
                    'nombre': nombre,
                    'tema': numero_tema,
                    'categoria': categoria,
                    'href': href
                })
    
    # Guardar TOP.json actualizado
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Corregidas: {corregidas}")
    print(f"   ❌ Sin imagen disponible: {len(no_corregidas)}")
    
    if no_corregidas:
        print(f"\n⚠️ Items que necesitan re-descargar imagen:")
        for item in no_corregidas:
            print(f"   - t{item['tema']}: {item['nombre']}")

if __name__ == "__main__":
    main()
