import json
from pathlib import Path

# Cargar el HTML generado para verificar si contiene los datos
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Verificar si hay datos en el HTML
if 'const allItems' in html_content:
    print('✅ Se encontró la sección de datos JavaScript')
    
    # Extraer los datos JavaScript
    start = html_content.find('const allItems')
    if start != -1:
        # Buscar el final del array
        end = html_content.find('];', start)
        if end != -1:
            js_data = html_content[start:end+2]
            print(f'📏 Longitud de datos JavaScript: {len(js_data)} caracteres')
            
            # Contar items totales
            total_items = js_data.count('name:')
            print(f'📊 Total items en datos: {total_items}')
            
            # Verificar categorías
            categories = ['anime', 'dibujos', 'peliculas', 'series']
            for cat in categories:
                count = js_data.lower().count(f'"{cat}"')
                print(f'📁 {cat.upper()}: {count} items')
else:
    print('❌ No se encontró la sección de datos JavaScript')

# Verificar si hay funciones JavaScript importantes
functions = ['showTab', 'applyFilters', 'sortItems']
for func in functions:
    if f'function {func}' in html_content or f'function {func}' in html_content:
        print(f'✅ Función {func} encontrada')
    else:
        print(f'❌ Función {func} NO encontrada')
