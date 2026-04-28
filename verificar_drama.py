"""Verificar cuántos items tienen Drama como primer género"""
import json
from pathlib import Path

ruta = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
with open(ruta, 'r', encoding='utf-8') as f:
    data = json.load(f)

genre_counts = {}
drama_items = []

for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        # Usar genre primero (actualizado), luego specificGenre
        full_genre = item.get('genre') or item.get('specificGenre') or 'Sin Género'
        if not isinstance(full_genre, str):
            full_genre = str(full_genre) if full_genre else 'Sin Género'
        
        primer_genero = full_genre.split(',')[0].strip().lower()
        genre_counts[primer_genero] = genre_counts.get(primer_genero, 0) + 1
        
        if primer_genero == 'drama':
            drama_items.append(item.get('name', 'Sin nombre')[:60])

print("=== CONTEO POR GÉNERO EN TOP.JSON ===\n")
for genero, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{genero}: {count}")

print(f"\n=== SERIES CON 'DRAMA' COMO PRIMER GÉNERO ({len(drama_items)}): ===")
for i, nombre in enumerate(drama_items[:15], 1):
    print(f"{i}. {nombre}")
if len(drama_items) > 15:
    print(f"... y {len(drama_items) - 15} más")
