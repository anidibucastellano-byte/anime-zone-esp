#!/usr/bin/env python3
"""Script de prueba para depurar extracción de información del foro"""

import requests
from bs4 import BeautifulSoup
import re

# URL de prueba
url = "https://animezoneesp.foroactivo.com/t1895-activo-la-tierra-del-arcoiris-1984-castellano-13-13-dvd-rip-576x432-330mb-375mb-mega-pixeldrain-ver-online#4636"

def login_foro(session):
    """Hacer login en el foro"""
    login_url = "https://animezoneesp.foroactivo.com/login"
    
    login_data = {
        'username': 'Admin',
        'password': '9XsBiygA2CpqgB9',
        'autologin': 'on',
        'redirect': '',
        'login': 'Conectarse'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://animezoneesp.foroactivo.com/login'
    }
    
    response = session.post(login_url, data=login_data, headers=headers, timeout=15)
    print(f"Login status: {response.status_code}")
    
    # Verificar si el login fue exitoso
    if 'logout' in response.text.lower() or 'desconectarse' in response.text.lower():
        print("✅ Login exitoso")
        return True
    else:
        print("❌ Login posiblemente fallido")
        return False

def extraer_info():
    session = requests.Session()
    
    # Hacer login
    print("Haciendo login...")
    login_foro(session)
    
    # Obtener la página
    print(f"\nObteniendo: {url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = session.get(url, headers=headers, timeout=15)
    
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Guardar HTML para inspección
    with open('debug_pagina.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("\nHTML guardado en debug_pagina.html")
    
    # Extraer texto
    texto = soup.get_text(separator='\n', strip=True)
    
    # Guardar texto extraído
    with open('debug_texto.txt', 'w', encoding='utf-8') as f:
        f.write(texto[:3000])  # Primeros 3000 chars
    print("Texto guardado en debug_texto.txt")
    
    print("\n" + "="*60)
    print("ANÁLISIS DE EXTRACCIÓN")
    print("="*60)
    
    # 1. Buscar nombre en h1
    h1 = soup.find('h1')
    if h1:
        titulo = h1.get_text(strip=True)
        print(f"\n📝 H1 encontrado: {titulo}")
        # Limpiar
        titulo_limpio = re.sub(r'^(Re:)?\s*\[.*?\]\s*', '', titulo)
        print(f"📝 Título limpio: {titulo_limpio}")
    else:
        print("\n❌ No se encontró H1")
    
    # 2. Buscar imágenes
    print("\n🖼️  IMÁGENES ENCONTRADAS:")
    img_tags = soup.find_all('img')
    for i, img in enumerate(img_tags[:10]):
        src = img.get('src', '')
        if src and ('jpg' in src.lower() or 'jpeg' in src.lower() or 'png' in src.lower()):
            print(f"  {i+1}. {src[:80]}")
    
    # 3. Buscar en texto líneas con dos puntos
    print("\n📋 LÍNEAS CON ':' (primeras 50):")
    lineas = texto.split('\n')
    for i, linea in enumerate(lineas[:50]):
        if ':' in linea and len(linea) < 100:
            print(f"  {i+1}. {linea[:80]}")
    
    # 4. Buscar específicamente campos técnicos
    print("\n🔍 BUSCANDO CAMPOS TÉCNICOS:")
    
    campos_buscar = ['Idioma', 'Subtítulo', 'Calidad', 'Resolución', 'Formato', 'Peso', 'Año', 'Género', 'Sinopsis']
    for campo in campos_buscar:
        # Buscar en las primeras 100 líneas
        for linea in lineas[:100]:
            if campo.lower() in linea.lower() and ':' in linea:
                print(f"  ✅ {linea[:80]}")
                break
    
    print("\n" + "="*60)

if __name__ == "__main__":
    extraer_info()
