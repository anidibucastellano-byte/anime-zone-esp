"""Verificar cuáles items tienen ficha técnica vacía"""
import json

with open('TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Items con ficha_tecnica vacía o sin campos útiles:')
print('=' * 60)

errores = []
for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in data:
        continue
    
    for item in data[categoria]:
        ficha = item.get('ficha_tecnica', {})
        
        # Verificar si existe pero está vacía o solo tiene campos vacíos
        if ficha:
            campos_validos = [k for k, v in ficha.items() if v and str(v).strip() not in ['', 'Año:', 'Enlace', 'N/A']]
            if not campos_validos:
                errores.append({
                    'categoria': categoria,
                    'name': item.get('name', 'Sin nombre'),
                    'url': item.get('url', '')
                })
        else:
            errores.append({
                'categoria': categoria,
                'name': item.get('name', 'Sin nombre'),
                'url': item.get('url', '')
            })

# Mostrar todos
for i, err in enumerate(errores):
    print(f"[{i+1}] [{err['categoria'].upper()}] {err['name'][:50]}...")
    print(f"    URL: {err['url']}")
    print()

print(f'Total con errores: {len(errores)}')
