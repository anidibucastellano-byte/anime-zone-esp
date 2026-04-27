#!/usr/bin/env python3
"""
Verifica el tamaño de todas las imágenes y encuentra las que no son ~300x450
"""
import json
import os
from PIL import Image

def get_image_size(filepath):
    """Obtener tamaño de imagen"""
    try:
        with Image.open(filepath) as img:
            return img.size
    except:
        return None

def main():
    # Cargar TOP.json
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    incorrectas = []
    correctas = 0
    no_existe = 0
    
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        for item in data.get(categoria, []):
            nombre = item.get('nombre', item.get('name', 'Sin nombre'))
            imagen_path = item.get('imagen', '')
            href = item.get('href', '')
            
            if not imagen_path:
                continue
            
            # Verificar si existe
            ruta_completa = imagen_path.replace('/', os.sep)
            if not os.path.exists(ruta_completa):
                no_existe += 1
                continue
            
            # Verificar tamaño
            size = get_image_size(ruta_completa)
            if not size:
                continue
            
            width, height = size
            
            # Verificar si es aproximadamente 300x450 (con margen de error)
            # Ratio esperado: 300/450 = 0.667
            ratio = width / height if height > 0 else 0
            ratio_esperado = 300 / 450  # 0.667
            
            # Es correcta si:
            # - El ancho está entre 200-500
            # - El alto está entre 350-600
            # - El ratio es similar a 2:3 (0.6 - 0.75)
            es_correcta = (
                200 <= width <= 500 and
                350 <= height <= 600 and
                0.6 <= ratio <= 0.75
            )
            
            if es_correcta:
                correctas += 1
            else:
                incorrectas.append({
                    'nombre': nombre,
                    'href': href,
                    'path': imagen_path,
                    'size': f"{width}x{height}",
                    'ratio': f"{ratio:.3f}"
                })
                print(f"❌ {nombre}")
                print(f"   Tamaño: {width}x{height} (ratio: {ratio:.3f})")
                print(f"   Esperado: ~300x450 (ratio: 0.667)\n")
    
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Correctas (~300x450): {correctas}")
    print(f"   ❌ Incorrectas: {len(incorrectas)}")
    print(f"   ❌ No existen: {no_existe}")
    
    # Guardar lista de incorrectas para re-extracción
    with open('imagenes_incorrectas.json', 'w', encoding='utf-8') as f:
        json.dump(incorrectas, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Lista guardada en: imagenes_incorrectas.json")
    print(f"   Total a re-extraer: {len(incorrectas)}")

if __name__ == "__main__":
    main()
