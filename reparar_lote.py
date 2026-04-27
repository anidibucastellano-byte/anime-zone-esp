#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sys

# Cargar lista de incompletas
with open('lista_incompletas.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

nombres_incompletos = []
for line in lines:
    if line.strip() and line[0].isdigit():
        match = re.match(r'\d+\.\s+(.+)', line.strip())
        if match:
            nombres_incompletos.append(match.group(1))

# Cargar progreso previo
try:
    with open('progreso_reparacion.json', 'r', encoding='utf-8') as f:
        progreso = json.load(f)
    ya_procesados = set(progreso.get('procesados', []))
except:
    progreso = {'procesados': [], 'reparadas': 0}
    ya_procesados = set()

print(f"Total a reparar: {len(nombres_incompletos)}")
print(f"Ya procesados: {len(ya_procesados)}")
print(f"Pendientes: {len(nombres_incompletos) - len(ya_procesados)}\n")

# Cargar TOP.json
with open('TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Login
print("🔑 Login...")
session.get('https://animezoneesp.foroactivo.com/login', headers=headers, timeout=30)
session.post('https://animezoneesp.foroactivo.com/login',
    data={'username': 'Admin', 'password': '9XsBiygA2CpqgB9', 'login': 'Conectarse'},
    headers=headers, timeout=30)
print("✅ Login\n")

reparadas_lote = 0
procesados_lote = 0

for idx, nombre_completo in enumerate(nombres_incompletos, 1):
    if nombre_completo in ya_procesados:
        continue
    
    if procesados_lote >= 50:  # Procesar solo 50 por ejecución
        print(f"\n⏹️ Límite de 50 alcanzado. Guardando progreso...")
        break
    
    print(f"[{idx}/208] {nombre_completo[:45]}...", end=' ')
    sys.stdout.flush()
    
    # Buscar item
    item_encontrado = None
    for cat in ['anime', 'series', 'dibujos', 'peliculas']:
        for item in data.get(cat, []):
            if item.get('nombre_limpio') == nombre_completo or item.get('name') == nombre_completo:
                item_encontrado = item
                break
        if item_encontrado:
            break
    
    if not item_encontrado:
        print("❌ No encontrado")
        ya_procesados.add(nombre_completo)
        continue
    
    url = item_encontrado.get('url', '')
    if not url:
        print("❌ Sin URL")
        ya_procesados.add(nombre_completo)
        continue
    
    try:
        r = session.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')
        post = soup.find('div', class_='postbody')
        
        if not post:
            print("❌ No post")
            ya_procesados.add(nombre_completo)
            continue
        
        texto = post.get_text('\n', strip=True)
        parrafos = [p.strip() for p in texto.split('\n') if 150 < len(p.strip()) < 2000]
        
        mejor_sinopsis = None
        for p in parrafos[:5]:
            palabras_clave = ['historia', 'trama', 'protagonista', 'aventura', 'mundo', 'vida',
                            'cuenta', 'narra', 'sigue', 'cuando', 'donde', 'junto', 'deberá']
            if any(word in p.lower() for word in palabras_clave):
                p = re.sub(r'\s+', ' ', p).strip()
                if len(p) > 200:
                    mejor_sinopsis = p[:2000]
                    break
        
        if mejor_sinopsis:
            item_encontrado['sinopsis'] = mejor_sinopsis
            reparadas_lote += 1
            print(f"✅ ({len(mejor_sinopsis)} chars)")
        else:
            print("⚠️ No válida")
            
    except Exception as e:
        print(f"❌ Error: {str(e)[:30]}")
    
    ya_procesados.add(nombre_completo)
    procesados_lote += 1
    time.sleep(0.5)

# Guardar progreso
progreso['procesados'] = list(ya_procesados)
progreso['reparadas'] = progreso.get('reparadas', 0) + reparadas_lote
with open('progreso_reparacion.json', 'w', encoding='utf-8') as f:
    json.dump(progreso, f)

# Guardar TOP.json
with open('TOP.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n{'='*50}")
print(f"✅ Reparadas este lote: {reparadas_lote}")
print(f"📊 Total reparadas: {progreso['reparadas']}")
print(f"⏳ Pendientes: {len(nombres_incompletos) - len(ya_procesados)}")
print(f"{'='*50}")
