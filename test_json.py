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

# Probar generar JSON como lo hace el script
try:
    json_output = json.dumps(todos_items, ensure_ascii=False)
    print(f'✅ JSON generado correctamente: {len(json_output)} caracteres')
    
    # Verificar si el JSON generado es válido
    parsed_back = json.loads(json_output)
    print(f'✅ JSON válido: {len(parsed_back)} items')
    
    # Mostrar primeros 100 caracteres del JSON
    print(f'Primeros 100 caracteres: {json_output[:100]}')
    
except Exception as e:
    print(f'❌ Error generando JSON: {e}')
