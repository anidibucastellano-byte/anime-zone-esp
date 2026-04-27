#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import re

session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Login
print("🔑 Login...")
session.get('https://animezoneesp.foroactivo.com/login', headers=headers)
session.post('https://animezoneesp.foroactivo.com/login', 
    data={'username': 'Admin', 'password': '9XsBiygA2CpqgB9', 'login': 'Conectarse'},
    headers=headers)
print("✅ Login exitoso\n")

# Cargar lista de incompletas
with open('sinopsis_incompletas.json', 'r', encoding='utf-8') as f:
    incompletas = json.load(f)

# Cargar TOP.json
with open('TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"🔧 Reparando {len(incompletas)} sinopsis...\n")

reparadas = 0
for item_info in incompletas:
    url = item_info['url']
    nombre = item_info['nombre']
    
    try:
        print(f"📺 {nombre[:60]}...")
        r = session.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')
        post = soup.find('div', class_='postbody')
        
        if post:
            texto = post.get_text('\n', strip=True)
            
            # Buscar párrafos narrativos
            parrafos = [p.strip() for p in texto.split('\n') if 100 < len(p.strip()) < 1500]
            
            for p in parrafos[:5]:
                # Verificar que sea una sinopsis real (no título ni metadata)
                if any(word in p.lower() for word in ['historia', 'trama', 'protagonista', 'aventura', 'mundo', 'vida', 'cuenta']):
                    # Limpiar y truncar
                    p = re.sub(r'\s+', ' ', p).strip()
                    if len(p) > 150:
                        # Buscar en el JSON y actualizar
                        for cat in ['anime', 'series', 'dibujos', 'peliculas']:
                            for item in data.get(cat, []):
                                if item.get('url') == url:
                                    item['sinopsis'] = p[:2000]
                                    reparadas += 1
                                    print(f"   ✅ Reparada ({len(p)} chars)")
                                    break
                        break
            else:
                print(f"   ⚠️ No se encontró sinopsis válida")
        else:
            print(f"   ❌ No se encontró post")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print(f"\n✅ {reparadas} sinopsis reparadas")

# Guardar
with open('TOP.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ TOP.json actualizado")
