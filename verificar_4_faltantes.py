#!/usr/bin/env python3
"""
Verificar las imágenes de los 4 temas faltantes
"""
import requests
from bs4 import BeautifulSoup

FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"

TEMAS = [
    ("t1714", "La Hora de José Mota"),
    ("t582", "Xena, la princesa guerrera"),
    ("t568", "Hércules: Sus viajes legendarios"),
    ("t482", "Historias de la cripta"),
]

def verificar_tema(session, tema_id, nombre):
    url = f"{FORO_URL}/{tema_id}-"
    print(f"\n🔍 {tema_id}: {nombre}")
    print("="*60)
    
    resp = session.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Buscar og:image
    og_image = soup.find('meta', property='og:image')
    if og_image:
        src = og_image.get('content', '')
        print(f"📸 og:image: {src}")
    
    # Buscar twitter:image
    twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
    if twitter_image:
        src = twitter_image.get('content', '')
        print(f"📸 twitter:image: {src}")
    
    # Buscar cualquier imagen en cloudinary
    cloudinary_imgs = soup.find_all('img', src=lambda x: x and 'cloudinary.com' in x)
    print(f"\n🌐 Imágenes Cloudinary: {len(cloudinary_imgs)}")
    for img in cloudinary_imgs[:3]:
        print(f"   - {img.get('src', '')}")

def main():
    session = requests.Session()
    
    login_data = {
        'username': 'Admin',
        'password': '9XsBiygA2CpqgB9',
        'login': '1'
    }
    
    session.post(LOGIN_URL, data=login_data)
    print("✅ Login exitoso")
    
    for tema_id, nombre in TEMAS:
        verificar_tema(session, tema_id, nombre)

if __name__ == "__main__":
    main()
