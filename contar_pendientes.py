#!/usr/bin/env python3
import json

with open('progreso_reparacion.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

procesados = len(data['procesados'])
reparadas = data['reparadas']
total = 208
pendientes = total - procesados

print('='*60)
print('ESTADO DE REPARACIÓN DE SINOPSIS')
print('='*60)
print(f'📊 Total sinopsis incompletas: {total}')
print(f'✅ Ya procesadas: {procesados}')
print(f'🔧 Sinopsis reparadas: {reparadas}')
print(f'⏳ Pendientes: {pendientes}')
print(f'📈 Progreso: {procesados/total*100:.1f}%')
print('='*60)

if pendientes > 0:
    print(f'\n⚠️ Faltan {pendientes} sinopsis por procesar')
else:
    print('\n✅ ¡TODAS LAS SINOPSIS PROCESADAS!')
