#!/usr/bin/env python3
import json

with open('progreso_reparacion.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

procesados = len(data['procesados'])
reparadas = data['reparadas']
total = 208
pendientes = total - procesados

print('='*50)
print('PROGRESO REPARACIÓN SINOPSIS')
print('='*50)
print(f'Total a reparar: {total}')
print(f'Procesados: {procesados} ({procesados/total*100:.1f}%)')
print(f'Reparadas: {reparadas}')
print(f'Pendientes: {pendientes}')
print('='*50)
