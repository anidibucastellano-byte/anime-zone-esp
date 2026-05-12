#!/usr/bin/env python3
"""
Descargador simple de 3Cat usando yt-dlp
"""
import subprocess
import sys
from pathlib import Path

def main():
    url = "https://www.3cat.cat/3cat/asha/capitols/"
    output_dir = Path('descargas_3cat')
    output_dir.mkdir(exist_ok=True)
    
    print("="*60)
    print("🎬 DESCARGANDO VIDEOS DE 3CAT")
    print("="*60)
    print(f"URL: {url}")
    print(f"Destino: {output_dir.absolute()}")
    print()
    
    # Comando yt-dlp para descargar toda la serie
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '--no-warnings',
        '--ignore-errors',
        '-f', 'best',
        '-o', str(output_dir / '%(title)s.%(ext)s'),
        '--add-metadata',
        '--embed-thumbnail',
        '--concurrent-fragments', '3',
        url
    ]
    
    print("⬇️  Iniciando descarga...")
    print(f"Comando: {' '.join(cmd[:5])} ...")
    print()
    
    # Ejecutar sin capturar output para ver progreso
    subprocess.run(cmd)
    
    print()
    print("="*60)
    print("✅ Proceso completado")
    print(f"📁 Videos guardados en: {output_dir.absolute()}")
    print("="*60)

if __name__ == "__main__":
    main()
