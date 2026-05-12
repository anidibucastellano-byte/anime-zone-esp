import json
from pathlib import Path

# Cargar datos del JSON
ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Buscar items con género Disney
disney_items = []

# Buscar en todas las categorías
for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    items = data.get(categoria, [])
    for item in items:
        genre = item.get('genre', '')
        specific_genre = item.get('specificGenre', '')
        
        # Verificar si contiene 'Disney' en cualquier campo de género
        has_disney = False
        if isinstance(genre, str) and 'disney' in genre.lower():
            has_disney = True
        elif isinstance(genre, list) and any('disney' in str(g).lower() for g in genre):
            has_disney = True
            
        if isinstance(specific_genre, str) and 'disney' in specific_genre.lower():
            has_disney = True
        elif isinstance(specific_genre, list) and any('disney' in str(g).lower() for g in specific_genre):
            has_disney = True
        
        if has_disney:
            disney_items.append({
                'name': item.get('name', ''),
                'categoria': categoria,
                'genre': genre,
                'specificGenre': specific_genre
            })

print(f'Total items con género Disney: {len(disney_items)}')
print()

# Agrupar por categoría
categorias_disney = {}
for item in disney_items:
    cat = item['categoria']
    if cat not in categorias_disney:
        categorias_disney[cat] = []
    categorias_disney[cat].append(item)

for cat, items in categorias_disney.items():
    print(f'{cat.upper()}: {len(items)} items')
    for item in items[:3]:  # Mostrar primeros 3
        print(f'  - {item["name"]}')
    if len(items) > 3:
        print(f'  ... y {len(items) - 3} más')
    print()
