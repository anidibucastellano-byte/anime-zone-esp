#!/usr/bin/env python3
"""
Descarga las 3 imágenes faltantes
"""
import json
import os
import requests

IMAGENES = [
    ("t1293", "series", "[Activo] Buffy, cazavampiros (1997) [Castellano] [144/144] [BD-Rip] [1280x720] [1,14/2,47 GB] [Mega/Pixeldrain] [Ver Online]",
     "https://res.cloudinary.com/ddaxoi1n4/image/upload/v1773320592/mis_archivos_elegidos/manual_poster_tmdb_Buffy%2C_cazavampiros.jpg"),
    ("t1671", "series", "[Activo] El príncipe de Bel-Air (1990) [Dual-Audio] [148/148] [BD-Rip] [1440x1080] [265MB/520MB] [Mega/Pixeldrain] [Ver Online]",
     "https://res.cloudinary.com/ddaxoi1n4/image/upload/v1776289261/mis_archivos_elegidos/manual_poster_tmdb_El_pr%C3%ADncipe_de_Bel-Air.jpg"),
    ("t90", "series", "[Activo]Los Fraguel: La diversión continúa (2022) [Castellano] [26/26] [WebDL-Rip] [1920x1080] [585/700 MB] [Mega] [Ver Online]",
     "https://res.cloudinary.com/ddaxoi1n4/image/upload/v1764030371/mis_archivos_elegidos/manual_poster_tmdb_Los_Fraguel_La_diversi%C3%B3n_contin%C3%BAa.jpg"),
]

def safe_filename(nombre):
    import re
    nombre = re.sub(r'[<>:"/\\|?*]', '', nombre)
    nombre = nombre[:80]
    return nombre.strip()

def main():
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    descargadas = 0
    
    for tema_id, categoria, nombre, url in IMAGENES:
        print(f"🔄 {tema_id}: {nombre[:50]}...")
        
        try:
            # Descargar imagen
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                # Guardar imagen
                safe_name = safe_filename(nombre)
                filename = f"{categoria}_{tema_id.replace('t', '')}_{safe_name}.jpg"
                filepath = os.path.join('images', filename)
                
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                
                # Actualizar TOP.json
                for item in data.get(categoria, []):
                    if item.get('href', '').startswith(f"/{tema_id}-"):
                        item['imagen'] = f"images/{filename}"
                        item['imagen_url'] = url
                        descargadas += 1
                        print(f"   ✅ {filepath}")
                        break
            else:
                print(f"   ❌ Error HTTP {resp.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Guardar TOP.json
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Total: {descargadas}/3")

if __name__ == "__main__":
    main()
