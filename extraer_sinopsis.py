#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraer sinopsis e información detallada de cada tema del foro
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# Configuración
LOGIN_URL = "https://animezoneesp.foroactivo.com/login"
USERNAME = "Admin"
PASSWORD = "9XsBiygA2CpqgB9"

# Sesión para mantener cookies
session = requests.Session()

# Headers para simular navegador
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9',
}

def login():
    """Iniciar sesión en el foro"""
    print("🔐 Iniciando sesión...")
    try:
        # Obtener página de login para cookies
        session.get(LOGIN_URL, headers=headers, timeout=30)
        
        # Datos de login
        login_data = {
            'username': USERNAME,
            'password': PASSWORD,
            'login': 'Conectarse'
        }
        
        response = session.post(LOGIN_URL, data=login_data, headers=headers, timeout=30)
        
        if "Desconectarse" in response.text or "Admin" in response.text:
            print("✅ Login exitoso")
            return True
        else:
            print("❌ Error en login")
            return False
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False

def extraer_info_tema(url):
    """Extraer sinopsis e información de un tema"""
    try:
        response = session.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar el primer post
        first_post = soup.find('div', class_='postbody')
        if not first_post:
            return None
        
        # Extraer texto completo del post
        post_text = first_post.get_text('\n', strip=True)
        
        # Buscar sinopsis - suele estar después de "Sinopsis:" o similar
        sinopsis = ""
        info_extra = ""
        
        # Patrones comunes para sinopsis
        sinopsis_patterns = ['Sinopsis:', 'SINOPSIS:', 'sinopsis:', 'Argumento:', 'ARGUMENTO:', 'Historia:']
        for pattern in sinopsis_patterns:
            if pattern in post_text:
                parts = post_text.split(pattern, 1)
                if len(parts) > 1:
                    # Tomar texto hasta el siguiente salto de línea o punto
                    sinopsis_text = parts[1].strip()
                    # Cortar en el primer doble salto o línea vacía
                    lines = sinopsis_text.split('\n')
                    sinopsis_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('Género:') and not line.startswith('Título:'):
                            sinopsis_lines.append(line)
                        elif len(sinopsis_lines) > 0:
                            break
                    sinopsis = ' '.join(sinopsis_lines[:3])  # Máximo 3 líneas
                    break
        
        # Extraer información entre Género: y Trailer:
        if 'Género:' in post_text:
            parts = post_text.split('Género:', 1)
            if len(parts) > 1:
                info_text = 'Género:' + parts[1]
                # Cortar en Trailer: o final
                if 'Trailer:' in info_text:
                    info_text = info_text.split('Trailer:', 1)[0] + 'Trailer:'
                elif 'Trailer' in info_text:
                    info_text = info_text.split('Trailer', 1)[0] + 'Trailer'
                
                # Limpiar el texto
                lines = info_text.split('\n')
                info_lines = []
                for line in lines:
                    line = line.strip()
                    if line:
                        info_lines.append(line)
                
                info_extra = '\n'.join(info_lines)
        
        return {
            'sinopsis': sinopsis[:500] if sinopsis else "",  # Limitar a 500 chars
            'info_extra': info_extra[:1000] if info_extra else ""
        }
        
    except Exception as e:
        print(f"  ❌ Error extrayendo {url}: {e}")
        return None

def main():
    print("=" * 60)
    print("🎬 EXTRACTOR DE SINOPSIS")
    print("=" * 60)
    
    # Login
    if not login():
        print("No se pudo iniciar sesión")
        return
    
    # Cargar TOP.json
    print("\n📂 Cargando TOP.json...")
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Procesar cada categoría
    categorias = ['anime', 'series', 'dibujos', 'peliculas']
    total_items = 0
    items_actualizados = 0
    
    for categoria in categorias:
        if categoria not in data:
            continue
            
        items = data[categoria]
        print(f"\n📁 Procesando {categoria}: {len(items)} items")
        
        for i, item in enumerate(items):
            total_items += 1
            
            # Saltar si ya tiene sinopsis
            if item.get('sinopsis') and len(item.get('sinopsis', '')) > 10:
                print(f"  ⏭️  {i+1}/{len(items)}: Ya tiene sinopsis - {item.get('nombre_limpio', item.get('name', '???'))[:40]}")
                continue
            
            url = item.get('url', '')
            if not url:
                continue
            
            print(f"  🔍 {i+1}/{len(items)}: Extrayendo {item.get('nombre_limpio', item.get('name', '???'))[:40]}...")
            
            info = extraer_info_tema(url)
            if info:
                item['sinopsis'] = info['sinopsis']
                item['info_extra'] = info['info_extra']
                items_actualizados += 1
                print(f"     ✅ Sinopsis: {len(info['sinopsis'])} chars, Info: {len(info['info_extra'])} chars")
            else:
                print(f"     ⚠️  No se pudo extraer información")
            
            # Esperar entre requests
            time.sleep(0.5)
    
    # Guardar JSON actualizado
    print(f"\n💾 Guardando TOP.json actualizado...")
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Proceso completado!")
    print(f"   Total items: {total_items}")
    print(f"   Items actualizados: {items_actualizados}")

if __name__ == "__main__":
    main()
