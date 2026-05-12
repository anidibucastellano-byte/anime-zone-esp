import json
from pathlib import Path

# Cargar el HTML generado para verificar si contiene los datos Disney
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Buscar si hay datos Disney en el JavaScript del HTML
if 'disney' in html_content.lower():
    print('✅ Se encontró "disney" en el HTML')
    
    # Contar cuántas veces aparece
    disney_count = html_content.lower().count('disney')
    print(f'📊 Apariciones de "disney": {disney_count}')
    
    # Buscar la sección de datos JavaScript
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
                
                # Contar items Disney en los datos
                disney_in_data = js_data.lower().count('disney')
                print(f'🎯 Items Disney en datos: {disney_in_data}')
    else:
        print('❌ No se encontró la sección de datos JavaScript')
else:
    print('❌ NO se encontró "disney" en el HTML')
