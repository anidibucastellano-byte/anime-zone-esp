#!/usr/bin/env python3
"""
Re-extraer las 15 imágenes que faltan del foro
"""
import json
import os
from extraer_imagenes_foro import ForoImageExtractor

FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"

# Lista de los 15 items que faltan
TEMAS_FALTANTES = [
    ("t1236", "anime", "[Activo] Boogiepop Phantom (2000) [Dual-Audio] [12/12] [DVD-Rip] [960x720] [420/595 MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1239", "anime", "[Activo] Don Drácula (1982) [Castellano] [8/8] [TV-RIP] [360x272] [140 MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1469", "anime", "[Activo] Dos fuera de serie, Juana y Sergio (1984) [Castellano] [58/58] [DVD-Rip] [640x480] [280MB/510MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1090", "anime", "[Activo] Dota: Sangre de dragón (2021) [Tri-Audio] [24/24] [WebDL-Rip] [1920x1080] [995 MB/1,15 GB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1253", "anime", "[Activo] El amor a través de un prisma (2026) [Multi-audio] [20/20] [WebDL-Rip] [1920x1080] [1,75/3,18 GB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1494", "anime", "[Activo] El mundo de Rumiko (1991) [Dual-Audio] [05/05] [DVD-Rip] [640x480] [465MB/785MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1444", "anime", "[Activo] ¡Estás arrestado! (1999) [Tri-Audio] [51/51+01] [DVD-Rip] [960x720] [230MB/370MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1506", "anime", "[Activo] Gunslinger Girl (2003) [Dual-Audio] [13/13] [BD-Rip] [1920x1080] [735MB/1,02GB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1320", "anime", "[Activo] JoJo's Bizarre Adventure (2012) [Tri-Audio] [190/190] [WebDL-Rip] [1920x1080] [380/620 MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1250", "anime", "[Activo] La melodía del olvido (2004) [Castellano] [24/24] [DVD-Rip] [640x480] [45/100 MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1470", "anime", "[Activo] New Getter Robo (2004) [Dual-Audio] [13/13] [BD-Rip] [1440x1080] [645MB/935MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1209", "anime", "[Activo] Niña del demonio (2022) [Dual-Audio] [10/10] [WebDL-Rip] [1920x1080] [545/625 MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1391", "anime", "[Activo] Rin: Las Hijas de Mnemosyne (Miniserie) (2008) [Tri-Audio] [06/06] [WebDL-Rip] [1920x1080] [2,55GB/2,72GB] [Mega/Pixeldrain] [Ver Online]"),
    ("t581", "anime", "[Activo] Utena, la chica revolucionaria (1997) [Castellano] [39/39] [WebDL-Rip] [1280x720] [100/285 MB] [Mega/Pixeldrain] [Ver Online]"),
    ("t1484", "anime", "[Activo] Wolf's Rain (2003) [Castellano] [30/30] [DVD-Rip] [640x480] [60MB/100MB] [Mega/Pixeldrain] [Ver Online]"),
]

def safe_filename(nombre):
    """Crear nombre de archivo seguro"""
    import re
    nombre = re.sub(r'[<>:"/\\|?*]', '', nombre)
    nombre = nombre[:80]
    return nombre.strip()

def main():
    # Cargar TOP.json
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Inicializar extractor
    extractor = ForoImageExtractor()
    
    # Login
    login_data = {
        'username': 'Admin',
        'password': '9XsBiygA2CpqgB9',
        'login': '1'
    }
    extractor.session.post(LOGIN_URL, data=login_data)
    print("✅ Login exitoso\n")
    
    descargadas = 0
    
    for tema_id, categoria, nombre in TEMAS_FALTANTES:
        url_tema = f"{FORO_URL}/{tema_id}-"
        print(f"🔄 [{tema_id}] {nombre[:50]}...")
        
        # Extraer imagen
        imagen_url = extractor.extraer_imagen_de_tema(url_tema)
        
        if imagen_url:
            # Descargar imagen
            safe_name = safe_filename(nombre)
            ext = '.png' if 'png' in imagen_url.lower() else '.jpg'
            filename = f"{categoria}_{tema_id.replace('t', '')}_{safe_name}{ext}"
            filepath = os.path.join('images', filename)
            
            if extractor.descargar_imagen(imagen_url, filepath):
                # Actualizar TOP.json
                for item in data.get(categoria, []):
                    if item.get('href', '').startswith(f"/{tema_id}-"):
                        item['imagen'] = filepath.replace('\\', '/')
                        item['imagen_url'] = imagen_url
                        descargadas += 1
                        print(f"   ✅ Imagen guardada: {filepath}")
                        break
            else:
                print(f"   ❌ Error descargando imagen")
        else:
            print(f"   ⚠️ No se encontró imagen en el tema")
    
    # Guardar TOP.json
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Total descargadas: {descargadas}/{len(TEMAS_FALTANTES)}")

if __name__ == "__main__":
    main()
