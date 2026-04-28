"""
Script para scrapear enlaces de rentry.co haciendo login en el foro
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

# URLs del foro
FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def login():
    """Hacer login en el foro y devolver la sesión"""
    session = requests.Session()
    
    print("🔐 Iniciando sesión...")
    
    # Primero obtener la página de login para extraer tokens
    resp = session.get(LOGIN_URL, headers=headers, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Extraer campos ocultos si existen
    hidden_fields = {}
    for input_tag in soup.find_all('input', type='hidden'):
        name = input_tag.get('name')
        value = input_tag.get('value', '')
        if name:
            hidden_fields[name] = value
    
    # Datos de login
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'login': 'Conectarse',
        'redirect': '',
        **hidden_fields
    }
    
    # Hacer POST al login
    resp = session.post(LOGIN_URL, data=login_data, headers=headers, timeout=30)
    
    if 'Desconectarse' in resp.text or 'Admin' in resp.text or 'Panel' in resp.text:
        print("✅ Login exitoso")
        return session
    else:
        print("❌ Error en login - posiblemente requiere verificación adicional")
        # Intentar de todos modos
        return session

def extract_rentry_link(session, url):
    """Extrae el enlace de rentry.co de una página del foro (con login)"""
    try:
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar en todos los enlaces
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            link_text = link.get_text().strip().lower()
            
            # Buscar enlaces a rentry.co
            if 'rentry.co' in href:
                return href
            
            # Buscar si el texto contiene referencias a rentry
            if 'rentry' in link_text or 'ver online' in link_text:
                if 'rentry' in href:
                    return href
        
        # Buscar en el texto completo con regex
        text = soup.get_text()
        rentry_match = re.search(r'https?://rentry\.co/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
        if rentry_match:
            return rentry_match.group(0)
        
        # Buscar cualquier enlace que pueda ser de rentry
        for link in links:
            href = link.get('href', '')
            if 'rentry' in href.lower():
                return href
        
        return None
        
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
    
    # Login
    session = login()
    if not session:
        print("❌ No se pudo iniciar sesión")
        return
    
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
            
            # Mostrar progreso cada 10
            if (idx + 1) % 10 == 0:
                print(f"   {idx + 1}/{len(items)}... ({encontrados} encontrados)")
            
            # Extraer enlace de rentry
            rentry_link = extract_rentry_link(session, url)
            
            if rentry_link:
                item['rentry_url'] = rentry_link
                encontrados += 1
                print(f"   ✅ {nombre}... -> {rentry_link[:50]}...")
            
            time.sleep(0.3)  # Pausa más corta porque estamos logueados
        
        print(f"   {categoria.upper()} completado - {encontrados} enlaces rentry")
    
    # Guardar
    print("\n💾 Guardando...")
    with open(ruta_top, 'w', encoding='utf-8') as f:
        json.dump(top_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Completado: {encontrados}/{total} con enlaces de rentry.co")
    
    # Guardar lista de los que no tienen rentry
    sin_rentry = []
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        if categoria not in top_data:
            continue
        for item in top_data[categoria]:
            if 'rentry_url' not in item:
                sin_rentry.append({
                    'name': item.get('name', ''),
                    'url': item.get('url', ''),
                    'categoria': categoria
                })
    
    with open('sin_rentry.json', 'w', encoding='utf-8') as f:
        json.dump(sin_rentry, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Guardada lista de {len(sin_rentry)} items sin enlace rentry en sin_rentry.json")

if __name__ == "__main__":
    main()
