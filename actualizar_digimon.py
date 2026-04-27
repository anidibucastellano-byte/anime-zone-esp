import requests
from bs4 import BeautifulSoup
import json
import re

session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Login
print("Iniciando sesión...")
session.get('https://animezoneesp.foroactivo.com/login', headers=headers)
session.post('https://animezoneesp.foroactivo.com/login', 
    data={'username': 'Admin', 'password': '9XsBiygA2CpqgB9', 'login': 'Conectarse'},
    headers=headers)
print("✅ Login exitoso")

# Cargar TOP.json
with open('TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Buscar Digimon
actualizados = 0
for cat in ['anime', 'series', 'dibujos', 'peliculas']:
    for item in data.get(cat, []):
        nombre = item.get('nombre_limpio', item.get('name', '')).lower()
        if 'digimon' in nombre:
            print(f"\n📺 {item.get('nombre_limpio', item.get('name', ''))}")
            
            try:
                url = item['url']
                response = session.get(url, headers=headers, timeout=30)
                soup = BeautifulSoup(response.text, 'html.parser')
                post_body = soup.find('div', class_='postbody')
                
                if post_body:
                    texto = post_body.get_text('\n', strip=True)
                    
                    # Buscar párrafo narrativo
                    parrafos = [p.strip() for p in texto.split('\n') if 100 < len(p.strip())]
                    sinopsis_completa = None
                    
                    for p in parrafos[:3]:
                        if any(word in p.lower() for word in ['historia', 'trama', 'digimon', 'mundo', 'protagonista', 'aventura']):
                            sinopsis_completa = p[:2000]
                            break
                    
                    if sinopsis_completa and len(sinopsis_completa) > len(item.get('sinopsis', '')):
                        item['sinopsis'] = sinopsis_completa
                        actualizados += 1
                        print(f"✅ Sinopsis actualizada ({len(sinopsis_completa)} chars)")
                    else:
                        print(f"⚠️ No se encontró mejor sinopsis")
                        
            except Exception as e:
                print(f"❌ Error: {e}")

# Guardar
with open('TOP.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n🎉 {actualizados} Digimon actualizados")
