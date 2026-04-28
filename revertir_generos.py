"""
Revertir géneros a los valores originales (specificGenre)
"""

import json
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')

with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Revertir géneros
revertidos = 0
for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        # Si tiene specificGenre (original del scraping), eliminar genre (actualizado manualmente)
        if item.get('specificGenre') and item.get('genre'):
            print(f"🔄 {item['name'][:50]}...")
            print(f"   Eliminando: {item['genre']}")
            print(f"   Usando original: {item['specificGenre']}")
            del item['genre']  # Eliminar el género actualizado
            revertidos += 1

print(f"\n📊 Total revertidos: {revertidos}")

with open(ruta_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("💾 Cambios guardados")
print("🔄 Regenerando HTML...")
