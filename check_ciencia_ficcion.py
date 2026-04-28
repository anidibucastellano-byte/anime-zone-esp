"""
Verificar cuántos items tienen Ciencia ficción como primer género
"""

import json
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')

with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Contar géneros (primer género de cada item)
genre_counts = {}
items_por_genero = {}

for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        # Usar item.genre primero (actualizado), luego specificGenre
        full_genre = item.get('genre') or item.get('specificGenre') or 'Sin Género'
        if not isinstance(full_genre, str):
            full_genre = str(full_genre) if full_genre else 'Sin Género'
        
        # Primer género (antes de la coma)
        primer_genero = full_genre.split(',')[0].strip().lower()
        
        genre_counts[primer_genero] = genre_counts.get(primer_genero, 0) + 1
        
        if primer_genero not in items_por_genero:
            items_por_genero[primer_genero] = []
        items_por_genero[primer_genero].append(item.get('name', 'Sin nombre')[:50])

# Mostrar conteos
print("=== CONTEO POR PRIMER GÉNERO ===\n")
for genero, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
    print(f"{genero}: {count}")

# Verificar específicamente ciencia ficción
if 'ciencia ficción' in items_por_genero:
    print(f"\n=== Items con 'Ciencia ficción' como primer género ({len(items_por_genero['ciencia ficción'])}): ===")
    for nombre in items_por_genero['ciencia ficción'][:10]:
        print(f"  - {nombre}")
    if len(items_por_genero['ciencia ficción']) > 10:
        print(f"  ... y {len(items_por_genero['ciencia ficción']) - 10} más")
