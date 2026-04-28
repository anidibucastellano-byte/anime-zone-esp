"""
Test para verificar extracción de rentry.co en URL específica
"""

import requests
import re
from bs4 import BeautifulSoup

# Credenciales
USERNAME = "Admin"
PASSWORD = "9XsBiygA2CpqgB9"

FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"
TEST_URL = "https://animezoneesp.foroactivo.com/t1332-activo-the-cockpit-miniserie-1993-multi-audio-3-3-bd-rip-1016x720-125-131-gb-mega-pixeldrain-ver-online"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
}

def login():
    session = requests.Session()
    
    # Obtener página de login
    resp = session.get(LOGIN_URL, headers=headers, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Extraer campos ocultos
    hidden_fields = {}
    for input_tag in soup.find_all('input', type='hidden'):
        name = input_tag.get('name')
        value = input_tag.get('value', '')
        if name:
            hidden_fields[name] = value
    
    # Login
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'login': 'Conectarse',
        'redirect': '',
        **hidden_fields
    }
    
    resp = session.post(LOGIN_URL, data=login_data, headers=headers, timeout=30)
    return session

def extract_rentry(session, url):
    try:
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"\n🔍 Analizando: {url}")
        print(f"Status: {response.status_code}")
        
        # Buscar todos los enlaces
        links = soup.find_all('a', href=True)
        print(f"\n📋 Total enlaces: {len(links)}")
        
        # Filtrar por rentry o ver online
        rentry_links = []
        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()
            lower_href = href.lower()
            lower_text = text.lower()
            
            if 'rentry' in lower_href or 'rentry' in lower_text:
                rentry_links.append((text[:50], href))
            elif 'ver online' in lower_text and ('http' in lower_href or 'rentry' in lower_href):
                rentry_links.append((text[:50], href))
        
        print(f"\n🔗 Enlaces encontrados ({len(rentry_links)}):")
        for text, href in rentry_links[:10]:
            print(f"   Texto: '{text}'")
            print(f"   URL: {href[:100]}")
            print()
        
        # Buscar en texto
        text = soup.get_text()
        rentry_matches = re.findall(r'https?://[^\s\"<>]*rentry[^\s\"<>]*', text, re.IGNORECASE)
        print(f"\n🔍 URLs rentry en texto: {len(rentry_matches)}")
        for match in rentry_matches[:5]:
            print(f"   {match}")
        
        return rentry_links[0][1] if rentry_links else None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Ejecutar
session = login()
if session:
    result = extract_rentry(session, TEST_URL)
    if result:
        print(f"\n✅ Enlace encontrado: {result}")
    else:
        print("\n❌ No se encontró enlace de rentry")
else:
    print("❌ No se pudo iniciar sesión")
