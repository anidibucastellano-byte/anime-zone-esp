import requests
from bs4 import BeautifulSoup
import json
import re

session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Login
print("🔑 Iniciando sesión...")
session.get('https://animezoneesp.foroactivo.com/login', headers=headers)
session.post('https://animezoneesp.foroactivo.com/login', 
    data={'username': 'Admin', 'password': '9XsBiygA2CpqgB9', 'login': 'Conectarse'},
    headers=headers)
print("✅ Login exitoso\n")

# URLs conocidas de Digimon
digimon_urls = [
    'https://animezoneesp.foroactivo.com/t3-digimon-adventure',
    'https://animezoneesp.foroactivo.com/t2-digimon-adventure-02',
    'https://animezoneesp.foroactivo.com/t188-activodigimon-tamers-2001-dual-audio-51-51-dvd-rip-1280x720-730-mb-mega-ver-online',
    'https://animezoneesp.foroactivo.com/t191-activodigimon-xros-wars-2010-castellano-30-30-webdl-rip-1280x720-305-525-mb-mega-ver-online',
]

print("🔍 Buscando temas de Digimon...\n")
encontrados = []

for url in digimon_urls:
    try:
        r = session.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            titulo = soup.find('h1', class_='page-title')
            if titulo:
                nombre = titulo.get_text(strip=True)
                print(f"✅ {nombre}")
                print(f"   URL: {url}")
                
                # Extraer imagen
                img = soup.find('img', class_='postimage') or soup.find('img', {'alt': ''})
                imagen_url = img['src'] if img else None
                
                # Extraer sinopsis
                post_body = soup.find('div', class_='postbody')
                sinopsis = None
                if post_body:
                    texto = post_body.get_text('\n', strip=True)
                    parrafos = [p.strip() for p in texto.split('\n') if 100 < len(p.strip()) < 1500]
                    for p in parrafos[:3]:
                        if any(word in p.lower() for word in ['historia', 'trama', 'digimon', 'mundo', 'protagonista', 'aventura']):
                            sinopsis = p[:2000]
                            break
                
                print(f"   Imagen: {imagen_url[:50] if imagen_url else 'NO'}...")
                print(f"   Sinopsis: {sinopsis[:80] if sinopsis else 'NO'}...")
                print()
                
                encontrados.append({
                    'nombre': nombre,
                    'url': url,
                    'imagen_url': imagen_url,
                    'sinopsis': sinopsis
                })
        else:
            print(f"❌ {url} - Status {r.status_code}")
    except Exception as e:
        print(f"❌ {url} - Error: {e}")

print(f"\n🎉 Total encontrados: {len(encontrados)}")
