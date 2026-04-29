#!/usr/bin/env python3
"""Debug script para edición masiva"""

import json
import re

def limpiar_nombre(nombre):
    """Limpiar nombre de formato técnico"""
    if not nombre:
        return 'Sin nombre'
    nombre = re.sub(r'\[.*?\]', '', nombre)
    nombre = nombre.replace('(Activo)', '').replace('(Finalizado)', '')
    nombre = re.sub(r'\(.*?\)', '', nombre)
    nombre = re.sub(r'\s+', ' ', nombre)
    return nombre.strip().lower()

# Cargar el JSON
with open(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Obtener todas las series
todas_series = []
for cat in ['anime', 'dibujos', 'peliculas', 'series']:
    for serie in data.get(cat, []):
        nombre_limpio = limpiar_nombre(serie.get('name', ''))
        todas_series.append({
            'nombre_original': serie.get('name', ''),
            'nombre_limpio': nombre_limpio,
            'categoria': cat
        })

print(f"Total series en catálogo: {len(todas_series)}")
print("\nPrimeras 10 series (nombres limpios):")
for i, s in enumerate(todas_series[:10]):
    print(f"  {i+1}. {s['nombre_limpio'][:60]}")

print("\n\nEscribe algunos nombres de series que NO se encontraron")
print("y veremos por qué no hacen match.")
print("\nEjemplo de formato de entrada:")
print("Nombre Serie (Año)")
print("Género1, Género2")
