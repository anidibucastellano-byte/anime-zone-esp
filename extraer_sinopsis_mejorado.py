
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraer sinopsis de cada tema del foro - Versión mejorada
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

# Configuración
LOGIN_URL = "https://animezoneesp.foroactivo.com/login"
USERNAME = "Admin"
PASSWORD = "9XsBiygA2CpqgB9"

session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

def login():
    """Iniciar sesión en el foro"""
    try:
        session.get(LOGIN_URL, headers=headers, timeout=30)
        login_data = {'username': USERNAME, 'password': PASSWORD, 'login': 'Conectarse'}
        response = session.post(LOGIN_URL, data=login_data, headers=headers, timeout=30)
        return "Desconectarse" in response.text or "Admin" in response.text
    except Exception as e:
        print(f"Error en login: {e}")
        return False

def es_texto_de_sinopsis(texto, nombre_item):
    """
    Determina si un texto es realmente una sinopsis y no un título u otra cosa.
    Retorna True si parece ser una sinopsis válida.
    """
    texto_lower = texto.lower()
    
    # 1. Si contiene indicadores de título del post, NO es sinopsis
    if '[activo]' in texto_lower or '[completo]' in texto_lower:
        return False
    
    # 2. Si tiene muchos corchetes con info técnica [DVD], [WebDL], [Mega], etc.
    if texto.count('[') >= 3 and texto.count(']') >= 3:
        return False
    
    # 3. Si contiene patrones técnicos típicos de posts
    patrones_tecnicos = [
        r'\[\d+/\d+\]',  # [76/76], [2/2]
        r'\[\d{3,4}x\d{3,4}\]',  # [1920x1080]
        r'\d+\.\d+\s*(GB|MB)',  # 1.7 GB, 500 MB
        r'\[ver\s+online\]',
        r'mega|pixeldrain|mediafire',
    ]
    for patron in patrones_tecnicos:
        if re.search(patron, texto_lower):
            return False
    
    # 4. Si es muy similar al nombre del item, NO es sinopsis
    nombre_lower = nombre_item.lower()
    # Comparar sin caracteres especiales
    texto_simple = re.sub(r'[^\w]', '', texto_lower)
    nombre_simple = re.sub(r'[^\w]', '', nombre_lower)
    if len(nombre_simple) > 10 and nombre_simple in texto_simple:
        return False
    
    # 5. Debe tener características de narrativa
    # Palabras que indican que es una descripción de historia
    palabras_narrativa = [
        'es', 'cuenta', 'historia', 'narra', 'trata', 'sigue', 'vive', 'encuentra',
        'protagonista', 'personaje', 'mundo', 'tiempo', 'año', 'epoca', 'vida',
        'aventura', 'viaje', 'lucha', 'descubre', 'debe', 'decide', 'comienza'
    ]
    tiene_narrativa = any(palabra in texto_lower for palabra in palabras_narrativa)
    
    # 6. Longitud adecuada (sinopsis son generalmente entre 100-800 caracteres)
    longitud_ok = 80 < len(texto) < 1000
    
    # 7. Debe tener frases completas (verbos conjugados)
    tiene_verbos = bool(re.search(r'\b(es|son|fue|fueron|tiene|tienen|había|vive|viven|encuentra|encuentran|debe|deben|comienza|comienzan|decide|deciden|descubre|descubren|narra|trata)\b', texto_lower))
    
    return longitud_ok and (tiene_narrativa or tiene_verbos)


def extraer_ficha_tecnica(soup):
    """
    Extraer información de la ficha técnica del post.
    Busca campos como Género, Año, Idioma, Subtítulos, Formato, etc.
    """
    ficha = {}
    
    # Buscar en todo el post
    texto_completo = soup.get_text('\n', strip=True)
    
    # Patrones para extraer campos de la ficha técnica
    patrones_ficha = {
        'genero': [
            r'G[eé]nero[:\s]+([^\n]+)',
            r'Categor[ií]a[:\s]+([^\n]+)',
        ],
        'ano': [
            r'A[ñn]o[:\s]+(\d{4})',
            r'Estreno[:\s]+(\d{4})',
        ],
        'idioma': [
            r'Idioma[:\s]+([^\n]+)',
            r'Audio[:\s]+([^\n]+)',
            r'Idiomas[:\s]+([^\n]+)',
        ],
        'subtitulos': [
            r'Subt[ií]tulos[:\s]+([^\n]+)',
            r'Subs[:\s]+([^\n]+)',
        ],
        'formato': [
            r'Formato[:\s]+([^\n]+)',
            r'Codec[:\s]+([^\n]+)',
            r'Contenedor[:\s]+([^\n]+)',
        ],
        'peso': [
            r'Peso[/\s]+Cap[:\s]+([^\n]+)',
            r'Peso[:\s]+([^\n]+)',
            r'Tama[ñn]o[:\s]+([^\n]+)',
            r'Calidad[:\s]+([^\n]+)',
        ],
        'nfo': [
            r'NFO[:\s]+([^\n]+)',
            r'Mediainfo[:\s]+([^\n]+)',
        ],
        'trailer': [
            r'Trailer[:\s]+([^\n]+)',
        ],
        'temporadas': [
            r'Temporadas?[:\s]+([^\n]+)',
        ],
        'episodios': [
            r'Episodios?[:\s]+([^\n]+)',
            r'Cap[ií]tulos?[:\s]+([^\n]+)',
        ],
        'duracion': [
            r'Duraci[oó]n[:\s]+([^\n]+)',
        ],
        'director': [
            r'Director(?:es)?[:\s]+([^\n]+)',
        ],
        'estudio': [
            r'Estudio[:\s]+([^\n]+)',
            r'Animaci[oó]n[:\s]+([^\n]+)',
        ],
    }
    
    for campo, patrones in patrones_ficha.items():
        for patron in patrones:
            match = re.search(patron, texto_completo, re.IGNORECASE)
            if match:
                valor = match.group(1).strip()
                # Limpiar el valor
                valor = re.sub(r'\s+', ' ', valor)
                valor = re.sub(r'[,;]+$', '', valor)
                if len(valor) > 1 and len(valor) < 200:
                    ficha[campo] = valor
                    break
    
    return ficha if ficha else None


def extraer_sinopsis(html_content, nombre_item=''):
    """Extraer sinopsis del HTML del post"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Buscar el primer post
    post_body = soup.find('div', class_='postbody')
    if not post_body:
        return None, None
    
    # Extraer ficha técnica primero
    ficha_tecnica = extraer_ficha_tecnica(soup)
    
    # Obtener todo el texto para la sinopsis
    texto = post_body.get_text('\n', strip=True)
    
    # === MÉTODO 1: Buscar etiquetas explícitas de sinopsis ===
    patrones = [
        r'Sinopsis[:\s]+\s*(.+?)(?=\n\n|\n[A-Z]|Título|Género|Calidad|Enlaces|Descargar|$)',
        r'SINOPSIS[:\s]+\s*(.+?)(?=\n\n|\n[A-Z]|Título|Género|Calidad|Enlaces|Descargar|$)',
        r'Argumento[:\s]+\s*(.+?)(?=\n\n|\n[A-Z]|Título|Género|Calidad|Enlaces|Descargar|$)',
        r'Historia[:\s]+\s*(.+?)(?=\n\n|\n[A-Z]|Título|Género|Calidad|Enlaces|Descargar|$)',
        r'Resumen[:\s]+\s*(.+?)(?=\n\n|\n[A-Z]|Título|Género|Calidad|Enlaces|Descargar|$)',
        r'Descripción[:\s]+\s*(.+?)(?=\n\n|\n[A-Z]|Título|Género|Calidad|Enlaces|Descargar|$)',
    ]
    
    for patron in patrones:
        match = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
        if match:
            sinopsis = match.group(1).strip()
            sinopsis = re.sub(r'\n+', ' ', sinopsis)
            sinopsis = re.sub(r'\s+', ' ', sinopsis)
            if len(sinopsis) > 40:
                return sinopsis[:2000], ficha_tecnica
    
    # === MÉTODO 2: Buscar en elementos específicos del HTML ===
    # A veces la sinopsis está en divs o spans específicos
    for element in post_body.find_all(['div', 'span', 'p', 'font']):
        texto_elem = element.get_text(strip=True)
        if 'sinopsis' in texto_elem.lower() or 'argumento' in texto_elem.lower():
            # El siguiente hermano suele ser la sinopsis
            siguiente = element.find_next_sibling()
            if siguiente:
                texto_sig = siguiente.get_text(strip=True)
                if es_texto_de_sinopsis(texto_sig, nombre_item):
                    return texto_sig[:2000], ficha_tecnica
    
    # === MÉTODO 3: Buscar párrafos narrativos con heurística ===
    parrafos = [p.strip() for p in texto.split('\n') if len(p.strip()) > 60]
    
    for parrafo in parrafos[:5]:  # Revisar primeros 5 párrafos
        if es_texto_de_sinopsis(parrafo, nombre_item):
            # Limpiar
            parrafo = re.sub(r'\n+', ' ', parrafo)
            parrafo = re.sub(r'\s+', ' ', parrafo)
            return parrafo[:2000], ficha_tecnica
    
    # === MÉTODO 4: Buscar texto entre imágenes o después de ciertos patrones ===
    # A veces la sinopsis está entre el título y los datos técnicos
    for i, parrafo in enumerate(parrafos):
        # Ignorar párrafos que parecen títulos
        if '[activo]' in parrafo.lower() or parrafo.count('[') >= 3:
            continue
        # El siguiente párrafo podría ser la sinopsis
        if i + 1 < len(parrafos):
            siguiente = parrafos[i + 1]
            if es_texto_de_sinopsis(siguiente, nombre_item):
                siguiente = re.sub(r'\n+', ' ', siguiente)
                siguiente = re.sub(r'\s+', ' ', siguiente)
                return siguiente[:2000], ficha_tecnica
    
    return None, ficha_tecnica


def main():
    print("=" * 60)
    print("🎬 EXTRACTOR DE SINOPSIS MEJORADO")
    print("=" * 60)
    
    if not login():
        print("❌ Error en login")
        return
    
    print("✅ Login exitoso\n")
    
    # Cargar TOP.json
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categorias = ['anime', 'series', 'dibujos', 'peliculas']
    total = 0
    exitosos = 0
    
    for categoria in categorias:
        if categoria not in data:
            continue
            
        items = data[categoria]
        print(f"📁 {categoria.upper()}: {len(items)} items")
        
        for i, item in enumerate(items):
            total += 1
            
            # Saltar si ya tiene sinopsis
            if item.get('sinopsis') and len(item.get('sinopsis', '')) > 20:
                continue
            
            url = item.get('url', '')
            if not url:
                continue
            
            try:
                response = session.get(url, headers=headers, timeout=30)
                nombre_item = item.get('nombre_limpio', item.get('name', ''))
                sinopsis, ficha_tecnica = extraer_sinopsis(response.text, nombre_item)
                
                actualizado = False
                
                if sinopsis:
                    item['sinopsis'] = sinopsis
                    actualizado = True
                    nombre = nombre_item[:40]
                    print(f"  ✅ [{i+1}/{len(items)}] {nombre} - Sinopsis extraída")
                    print(f"     📝 {sinopsis[:60]}...")
                
                if ficha_tecnica:
                    item['ficha_tecnica'] = ficha_tecnica
                    actualizado = True
                    print(f"     📋 Ficha técnica: {', '.join(ficha_tecnica.keys())}")
                
                if actualizado:
                    exitosos += 1
                else:
                    nombre = nombre_item[:40]
                    print(f"  ⚠️  [{i+1}/{len(items)}] {nombre} - Sin información nueva")
                
                time.sleep(0.3)  # Esperar entre requests
                
            except Exception as e:
                print(f"  ❌ [{i+1}/{len(items)}] Error: {e}")
    
    # Guardar JSON actualizado
    print(f"\n💾 Guardando...")
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 COMPLETADO:")
    print(f"   Total: {total}")
    print(f"   Sinopsis extraídas: {exitosos}")

if __name__ == "__main__":
    main()
