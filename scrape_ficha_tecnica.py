"""
Script para re-scrapear la ficha técnica de todas las series del foro
Extrae: Mediainfo (enlace real) y Trailer (enlace de YouTube)
"""

import json
import re
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# Headers para simular navegador
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_ficha_tecnica(url):
    """Extrae la ficha técnica de una página del foro"""
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        ficha_tecnica = {}
        
        # Buscar el bloque de ficha técnica
        # Normalmente está en un post con clase "postbody" o similar
        posts = soup.find_all('div', class_='postbody')
        
        for post in posts:
            text = post.get_text()
            
            # Extraer campos de la ficha técnica
            patterns = {
                'genero': r'Género:\s*([^\n]+)',
                'ano': r'[📅\s]*Año:\s*([^\n]+)',
                'idioma': r'[🎙️\s]*Idioma:\s*([^\n]+)',
                'subtitulos': r'[💾\s]*Subtítulos:\s*([^\n]+)',
                'formato': r'[📘\s]*Formato:\s*([^\n]+)',
                'calidad': r'[™️\s]*Calidad:\s*([^\n]+)',
                'resolucion': r'[🖼️\s]*Resolución:\s*([^\n]+)',
                'peso': r'[⚙️\s]*Peso/Cap(?:acidad)?:\s*([^\n]+)',
                'temporadas': r'[📺\s]*Temporadas?:\s*([^\n]+)',
                'episodios': r'[🎬\s]*Episodios?:\s*([^\n]+)',
                'estudio': r'[🏢\s]*Estudio:\s*([^\n]+)',
                'director': r'[🎬\s]*Director:\s*([^\n]+)',
                'reparto': r'[👥\s]*Reparto:\s*([^\n]+)',
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Limpiar emojis y espacios extra
                    value = re.sub(r'[📅🎙️💾📘™️🖼️⚙️📺🎬🏢👥]', '', value).strip()
                    if value and value not in ['Año:', 'Enlace', '-', '']:
                        ficha_tecnica[key] = value
            
            # Extraer enlace de NFO/Mediainfo
            # Buscar enlaces a pastebin, mega, etc. cerca de "NFO" o "Mediainfo"
            nfo_patterns = [
                r'NFO[\s:]+<a[^>]+href="([^"]+)"',
                r'Mediainfo[\s:]+<a[^>]+href="([^"]+)"',
                r'🎞️\s*NFO[\s:]+\[url=([^\]]+)\]',
                r'\[url=([^\]]+)\].*?(?:mediainfo|nfo)',
            ]
            
            for pattern in nfo_patterns:
                match = re.search(pattern, str(post), re.IGNORECASE)
                if match:
                    nfo_link = match.group(1).strip()
                    if nfo_link.startswith('http'):
                        ficha_tecnica['nfo'] = nfo_link
                        break
            
            # También buscar enlaces en el texto plano
            if 'nfo' not in ficha_tecnica:
                # Buscar cualquier enlace después de NFO o Mediainfo
                nfo_match = re.search(r'(?:NFO|Mediainfo)[\s:]+(?:\[url=)?(https?://[^\s\]]+)', text, re.IGNORECASE)
                if nfo_match:
                    ficha_tecnica['nfo'] = nfo_match.group(1).strip()
            
            # Extraer enlace de Trailer (YouTube)
            trailer_patterns = [
                r'Trailer[\s:]+<a[^>]+href="([^"]+)"',
                r'📽️\s*Trailer[\s:]+\[url=([^\]]+)\]',
                r'\[url=([^\]]+)\].*?trailer',
                r'(?:Trailer)[\s:]+(?:\[url=)?(https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^\s\]]+)',
            ]
            
            for pattern in trailer_patterns:
                match = re.search(pattern, str(post), re.IGNORECASE)
                if match:
                    trailer_link = match.group(1).strip()
                    if 'youtube' in trailer_link or 'youtu.be' in trailer_link:
                        ficha_tecnica['trailer'] = trailer_link
                        break
            
            # Buscar en texto plano también
            if 'trailer' not in ficha_tecnica:
                trailer_match = re.search(r'(?:Trailer)[\s:]+(?:\[url=)?(https?://[^\s\]]+)', text, re.IGNORECASE)
                if trailer_match and ('youtube' in trailer_match.group(1) or 'youtu.be' in trailer_match.group(1)):
                    ficha_tecnica['trailer'] = trailer_match.group(1).strip()
            
            # Buscar todos los enlaces en el post
            links = post.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                link_text = link.get_text().lower()
                
                # Si el texto del enlace contiene "mediainfo" o "nfo"
                if 'mediainfo' in link_text or 'nfo' in link_text:
                    if href.startswith('http'):
                        ficha_tecnica['nfo'] = href
                
                # Si el texto del enlace contiene "trailer"
                if 'trailer' in link_text:
                    if 'youtube' in href or 'youtu.be' in href:
                        ficha_tecnica['trailer'] = href
        
        return ficha_tecnica
        
    except Exception as e:
        print(f"❌ Error extrayendo {url}: {e}")
        return {}

def main():
    ruta_top = Path('TOP.json')
    
    # Cargar TOP.json
    print("📂 Cargando TOP.json...")
    with open(ruta_top, 'r', encoding='utf-8') as f:
        top_data = json.load(f)
    
    # Crear backup
    backup_path = Path('TOP_backup_ficha.json')
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(top_data, f, indent=2, ensure_ascii=False)
    print(f"💾 Backup creado: {backup_path}")
    
    total_actualizadas = 0
    total_errores = 0
    
    # Procesar cada categoría
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        if categoria not in top_data:
            continue
        
        print(f"\n🔍 Procesando {categoria.upper()}...")
        items = top_data[categoria]
        
        for idx, item in enumerate(items):
            if 'url' not in item:
                continue
            
            url = item['url']
            nombre = item.get('name', 'Sin nombre')
            
            # Mostrar progreso cada 10 items
            if (idx + 1) % 10 == 0:
                print(f"   {idx + 1}/{len(items)}...")
            
            # Extraer ficha técnica
            ficha_nueva = extract_ficha_tecnica(url)
            
            if ficha_nueva:
                # Fusionar con ficha técnica existente (si hay)
                if 'ficha_tecnica' not in item:
                    item['ficha_tecnica'] = {}
                
                # Actualizar solo campos que tengan valor
                for key, value in ficha_nueva.items():
                    if value and value.strip():
                        item['ficha_tecnica'][key] = value
                
                total_actualizadas += 1
                
                # Mostrar si encontró NFO o Trailer
                if 'nfo' in ficha_nueva or 'trailer' in ficha_nueva:
                    extras = []
                    if 'nfo' in ficha_nueva:
                        extras.append('NFO')
                    if 'trailer' in ficha_nueva:
                        extras.append('Trailer')
                    print(f"   ✅ {nombre[:50]}... ({', '.join(extras)})")
            else:
                total_errores += 1
            
            # Pausa para no sobrecargar el servidor
            time.sleep(0.5)
        
        print(f"   {categoria.upper()} completado")
    
    # Guardar cambios
    print("\n💾 Guardando cambios...")
    with open(ruta_top, 'w', encoding='utf-8') as f:
        json.dump(top_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Proceso completado:")
    print(f"   • Actualizadas: {total_actualizadas}")
    print(f"   • Errores: {total_errores}")
    print(f"   • Backup: {backup_path}")

if __name__ == "__main__":
    main()
