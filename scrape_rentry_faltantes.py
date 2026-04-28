"""
Script para scrapear solo los enlaces de rentry.co que faltan
"""

import json
import re
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# Credenciales
USERNAME = "Admin"
PASSWORD = "9XsBiygA2CpqgB9"

FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
}

def login():
    """Hacer login en el foro"""
    session = requests.Session()
    
    resp = session.get(LOGIN_URL, headers=headers, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    hidden_fields = {}
    for input_tag in soup.find_all('input', type='hidden'):
        name = input_tag.get('name')
        value = input_tag.get('value', '')
        if name:
            hidden_fields[name] = value
    
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'login': 'Conectarse',
        'redirect': '',
        **hidden_fields
    }
    
    resp = session.post(LOGIN_URL, data=login_data, headers=headers, timeout=30)
    
    if 'Desconectarse' in resp.text or 'Admin' in resp.text:
        print("✅ Login exitoso")
        return session
    return session

def extract_rentry_link(session, url):
    """Extrae el enlace de rentry.co"""
    try:
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar en todos los enlaces
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if 'rentry.co' in href:
                return href
        
        # Buscar en texto
        text = soup.get_text()
        rentry_match = re.search(r'https?://rentry\.co/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
        if rentry_match:
            return rentry_match.group(0)
        
        return None
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    ruta_top = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
    
    print("📂 Cargando TOP.json...")
    with open(ruta_top, 'r', encoding='utf-8') as f:
        top_data = json.load(f)
    
    # Login
    session = login()
    if not session:
        print("❌ No se pudo iniciar sesión")
        return
    
    total_procesados = 0
    total_encontrados = 0
    errores = 0
    
    # Procesar solo los que no tienen rentry_url
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        if categoria not in top_data:
            continue
        
        items_sin_rentry = [item for item in top_data[categoria] if 'rentry_url' not in item and 'url' in item]
        
        if not items_sin_rentry:
            continue
        
        print(f"\n🔍 {categoria.upper()}: {len(items_sin_rentry)} sin rentry...")
        
        for idx, item in enumerate(items_sin_rentry):
            url = item['url']
            nombre = item.get('name', 'Sin nombre')[:40]
            
            if (idx + 1) % 10 == 0:
                print(f"   {idx + 1}/{len(items_sin_rentry)}...")
            
            rentry_link = extract_rentry_link(session, url)
            
            if rentry_link:
                item['rentry_url'] = rentry_link
                total_encontrados += 1
                print(f"   ✅ {nombre}... -> {rentry_link[:40]}...")
            
            total_procesados += 1
            time.sleep(0.5)  # Pausa para no sobrecargar
        
        print(f"   {categoria.upper()} completado - {total_encontrados} nuevos enlaces")
    
    # Guardar
    print(f"\n💾 Guardando... ({total_encontrados} nuevos enlaces)")
    with open(ruta_top, 'w', encoding='utf-8') as f:
        json.dump(top_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Completado:")
    print(f"   Procesados: {total_procesados}")
    print(f"   Nuevos enlaces: {total_encontrados}")
    print(f"   Errores: {errores}")

if __name__ == "__main__":
    main()
