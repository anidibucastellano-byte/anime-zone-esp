#!/usr/bin/env python3
"""
Análisis profundo del HTML de un tema
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
    
    session.post(LOGIN_URL, data=login_data)
    
    # Obtener HTML de un tema
    tema_url = 'https://animezoneesp.foroactivo.com/t1860-activo-las-nuevas-aventuras-de-winnie-the-pooh-1988-castellano-53-55-tv-rip-640x480-180mb-150gb-mega-pixeldrain-ver-online#4509'
    resp = session.get(tema_url)
    
    # Guardar HTML para análisis
    with open('debug_tema.html', 'w', encoding='utf-8') as f:
        f.write(resp.text)
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    print("🔍 Buscando TODAS las imágenes con 'servimg'...")
    all_imgs = soup.find_all('img')
    
    servimg_imgs = []
    for img in all_imgs:
        src = img.get('src', '')
        if 'servimg.com' in src and not any(x in src.lower() for x in ['icon', 'avatar', 'smiley', 'mini', 'logo']):
            servimg_imgs.append(img)
    
    print(f"\n📸 Imágenes servimg encontradas: {len(servimg_imgs)}")
    
    for i, img in enumerate(servimg_imgs[:10]):
        src = img.get('src', '')
        print(f"\n[{i+1}] {src}")
        print(f"    Clases: {img.get('class', 'N/A')}")
        print(f"    Alt: {img.get('alt', 'N/A')}")
        
        # Contexto
        parent = img.parent
        for level in range(1, 4):
            if parent:
                print(f"    Parent {level}: {parent.name} class={parent.get('class', 'N/A')}")
                parent = parent.parent
    
    print(f"\n📄 HTML guardado en debug_tema.html")

if __name__ == "__main__":
    main()
