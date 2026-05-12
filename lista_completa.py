#!/usr/bin/env python3
"""
Generar lista completa del catálogo AnimeZoneESP
"""

import json
import re
from pathlib import Path

def limpiar_nombre(nombre):
    """Limpiar nombre de formato técnico"""
    if not nombre:
        return 'Sin nombre'
    nombre = re.sub(r'\[.*?\]', '', nombre)
    nombre = nombre.replace('(Activo)', '').replace('(Finalizado)', '')
    nombre = re.sub(r'\(.*?\)', '', nombre)
    nombre = re.sub(r'\s+', ' ', nombre)
    return nombre.strip()

def main():
    """Generar lista completa del catálogo"""
    ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
    
    # Cargar datos
    with open(ruta_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extraer todas las categorías
    categorias = {
        'Anime': data.get('anime', []),
        'Dibujos': data.get('dibujos', []),
        'Películas': data.get('peliculas', []),
        'Series': data.get('series', [])
    }
    
    print('📊 CATÁLOGO COMPLETO ANIMEZONEESP')
    print('=' * 60)
    
    # Mostrar por categoría
    for cat_name, items in categorias.items():
        print(f'\n🎬 {cat_name.upper()}: {len(items)} títulos')
        print('-' * 40)
        
        # Extraer nombres limpios
        nombres = []
        for item in items:
            nombre = item.get('name', '')
            nombre_limpio = limpiar_nombre(nombre)
            nombres.append(nombre_limpio)
        
        # Ordenar alfabéticamente
        nombres_ordenados = sorted(nombres, key=lambda x: x.lower())
        
        # Mostrar todos los nombres
        for i, nombre in enumerate(nombres_ordenados, 1):
            print(f'{i:3d}. {nombre}')
    
    # Totales
    total_general = sum(len(items) for items in categorias.values())
    print(f'\n📈 TOTAL GENERAL: {total_general} títulos')
    print('=' * 60)
    
    # Estadísticas adicionales
    print(f'\n📋 RESUMEN:')
    for cat_name, items in categorias.items():
        porcentaje = (len(items) / total_general) * 100
        print(f'  {cat_name}: {len(items):4d} títulos ({porcentaje:5.1f}%)')

if __name__ == '__main__':
    main()
