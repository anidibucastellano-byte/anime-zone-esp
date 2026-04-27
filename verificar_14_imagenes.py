#!/usr/bin/env python3
import json
import os

temas = ['t1239', 't1469', 't1090', 't1253', 't1494', 't1444', 't1506', 't1320', 't1250', 't1470', 't1209', 't1391', 't581', 't1484']

with open('TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Verificando rutas de las 14 imagenes:')
print('='*80)

for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    for item in data.get(categoria, []):
        href = item.get('href', '')
        for tema in temas:
            if href.startswith(f'/{tema}-'):
                imagen = item.get('imagen', '')
                existe = os.path.exists(imagen.replace('/', os.sep)) if imagen else False
                status = '✅' if existe else '❌'
                print(f'{tema}: {status} {imagen}')
