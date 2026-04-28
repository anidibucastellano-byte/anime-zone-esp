"""
Listar todas las series con Ciencia ficción como primer género
"""

import json
from pathlib import Path

ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')

with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== SERIES CON 'CIENCIA FICCIÓN' COMO PRIMER GÉNERO ===\n")

contador = 0
series_list = []

for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    for item in data[categoria]:
        # Usar item.genre primero (actualizado), luego specificGenre
        full_genre = item.get('genre') or item.get('specificGenre') or 'Sin Género'
        if not isinstance(full_genre, str):
            full_genre = str(full_genre) if full_genre else 'Sin Género'
        
        # Primer género
        primer_genero = full_genre.split(',')[0].strip().lower()
        
        if primer_genero == 'ciencia ficción':
            contador += 1
            nombre = item.get('name', 'Sin nombre')
            series_list.append((contador, nombre, full_genre, categoria))

# Mostrar las primeras 50
for num, nombre, genero, cat in series_list[:50]:
    print(f"{num}. [{cat.upper()}] {nombre[:70]}")
    print(f"   Género actual: {genero}")
    print()

print(f"\n📊 Total: {contador} series con 'Ciencia ficción' como primer género")
print(f"\nMostrando las primeras 50. Hay {contador - 50} más.")
print("\n💡 Para corregir, dime el número de la serie y el género correcto")
print("   Ejemplo: '1 → Fantasía, Ciencia ficción, Aventura'")
