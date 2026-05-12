import json
from pathlib import Path

# Cargar datos del JSON
ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Combinar todos los items con tipo
todos_items = []
for item in data.get('anime', []):
    item['tipo'] = 'anime'
    todos_items.append(item)
for item in data.get('dibujos', []):
    item['tipo'] = 'dibujos'
    todos_items.append(item)
for item in data.get('peliculas', []):
    item['tipo'] = 'peliculas'
    todos_items.append(item)
for item in data.get('series', []):
    item['tipo'] = 'series'
    todos_items.append(item)

print(f'Total items: {len(todos_items)}')

# Verificar si hay items vacíos
empty_items = 0
for i, item in enumerate(todos_items):
    if not item.get('name'):
        empty_items += 1
        print(f'Item {i} sin nombre: {item}')

print(f'Items sin nombre: {empty_items}')

# Mostrar primeros 3 items
for i, item in enumerate(todos_items[:3]):
    print(f'Item {i}: {item.get("name", "SIN NOMBRE")} - Tipo: {item.get("tipo", "SIN TIPO")}')
