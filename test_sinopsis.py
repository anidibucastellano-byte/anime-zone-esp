#!/usr/bin/env python3
"""Test específico para depurar extracción de sinopsis"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://animezoneesp.foroactivo.com/t1895-activo-la-tierra-del-arcoiris-1984-castellano-13-13-dvd-rip-576x432-330mb-375mb-mega-pixeldrain-ver-online#4636"

def login_foro(session):
    login_url = "https://animezoneesp.foroactivo.com/login"
    login_data = {
        'username': 'Admin',
        'password': '9XsBiygA2CpqgB9',
        'autologin': 'on',
        'login': 'Conectarse'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://animezoneesp.foroactivo.com/login'
    }
    session.post(login_url, data=login_data, headers=headers, timeout=15)

session = requests.Session()
login_foro(session)

response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
soup = BeautifulSoup(response.text, 'html.parser')
texto = soup.get_text(separator='\n', strip=True)

print("="*60)
print("BUSCANDO SINOPSIS EN EL HTML")
print("="*60)

# Buscar elementos que contengan "Sinopsis"
for elem in soup.find_all(['div', 'p', 'span', 'td', 'b', 'strong']):
    elem_texto = elem.get_text(strip=True)
    if 'sinopsis' in elem_texto.lower():
        print(f"\n--- Elemento encontrado ({elem.name}) ---")
        print(f"Texto: {elem_texto[:200]}")
        print(f"HTML: {str(elem)[:300]}")
        print("-"*40)

print("\n" + "="*60)
print("BUSCANDO EN TEXTO PLANO CON REGEX")
print("="*60)

# Buscar con regex en el texto
sinopsis_match = re.search(r'Sinopsis[:\s]+([^\n].{30,500}?)(?=\n\n|\n[A-Z]|$|Ficha)', texto, re.DOTALL | re.IGNORECASE)
if sinopsis_match:
    print(f"\n✅ Sinopsis encontrada con regex:")
    print(f"{sinopsis_match.group(1).strip()[:200]}")
else:
    print("\n❌ No se encontró sinopsis con regex")
    # Mostrar las líneas que contienen "Sinopsis"
    lineas = texto.split('\n')
    for i, linea in enumerate(lineas):
        if 'sinopsis' in linea.lower():
            print(f"\nLínea {i}: {linea}")
            # Mostrar contexto
            for j in range(max(0, i-2), min(len(lineas), i+5)):
                print(f"  [{j}] {lineas[j][:100]}")
