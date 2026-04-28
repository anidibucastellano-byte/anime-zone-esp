"""
Verificar géneros en el HTML generado
"""

from pathlib import Path
import re

ruta_html = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\index.html')

# Leer HTML
with open(ruta_html, 'r', encoding='utf-8') as f:
    contenido = f.read()

# Buscar ACCA en el JSON embebido
if 'ACCA' in contenido:
    # Encontrar la línea con ACCA
    for line in contenido.split('\n'):
        if 'ACCA' in line and '13-ku' in line:
            print("Encontrado ACCA en HTML:")
            print(line[:500])
            # Buscar genre en esa línea
            match = re.search(r'"genre":\s*"([^"]+)"', line)
            if match:
                print(f"\nGénero en HTML: {match.group(1)}")
            break
else:
    print("ACCA no encontrado en HTML")

# Verificar si el género está correcto
if 'Drama, Político, Misterio' in contenido:
    print("\n✅ SÍ existe 'Drama, Político, Misterio' en el HTML")
else:
    print("\n❌ NO existe 'Drama, Político, Misterio' en el HTML")
