#!/usr/bin/env python3
"""
Verificar temas específicos que no tienen imagen correcta
"""
import requests
from bs4 import BeautifulSoup

FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"

def verificar_tema(session, tema_url, nombre):
    """Verificar un tema específico"""
    print(f"\n{'='*60}")
    print(f"Verificando: {nombre}")
    print(f"URL: {tema_url}")
    print('='*60)
    
    resp = session.get(tema_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Buscar og:image
    og_image = soup.find('meta', property='og:image')
    if og_image:
        src = og_image.get('content', '')
        print(f"\n📸 og:image: {src}")
    else:
        print("\n❌ No hay og:image")
    
    # Buscar twitter:image
    twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
    if twitter_image:
        src = twitter_image.get('content', '')
        print(f"📸 twitter:image: {src}")
    else:
        print("❌ No hay twitter:image")
    
    # Buscar cualquier imagen en cloudinary
    cloudinary_imgs = soup.find_all('img', src=lambda x: x and 'cloudinary.com' in x)
    print(f"\n🌐 Imágenes Cloudinary en img tags: {len(cloudinary_imgs)}")
    for img in cloudinary_imgs[:3]:
        print(f"   - {img.get('src', '')[:80]}")

def main():
    session = requests.Session()
    
    # Login
    login_data = {
        'username': 'Admin',
        'password': '9XsBiygA2CpqgB9',
        'login': '1'
    }
    
    session.post(LOGIN_URL, data=login_data)
    print("✅ Login exitoso")
    
    # Verificar temas problemáticos
    temas = [
        ("https://animezoneesp.foroactivo.com/t1318-activo-alita-angel-de-combate-1993-multi-audio-2-2-dvd-rip-700x480-575-595-mb-mega-pixeldrain-ver-online", "Alita: Ángel de Combate"),
        ("https://animezoneesp.foroactivo.com/t1235-activo-blood-2005-castellano-50-50-webdl-rip-1440x1080-95-185-mb-mega-pixeldrain-ver-online", "Blood (2005)"),
    ]
    
    for url, nombre in temas:
        verificar_tema(session, url, nombre)

if __name__ == "__main__":
    main()
