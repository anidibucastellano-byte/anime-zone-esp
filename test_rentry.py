"""
Test para ver cómo están los enlaces de rentry en el foro
"""

import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Probar con el primer anime
url = "https://animezoneesp.foroactivo.com/t1247-activo-hack-sign-2002-castellano-28-28-dvd-rip-720x400-50-105-mb-mega-pixeldrain-ver-online"

print(f"🔍 Probando: {url}")

try:
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Buscar todos los enlaces
    links = soup.find_all('a', href=True)
    print(f"\n📋 Total enlaces encontrados: {len(links)}")
    
    # Filtrar por rentry
    rentry_links = []
    for link in links:
        href = link.get('href', '')
        text = link.get_text().strip()
        if 'rentry' in href.lower() or 'rentry' in text.lower():
            rentry_links.append((text, href))
    
    print(f"\n🔗 Enlaces con 'rentry': {len(rentry_links)}")
    for text, href in rentry_links[:10]:
        print(f"   Texto: {text[:50]}")
        print(f"   URL: {href[:80]}")
        print()
    
    # Buscar en el texto completo
    text = soup.get_text()
    rentry_matches = re.findall(r'https?://[^\s\"<>]*rentry[^\s\"<>]*', text, re.IGNORECASE)
    print(f"\n🔍 URLs de rentry en texto: {len(rentry_matches)}")
    for match in rentry_matches[:5]:
        print(f"   {match}")
        
except Exception as e:
    print(f"❌ Error: {e}")
