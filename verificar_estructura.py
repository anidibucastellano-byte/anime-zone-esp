#!/usr/bin/env python3
"""
Verificar estructura HTML del foro
"""
import requests
from bs4 import BeautifulSoup

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
    
    # Tema de ejemplo
    tema_url = 'https://animezoneesp.foroactivo.com/t1860-activo-las-nuevas-aventuras-de-winnie-the-pooh-1988-castellano-53-55-tv-rip-640x480-180mb-150gb-mega-pixeldrain-ver-online#4509'
    
    resp = session.get(tema_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    print("🔍 Buscando estructura del foro...\n")
    
    # Buscar posts
    posts = soup.find_all(['div', 'tr'], class_=['post', 'post--', 'post_row', 'postbody'])
    print(f"Posts encontrados con class 'post/postbody': {len(posts)}")
    
    # Buscar por ID que contenga post
    all_divs = soup.find_all('div', id=True)
    post_divs = [d for d in all_divs if 'post' in d.get('id', '').lower()]
    print(f"Divs con ID 'post': {len(post_divs)}")
    
    # Buscar primera imagen grande (servimg)
    all_imgs = soup.find_all('img')
    servimg_imgs = [img for img in all_imgs if 'servimg' in img.get('src', '')]
    print(f"\nImágenes servimg: {len(servimg_imgs)}")
    
    for img in servimg_imgs[:3]:
        src = img.get('src', '')
        parent = img.parent
        print(f"\n  SRC: {src}")
        print(f"  Parent: {parent.name}")
        if parent.name == 'a':
            print(f"  Link: {parent.get('href', '')}")
        
        # Buscar hacia arriba
        for level in range(1, 6):
            ancestor = img
            for _ in range(level):
                if ancestor.parent:
                    ancestor = ancestor.parent
            if ancestor:
                print(f"  Ancestor {level}: {ancestor.name} (class: {ancestor.get('class', 'N/A')})")
    
    # Guardar HTML para análisis
    with open('debug_tema.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify()[:5000])
    print("\n📄 HTML guardado en debug_tema.html (primeros 5000 chars)")

if __name__ == "__main__":
    main()
