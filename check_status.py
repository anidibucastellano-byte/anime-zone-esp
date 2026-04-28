import json
with open('progreso_reparacion.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
procesados = len(d['procesados'])
total = 208
print(f'PROGRESO: {procesados}/{total} ({procesados/total*100:.1f}%)')
print(f'Reparadas: {d["reparadas"]}')
print(f'Pendientes: {total - procesados}')
if procesados >= total:
    print('✅ COMPLETADO')
else:
    print('⏳ En progreso...')
