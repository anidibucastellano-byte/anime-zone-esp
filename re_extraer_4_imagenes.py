#!/usr/bin/env python3
"""
Re-extraer 4 imágenes específicas del foro
"""
import json
import os
from extraer_imagenes_foro import ForoImageExtractor

FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"

TEMAS = [
    ("t1176", "anime", "[Activo] Excepción (2022) [Tri-Audio] [8/8] [WebDL-Rip] [1920x1080] [830 MB/1,59 GB] [Mega/Pixeldrain] [Ver Online]"),
    ("t265", "anime", "[Activo] Kare Kano (Él y Ella) (1998) [Tri-Audio] [26/26] [WebDL-Rip] [1438x1080] [640/750 MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1137", "anime", "[Activo] La pequeña Polon (1982) [Dual-Audio] [24/24] [DVD-Rip] [720x544] [365/370 MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1256", "anime", "[Activo] Monster (2004) [Tri-Audio] [74/74] [WebDL-Rip] [960x720] [510/855 MB] [Mega/Pixeldrain] [Ver Online]"),
]

def safe_filename(nombre):
    import re
    nombre = re.sub(r'[<>:"/\\|?*]', '', nombre)
    nombre = nombre[:80]
    return nombre.strip()

def main():
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    extractor = ForoImageExtractor()
    
    login_data = {
        'username': 'Admin',
        'password': '9XsBiygA2CpqgB9',
        'login': '1'
    }
    extractor.session.post(LOGIN_URL, data=login_data)
    print("✅ Login exitoso\n")
    
    descargadas = 0
    
    for tema_id, categoria, nombre in TEMAS:
        url_tema = f"{FORO_URL}/{tema_id}-"
        print(f"🔄 [{tema_id}] {nombre[:50]}...")
        
        imagen_url = extractor.extraer_imagen_de_tema(url_tema)
        
        if imagen_url:
            safe_name = safe_filename(nombre)
            ext = '.png' if 'png' in imagen_url.lower() else '.jpg'
            filename = f"{categoria}_{tema_id.replace('t', '')}_{safe_name}{ext}"
            filepath = os.path.join('images', filename)
            
            if extractor.descargar_imagen(imagen_url, filepath):
                for item in data.get(categoria, []):
                    if item.get('href', '').startswith(f"/{tema_id}-"):
                        item['imagen'] = filepath.replace('\\', '/')
                        item['imagen_url'] = imagen_url
                        descargadas += 1
                        print(f"   ✅ {filepath}")
                        print(f"   URL: {imagen_url[:70]}...")
                        break
            else:
                print(f"   ❌ Error descargando")
        else:
            print(f"   ⚠️ No se encontró imagen")
    
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Total: {descargadas}/4")

if __name__ == "__main__":
    main()
