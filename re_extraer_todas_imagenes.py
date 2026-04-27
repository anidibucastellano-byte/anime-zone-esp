#!/usr/bin/env python3
"""
Script para RE-extraer TODAS las imágenes del foro
- Limpia los campos 'imagen' de TOP.json
- Procesa TODOS los items de nuevo
- Usa el nuevo código que busca en headerbar
"""
import json
import os
import sys
from extraer_imagenes_foro import ForoImageExtractor, IMAGES_DIR

def limpiar_imagenes_json():
    """Limpiar campos de imagen en TOP.json"""
    print("🧹 Limpiando campos de imagen en TOP.json...")
    
    try:
        with open('TOP.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error cargando TOP.json: {e}")
        return None
    
    categorias = ['anime', 'dibujos', 'peliculas', 'series']
    limpiados = 0
    
    for categoria in categorias:
        items = data.get(categoria, [])
        for item in items:
            if 'imagen' in item or 'imagen_url' in item:
                item.pop('imagen', None)
                item.pop('imagen_url', None)
                limpiados += 1
    
    print(f"   {limpiados} entries limpiados")
    
    # Guardar JSON limpio
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ TOP.json limpio guardado")
    return data

def main():
    print("=" * 60)
    print("🔄 RE-EXTRACTOR COMPLETO DE IMÁGENES")
    print("=" * 60)
    print("Este script limpiará y re-procesará TODAS las imágenes\n")
    
    print("⏳ Comenzando en 3 segundos... (Ctrl+C para cancelar)")
    import time
    time.sleep(3)
    
    # Paso 1: Limpiar JSON
    data = limpiar_imagenes_json()
    if not data:
        return
    
    # Paso 2: Ejecutar extractor
    print("\n🚀 Iniciando extracción completa...")
    extractor = ForoImageExtractor()
    
    # El extractor usará automáticamente el TOP.json limpio
    extractor.procesar_top_json()
    
    print("\n✅ Proceso completado!")

if __name__ == "__main__":
    main()
