#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import re
import time

session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Login
print("🔑 Login en el foro...")
try:
    session.get('https://animezoneesp.foroactivo.com/login', headers=headers, timeout=30)
    r = session.post('https://animezoneesp.foroactivo.com/login', 
        data={'username': 'Admin', 'password': '9XsBiygA2CpqgB9', 'login': 'Conectarse'},
        headers=headers, timeout=30)
    print("✅ Login exitoso")
except Exception as e:
    print(f"❌ Error login: {e}")

# Cargar TOP.json
with open('TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Cargar lista de incompletas
with open('lista_incompletas.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extraer nombres de la lista
nombres_incompletos = []
for line in lines:
    if line.strip() and line[0].isdigit():
        # Extraer nombre entre el número y los últimos chars
        match = re.match(r'\d+\.\s+(.+)', line.strip())
        if match:
            nombre = match.group(1)
            nombres_incompletos.append(nombre)

print(f"\n🔧 Encontrados {len(nombres_incompletos)} items para reparar")
print("⚠️ Esto tomará varios minutos...\n")

reparadas = 0
fallidas = 0

for idx, nombre_completo in enumerate(nombres_incompletos, 1):
    print(f"[{idx}/208] {nombre_completo[:50]}...")
    
    # Buscar el item en el JSON
    item_encontrado = None
    cat_encontrada = None
    
    for cat in ['anime', 'series', 'dibujos', 'peliculas']:
        for item in data.get(cat, []):
            if item.get('nombre_limpio') == nombre_completo or item.get('name') == nombre_completo:
                item_encontrado = item
                cat_encontrada = cat
                break
        if item_encontrado:
            break
    
    if not item_encontrado:
        print(f"   ⚠️ No encontrado en JSON")
        fallidas += 1
        continue
    
    url = item_encontrado.get('url', '')
    if not url:
        print(f"   ⚠️ Sin URL")
        fallidas += 1
        continue
    
    try:
        # Obtener página del foro
        r = session.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Buscar el primer post
        post = soup.find('div', class_='postbody')
        if not post:
            print(f"   ❌ No se encontró post")
            fallidas += 1
            continue
        
        # Extraer texto
        texto = post.get_text('\n', strip=True)
        
        # Buscar párrafos narrativos largos
        parrafos = [p.strip() for p in texto.split('\n') if 150 < len(p.strip()) < 2000]
        
        mejor_sinopsis = None
        for p in parrafos[:5]:
            # Verificar que sea una sinopsis real
            palabras_clave = ['historia', 'trama', 'protagonista', 'aventura', 'mundo', 'vida', 
                            'cuenta', 'narra', 'sigue', 'cuando', 'donde', 'junto', 'deberá']
            if any(word in p.lower() for word in palabras_clave):
                # Limpiar
                p = re.sub(r'\s+', ' ', p).strip()
                if len(p) > 200:
                    mejor_sinopsis = p[:2000]  # Máximo 2000 chars
                    break
        
        if mejor_sinopsis:
            item_encontrado['sinopsis'] = mejor_sinopsis
            reparadas += 1
            print(f"   ✅ Reparada ({len(mejor_sinopsis)} chars)")
        else:
            print(f"   ⚠️ No se encontró sinopsis válida")
            fallidas += 1
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:50]}")
        fallidas += 1
    
    # Pequeña pausa para no sobrecargar el servidor
    time.sleep(0.5)

print(f"\n{'='*60}")
print(f"✅ Reparadas: {reparadas}")
print(f"❌ Fallidas: {fallidas}")
print(f"{'='*60}")

# Guardar
with open('TOP.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ TOP.json actualizado")
