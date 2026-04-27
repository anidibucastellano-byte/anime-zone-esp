#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import re

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("Login...")
session.get('https://animezoneesp.foroactivo.com/login', headers=headers)
session.post(
    'https://animezoneesp.foroactivo.com/login',
    data={'username': 'Admin', 'password': '9XsBiygA2CpqgB9', 'login': 'Conectarse'},
    headers=headers
)

# Cargar TOP.json
with open('TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Buscar y actualizar Digimon Xros Wars
for cat in ['anime', 'series', 'dibujos', 'peliculas']:
    for item in data.get(cat, []):
        if 'xros' in item.get('name', '').lower() or 'xros' in item.get('nombre_limpio', '').lower():
            print(f"\nActualizando: {item.get('nombre_limpio', item.get('name'))}")
            
            try:
                r = session.get(item['url'], headers=headers, timeout=30)
                soup = BeautifulSoup(r.text, 'html.parser')
                post = soup.find('div', class_='postbody')
                
                if post:
                    texto = post.get_text('\n', strip=True)
                    
                    # Buscar párrafos narrativos largos
                    parrafos = [p.strip() for p in texto.split('\n') if 100 < len(p.strip()) < 1500]
                    
                    for p in parrafos[:5]:
                        # Verificar que parezca una sinopsis
                        if any(word in p.lower() for word in ['taiki', 'shoutmon', 'digimundo', 'mundo digital', 'universo paralelo']):
                            # Limpiar
                            p = re.sub(r'\s+', ' ', p).strip()
                            if len(p) > 200:
                                item['sinopsis'] = p[:2000]
                                print(f"✅ Sinopsis actualizada ({len(p)} chars)")
                                break
                    else:
                        print("⚠️ No se encontró sinopsis adecuada")
                        
            except Exception as e:
                print(f"❌ Error: {e}")

# Guardar
with open('TOP.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n✅ Archivo actualizado")
