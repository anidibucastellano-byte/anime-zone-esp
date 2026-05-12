import json
from pathlib import Path

# Cargar datos del JSON
ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Verificar estructura de algunos items Disney
disney_items = []
for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    items = data.get(categoria, [])
    for item in items:
        genre = item.get('genre', '')
        specific_genre = item.get('specificGenre', '')
        
        has_disney = False
        if isinstance(genre, str) and 'disney' in genre.lower():
            has_disney = True
        elif isinstance(specific_genre, str) and 'disney' in specific_genre.lower():
            has_disney = True
        
        if has_disney:
            disney_items.append({
                'name': item.get('name', ''),
                'categoria': categoria,
                'genre': genre,
                'specificGenre': specific_genre,
                'tipo': item.get('tipo', item.get('type', ''))
            })

print(f'Total items Disney: {len(disney_items)}')
print()

# Verificar estructura de los primeros 3
for i, item in enumerate(disney_items[:3]):
    print(f'Item {i+1}: {item["name"]}')
    print(f'  categoria: {item["categoria"]}')
    print(f'  tipo: "{item["tipo"]}"')
    print(f'  genre: "{item["genre"]}"')
    print(f'  specificGenre: "{item["specificGenre"]}"')
    print()
