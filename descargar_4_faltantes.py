#!/usr/bin/env python3
"""
Descarga las 4 imágenes faltantes
"""
import json
import os
import requests

IMAGENES = [
    ("t1714", "series", "[Activo] La Hora de José Mota (2009) [Castellano] [40/40] [WebDL-Rip] [1920x1080] [595MB/1,07GB] [Mega/Pixeldrain] [Ver Online]",
     "https://res.cloudinary.com/ddaxoi1n4/image/upload/v1776468034/mis_archivos_elegidos/manual_poster_tmdb_La_Hora_de_Jos%C3%A9_Mota.jpg"),
    ("t582", "series", "[Activo] Xena, la princesa guerrera (1995) [Castellano] [134/134] [WebDL-Rip] [640x480] [155/320 MB] [Mega/Pixeldrain] [Ver Online]",
     "https://res.cloudinary.com/ddaxoi1n4/image/upload/v1769526315/mis_archivos_elegidos/manual_poster_tmdb_Xena%2C_la_princesa_guerrera.jpg"),
    ("t568", "series", "[Activo] Hércules: Sus viajes legendarios (1995) [Castellano] [111/111] [DVD-Rip] [512x384] [300/445 MB] [Mega/Pixeldrain] [Ver Online]",
     "https://res.cloudinary.com/ddaxoi1n4/image/upload/v1769473371/mis_archivos_elegidos/manual_poster_tmdb_H%C3%A9rcules_Sus_viajes_legendarios.jpg"),
    ("t482", "series", "[Activo] Historias de la cripta (1989) [Dual-Audio] [93/93] [720x576] [285 MB / 1,23 GB] [Mega/Pixeldrain] [Ver Online]",
     "https://res.cloudinary.com/ddaxoi1n4/image/upload/v1769022404/mis_archivos_elegidos/manual_poster_tmdb_Historias_de_la_cripta.jpg"),
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
                        print(f"   ✅ Descargada: {filepath}")
                        break
            else:
                print(f"   ❌ Error HTTP {resp.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Guardar TOP.json
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Total descargadas: {descargadas}/4")

if __name__ == "__main__":
    main()
