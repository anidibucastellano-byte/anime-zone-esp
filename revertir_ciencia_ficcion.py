"""
Revertir series con género 'Ciencia ficción, Acción, Drama, Thriller' al género original
"""

import json
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')

with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Revertir series con ese género específico incorrecto
revertidos = 0
for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        genre = item.get('genre', '')
        # Si tiene el género incorrecto "Ciencia ficción, Acción, Drama, Thriller"
        if genre == 'Ciencia ficción, Acción, Drama, Thriller':
            nombre = item.get('name', 'Sin nombre')
            original = item.get('specificGenre', 'Sin género')
            print(f"🔄 {nombre[:60]}...")
            print(f"   Eliminando: {genre}")
            print(f"   Volviendo a: {original}")
            del item['genre']  # Eliminar el género incorrecto
            revertidos += 1

print(f"\n📊 Total revertidos: {revertidos}")

with open(ruta_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("💾 Cambios guardados en TOP.json")
print("🔄 Regenerando HTML...")

# Regenerar HTML
import subprocess
result = subprocess.run(['python', r'c:\Users\Rafael\CascadeProjects\windsurf-project\generar_html_foroactivo.py'], 
                       capture_output=True, text=True)
print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
