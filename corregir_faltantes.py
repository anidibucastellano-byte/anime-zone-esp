"""
Script para actualizar las 7 series que no se encontraron automáticamente
"""

import json
from pathlib import Path

def main():
    ruta_top = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
    
    # Cargar TOP.json
    print("📂 Cargando TOP.json...")
    with open(ruta_top, 'r', encoding='utf-8') as f:
        top_data = json.load(f)
    
    # Lista de correcciones manuales: (nombre_busqueda, géneros, año)
    correcciones = [
        # Metalocalipsis
        ("Metalocalipsis", "Comedia, Música", 2006),
        # X-Men
        ("X Men, La Serie Animada", "Acción, Superhéroes", 1992),
        # Boruto
        ("Boruto: Naruto La Pelicula", "Acción, Aventura", 2015),
        # Bubblegum Crisis
        ("Bubblegum Crisis 2032", "Ciencia ficción, Cyberpunk, Acción", 1988),
        # Evangelion películas
        ("Evangelion: 1.11 You Are (Not) Alone", "Ciencia ficción, Mecha, Psicológico", 2007),
        ("Evangelion: 2.22 You Can (Not) Advance", "Ciencia ficción, Mecha, Psicológico", 2009),
        ("Evangelion: 3.33 You Can (Not) Redo", "Ciencia ficción, Mecha, Psicológico", 2012),
        # Patlabor películas
        ("Patlabor: La película", "Ciencia ficción, Mecha, Policíaco", 1989),
        ("Patlabor 2: La película", "Ciencia ficción, Mecha, Policíaco", 1993),
        ("WXIII: Patlabor 3: La película", "Ciencia ficción, Mecha, Policíaco", 2002),
        # Yaiba
        ("La Leyenda del Maestro Espadachin Yaiba", "Acción, Aventura, Comedia, Fantasía, Shōnen", 1993),
    ]
    
    actualizadas = 0
    
    for nombre_busqueda, generos, year in correcciones:
        encontrado = False
        
        # Buscar en todas las categorías
        for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
            if categoria not in top_data:
                continue
                
            for item in top_data[categoria]:
                if 'name' not in item:
                    continue
                    
                nombre_item = item['name']
                
                # Verificar coincidencia
                if nombre_busqueda in nombre_item and item.get('year') == year:
                    # Actualizar géneros
                    item['specificGenre'] = generos
                    item['genre'] = generos.split(',')[0].strip()
                    actualizadas += 1
                    print(f"✅ Actualizado: {nombre_item} -> {generos}")
                    encontrado = True
                    break
            
            if encontrado:
                break
        
        if not encontrado:
            print(f"❌ No encontrado: {nombre_busqueda} ({year})")
    
    # Guardar cambios
    print("\n💾 Guardando cambios...")
    with open(ruta_top, 'w', encoding='utf-8') as f:
        json.dump(top_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Total actualizadas: {actualizadas}/{len(correcciones)}")

if __name__ == "__main__":
    main()
