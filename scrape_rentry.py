"""
Script para scrapear enlaces de rentry.co de cada tema del foro
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

def extract_rentry_link(url):
    """Extrae el enlace de rentry.co de una página del foro"""
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar enlaces a rentry.co
        rentry_link = None
        
        # Buscar en todos los enlaces
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            link_text = link.get_text().strip().lower()
            
            # Buscar enlaces a rentry.co
            if 'rentry.co' in href or 'rentry' in href:
                rentry_link = href
                break
            
            # También buscar si el texto del enlace contiene "ver online", "online", etc.
            if any(x in link_text for x in ['ver online', 'online', 'ver', 'rentry']):
                if 'rentry' in href:
                    rentry_link = href
                    break
        
        # Si no encontró en <a>, buscar en el texto
        if not rentry_link:
            text = soup.get_text()
            rentry_match = re.search(r'https?://rentry\.co/[^\s\]"]+', text)
            if rentry_match:
                rentry_link = rentry_match.group(0)
        
        return rentry_link
        
    except Exception as e:
        print(f"❌ Error en {url}: {e}")
        return None

def main():
    ruta_top = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
    
    print("📂 Cargando TOP.json...")
    with open(ruta_top, 'r', encoding='utf-8') as f:
        top_data = json.load(f)
    
    # Backup
    backup_path = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP_backup_rentry.json')
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(top_data, f, indent=2, ensure_ascii=False)
    print(f"💾 Backup: {backup_path}")
    
    total = 0
    encontrados = 0
    
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
            
            # Mostrar progreso
            if (idx + 1) % 10 == 0:
                print(f"   {idx + 1}/{len(items)}...")
            
            # Extraer enlace de rentry
            rentry_link = extract_rentry_link(url)
            
            if rentry_link:
                item['rentry_url'] = rentry_link
                encontrados += 1
                print(f"   ✅ {nombre}... -> {rentry_link[:60]}...")
            
            time.sleep(0.5)
        
        print(f"   {categoria.upper()} completado")
    
    # Guardar
    print("\n💾 Guardando...")
    with open(ruta_top, 'w', encoding='utf-8') as f:
        json.dump(top_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Completado: {encontrados}/{total} con enlaces de rentry.co")

if __name__ == "__main__":
    main()
