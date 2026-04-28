"""
Script mejorado para extraer ficha técnica correctamente
Extrae cada campo individualmente y obtiene enlaces reales
"""

import json
import re
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def extract_ficha_tecnica_fixed(url):
    """Extrae la ficha técnica correctamente campo por campo"""
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        ficha_tecnica = {}
        
        # Buscar en todos los posts
        posts = soup.find_all('div', class_='postbody')
        
        for post in posts:
            # Buscar el texto que contiene la ficha técnica
            text = post.get_text()
            
            # Encontrar el bloque de ficha técnica - buscar desde "Género:" hasta el final
            # o hasta que aparezca "Enlaces de descarga"
            ficha_match = re.search(
                r'Género[:\s]+(.+?)(?=Enlaces de descarga|Carpeta Contenedora|Código:|$)',
                text, 
                re.DOTALL | re.IGNORECASE
            )
            
            if ficha_match:
                ficha_text = ficha_match.group(1)
                
                # Extraer cada campo individualmente
                # El patrón es: Campo: valor (hasta el siguiente campo conocido)
                
                campos_orden = [
                    ('genero', r'Género[:\s]+(.+?)(?=\s*Año[:\s]|📅|$)'),
                    ('ano', r'[📅\s]*Año[:\s]+(\d{4})'),
                    ('idioma', r'[🎙️\s]*Idioma[:\s]+(.+?)(?=\s*Subtítulos[:\s]|💾|$)'),
                    ('subtitulos', r'[💾\s]*Subtítulos[:\s]+(.+?)(?=\s*Formato[:\s]|📘|$)'),
                    ('formato', r'[📘\s]*Formato[:\s]+(.+?)(?=\s*Calidad[:\s]|™️|$)'),
                    ('calidad', r'[™️\s]*Calidad[:\s]+(.+?)(?=\s*Resolución[:\s]|🖼️|$)'),
                    ('resolucion', r'[🖼️\s]*Resolución[:\s]+(.+?)(?=\s*Peso/Cap[:\s]|⚙️|$)'),
                    ('peso', r'[⚙️\s]*Peso/Cap(?:acidad)?[:\s]+(.+?)(?=\s*NFO[:\s]|🎞️|$)'),
                    ('temporadas', r'[📺\s]*Temporadas?[:\s]+(.+?)(?=\s*Episodios[:\s]|🎬|$)'),
                    ('episodios', r'[🎬\s]*Episodios?[:\s]+(.+?)(?=\s*NFO[:\s]|🎞️|$)'),
                ]
                
                for key, pattern in campos_orden:
                    match = re.search(pattern, ficha_text, re.IGNORECASE | re.DOTALL)
                    if match:
                        value = match.group(1).strip()
                        # Limpiar el valor - quitar emojis y líneas extras
                        value = re.sub(r'[🎭📅🎙️💾📘™️🖼️⚙️📺🎬🏢👥🎞️📽️\n\r]', ' ', value)
                        value = re.sub(r'\s+', ' ', value).strip()
                        # Limitar longitud
                        if len(value) > 100:
                            value = value[:100]
                        if value and value not in ['Año:', 'Enlace', '-', '']:
                            ficha_tecnica[key] = value
            
            # Extraer enlaces NFO y Trailer de los <a> tags
            links = post.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                link_text = link.get_text().strip().lower()
                
                # NFO/Mediainfo - buscar enlaces a pastebin, mega, etc.
                if 'mediainfo' in link_text or 'nfo' in link_text:
                    if href.startswith('http'):
                        ficha_tecnica['nfo'] = href
                
                # Trailer - buscar YouTube
                if 'trailer' in link_text:
                    if 'youtube' in href or 'youtu.be' in href:
                        ficha_tecnica['trailer'] = href
            
            # Si no encontró NFO/Trailer en el texto del enlace, buscar por URL
            if 'nfo' not in ficha_tecnica:
                for link in links:
                    href = link.get('href', '')
                    if 'pastebin' in href or 'mega.nz' in href or 'mediafire' in href:
                        # Verificar si está cerca de texto "NFO" o "Mediainfo"
                        parent = link.find_parent()
                        if parent:
                            parent_text = parent.get_text().lower()
                            if 'mediainfo' in parent_text or 'nfo' in parent_text:
                                ficha_tecnica['nfo'] = href
                                break
            
            if 'trailer' not in ficha_tecnica:
                for link in links:
                    href = link.get('href', '')
                    if 'youtube' in href or 'youtu.be' in href:
                        parent = link.find_parent()
                        if parent:
                            parent_text = parent.get_text().lower()
                            if 'trailer' in parent_text:
                                ficha_tecnica['trailer'] = href
                                break
        
        return ficha_tecnica
        
    except Exception as e:
        print(f"❌ Error en {url}: {e}")
        return {}

def main():
    ruta_top = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
    
    print("📂 Cargando TOP.json...")
    with open(ruta_top, 'r', encoding='utf-8') as f:
        top_data = json.load(f)
    
    # Backup
    backup_path = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP_backup_ficha_v2.json')
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(top_data, f, indent=2, ensure_ascii=False)
    print(f"💾 Backup: {backup_path}")
    
    total = 0
    actualizadas = 0
    
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        if categoria not in top_data:
            continue
        
        print(f"\n🔍 {categoria.upper()}...")
        items = top_data[categoria]
        
        for idx, item in enumerate(items):
            if 'url' not in item:
                continue
            
            total += 1
            url = item['url']
            nombre = item.get('name', 'Sin nombre')[:50]
            
            if (idx + 1) % 10 == 0:
                print(f"   {idx + 1}/{len(items)}...")
            
            # Extraer ficha técnica
            ficha_nueva = extract_ficha_tecnica_fixed(url)
            
            if ficha_nueva:
                # Reemplazar ficha técnica anterior (que estaba mal)
                item['ficha_tecnica'] = ficha_nueva
                actualizadas += 1
                
                # Mostrar progreso si tiene NFO o Trailer
                extras = []
                if 'nfo' in ficha_nueva:
                    extras.append('NFO')
                if 'trailer' in ficha_nueva:
                    extras.append('Trailer')
                if extras:
                    print(f"   ✅ {nombre}... ({', '.join(extras)})")
            
            time.sleep(0.5)
        
        print(f"   {categoria.upper()} completado")
    
    # Guardar
    print("\n💾 Guardando...")
    with open(ruta_top, 'w', encoding='utf-8') as f:
        json.dump(top_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Completado: {actualizadas}/{total} actualizadas")

if __name__ == "__main__":
    main()
