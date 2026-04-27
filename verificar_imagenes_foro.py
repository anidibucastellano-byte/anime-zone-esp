#!/usr/bin/env python3
"""
Script para verificar dónde están las imágenes en los temas del foro
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"

def main():
    session = requests.Session()
    
    # Login
    login_data = {
        'username': 'Admin',
        'password': '9XsBiygA2CpqgB9',
        'login': '1'
    }
    
    resp = session.post(LOGIN_URL, data=login_data)
    if 'Admin' not in resp.text and 'logout' not in resp.text.lower():
        print("❌ Error en login")
        return
    
    print("✅ Login exitoso")
    
    # Tema de ejemplo
    tema_url = 'https://animezoneesp.foroactivo.com/t1860-activo-las-nuevas-aventuras-de-winnie-the-pooh-1988-castellano-53-55-tv-rip-640x480-180mb-150gb-mega-pixeldrain-ver-online#4509'
    
    resp = session.get(tema_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    print(f"\n🔍 Analizando: {tema_url}")
    print(f"HTML length: {len(resp.text)} chars")
    
    # Buscar todas las imágenes
    imgs = soup.find_all('img')
    print(f"\n📸 Total imágenes encontradas: {len(imgs)}")
    
    # Filtrar imágenes relevantes (no iconos/smileys)
    relevantes = []
    for img in imgs:
        src = img.get('src', '')
        if src and not any(x in src.lower() for x in ['icon', 'smiley', 'avatar', 'rank', 'mini']):
            if src.startswith('http') or src.startswith('/'):
                relevantes.append(img)
    
    print(f"\n📸 Imágenes relevantes: {len(relevantes)}")
    
    for i, img in enumerate(relevantes[:5]):
        src = img.get('src', '')
        print(f"\n  [{i+1}] SRC: {src[:80]}...")
        print(f"      CLASS: {img.get('class', 'N/A')}")
        print(f"      WIDTH: {img.get('width', 'N/A')}")
        print(f"      HEIGHT: {img.get('height', 'N/A')}")
        
        # Ver parent
        parent = img.parent
        print(f"      PARENT: {parent.name}")
        if parent.name == 'a':
            href = parent.get('href', '')
            print(f"      LINK: {href[:80]}...")
    
    # Buscar también en enlaces
    print("\n\n🔗 Buscando imágenes en enlaces...")
    links = soup.find_all('a')
    imagenes_en_links = []
    for link in links:
        href = link.get('href', '')
        if any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            imagenes_en_links.append(href)
    
    print(f"Enlaces a imágenes: {len(imagenes_en_links)}")
    for img_link in imagenes_en_links[:3]:
        print(f"  - {img_link[:80]}...")

if __name__ == "__main__":
    main()
