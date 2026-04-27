"""
Script maestro para actualizar la web de Anime Zone ESP con miniaturas estilo Netflix

Este script coordina:
1. Extracción de imágenes del foro (requiere login)
2. Generación del HTML con diseño tipo Netflix
3. Preparación para subir a GitHub Pages

Uso:
    python actualizar_web_con_imagenes.py

Requisitos:
    - Python 3.8+
    - requests
    - beautifulsoup4
    - TOP.json con datos de series
"""

import subprocess
import sys
import os
from pathlib import Path

def run_script(script_name):
    """Ejecutar un script Python y mostrar la salida"""
    print(f"\n{'='*60}")
    print(f"🚀 Ejecutando: {script_name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error ejecutando {script_name}: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

def main():
    print("="*60)
    print("🎨 ACTUALIZADOR WEB ANIME ZONE ESP - Estilo Netflix")
    print("="*60)
    print("\nEste proceso:")
    print("   1. Extrae imágenes del foro (requiere login)")
    print("   2. Genera index.html con diseño tipo Netflix")
    print("   3. Prepara todo para GitHub Pages")
    print()
    
    # Verificar que existan los archivos necesarios
    required_files = ['TOP.json', 'extraer_imagenes_foro.py', 'generar_html_foroactivo.py']
    missing = [f for f in required_files if not Path(f).exists()]
    
    if missing:
        print(f"❌ Faltan archivos: {', '.join(missing)}")
        return
    
    # Paso 1: Extraer imágenes del foro
    print("\n📸 PASO 1: Extracción de imágenes del foro")
    print("   Se conectará a animezoneesp.foroactivo.com")
    print("   y descargará las imágenes de cada tema.")
    
    response = input("\n¿Deseas extraer las imágenes ahora? (s/n): ").lower().strip()
    
    if response == 's':
        if not run_script('extraer_imagenes_foro.py'):
            print("\n⚠️ La extracción de imágenes falló, pero continuaremos...")
            print("   Se usarán placeholders para las series sin imágenes.")
    else:
        print("\n⏭️ Saltando extracción de imágenes...")
    
    # Paso 2: Generar HTML
    print("\n🎨 PASO 2: Generación del HTML")
    if not run_script('generar_html_foroactivo.py'):
        print("\n❌ Error generando el HTML")
        return
    
    # Verificar que se generó el archivo
    if Path('index.html').exists():
        print("\n" + "="*60)
        print("✅ ¡PROCESO COMPLETADO!")
        print("="*60)
        print(f"\n📁 Archivos generados:")
        print(f"   • index.html - Web principal con diseño Netflix")
        if Path('images').exists():
            image_count = len(list(Path('images').glob('*')))
            print(f"   • images/ - Carpeta con {image_count} imágenes")
        print(f"\n🚀 Siguiente paso:")
        print(f"   1. Sube index.html a tu repositorio de GitHub")
        print(f"   2. Activa GitHub Pages en Settings > Pages")
        print(f"   3. Selecciona 'Deploy from Branch' > main/root")
        print(f"\n🌐 Tu web estará en:")
        print(f"   https://anidibucastellano-byte.github.io/anime-zone-esp/")
    else:
        print("\n❌ No se encontró index.html")

if __name__ == "__main__":
    main()
