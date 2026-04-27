#!/usr/bin/env python3
"""
Diagnóstico para encontrar dónde están las imágenes de portada en los temas
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"

def analizar_tema(session, tema_url, nombre):
    """Analizar un tema específico"""
    print(f"\n{'='*60}")
    print(f"Analizando: {nombre}")
    print(f"URL: {tema_url}")
    print('='*60)
    
    resp = session.get(tema_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Buscar posts específicos
    posts = soup.find_all(['div', 'td'], class_=lambda x: x and any(c in str(x).lower() for c in ['post', 'postbody', 'post--', 'entry-content']))
    print(f"\n📄 Posts encontrados: {len(posts)}")
    
    # Analizar primer post en detalle
    if posts:
        first_post = posts[0]
        print("\n🔍 Primer post:")
        print(f"   Clases: {first_post.get('class', 'N/A')}")
        print(f"   ID: {first_post.get('id', 'N/A')}")
        
        # Buscar imágenes en el primer post
        imgs = first_post.find_all('img')
        print(f"\n📸 Imágenes en primer post: {len(imgs)}")
        
        for i, img in enumerate(imgs[:5]):
            src = img.get('src', '')
            if src and not any(x in src.lower() for x in ['icon', 'smiley', 'avatar', 'mini']):
                print(f"\n   [{i+1}] SRC: {src[:80]}")
                print(f"        WIDTH: {img.get('width', 'N/A')}")
                print(f"        HEIGHT: {img.get('height', 'N/A')}")
                print(f"        CLASS: {img.get('class', 'N/A')}")
                
                # Ver si está dentro de un enlace
                parent_a = img.find_parent('a')
                if parent_a:
                    href = parent_a.get('href', '')
                    print(f"        LINK: {href[:60]}")
    
    # Buscar también imágenes en servimg que NO estén en headerbar
    print("\n🌐 Buscando imágenes de portada (servimg fuera de headerbar)...")
    headerbar = soup.find('div', {'class': 'headerbar'})
    
    all_servimg = soup.find_all('img', src=lambda x: x and 'servimg.com' in x)
    for img in all_servimg:
        # Ignorar si está en headerbar
        if headerbar and img.find_parent('div', {'class': 'headerbar'}):
            continue
        src = img.get('src', '')
        if any(x in src.lower() for x in ['portad', 'poster', 'cover', 'banner']):
            print(f"   POSIBLE PORTADA: {src[:80]}")

def main():
    session = requests.Session()
    
    # Login
    login_data = {
        'username': 'Admin',
        'password': '9XsBiygA2CpqgB9',
        'login': '1'
    }
    
    resp = session.post(LOGIN_URL, data=login_data)
    print("✅ Login exitoso" if 'Admin' in resp.text else "❌ Error en login")
    
    # Analizar algunos temas de ejemplo
    temas = [
        ("https://animezoneesp.foroactivo.com/t2801-activo-fullmetal-alchemist-2003-dual-audio-51-51-webdl-rip-1080p-mega-pixeldrain-ver-online", "Fullmetal Alchemist"),
        ("https://animezoneesp.foroactivo.com/t1860-activo-las-nuevas-aventuras-de-winnie-the-pooh-1988-castellano-53-55-tv-rip-640x480-180mb-150gb-mega-pixeldrain-ver-online#4509", "Winnie the Pooh"),
    ]
    
    for url, nombre in temas:
        analizar_tema(session, url, nombre)

if __name__ == "__main__":
    main()
