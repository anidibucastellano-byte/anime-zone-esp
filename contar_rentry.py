"""
Script para contar cuántos enlaces de rentry.co hay en el JSON
"""

import json
from pathlib import Path

ruta_top = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')

with open(ruta_top, 'r', encoding='utf-8') as f:
    top_data = json.load(f)

con_rentry = 0
sin_rentry = 0
total = 0

por_categoria = {}

for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
    if categoria not in top_data:
        continue
    
    items = top_data[categoria]
    cat_con = sum(1 for item in items if 'rentry_url' in item)
    cat_sin = sum(1 for item in items if 'rentry_url' not in item)
    
    por_categoria[categoria] = {
        'con': cat_con,
        'sin': cat_sin,
        'total': len(items)
    }
    
    con_rentry += cat_con
    sin_rentry += cat_sin
    total += len(items)

print("📊 RESUMEN DE ENLACES RENTRY.CO")
print("=" * 50)
print()

for cat, datos in por_categoria.items():
    porcentaje = (datos['con'] / datos['total'] * 100) if datos['total'] > 0 else 0
    print(f"{cat.upper()}:")
    print(f"   ✅ Con rentry: {datos['con']}")
    print(f"   ❌ Sin rentry: {datos['sin']}")
    print(f"   📊 Total: {datos['total']} ({porcentaje:.1f}%)")
    print()

print("=" * 50)
print(f"TOTALES:")
print(f"   ✅ Con rentry: {con_rentry}")
print(f"   ❌ Sin rentry: {sin_rentry}")
print(f"   📊 Total items: {total}")
print(f"   📈 Cobertura: {(con_rentry/total*100):.1f}%")
