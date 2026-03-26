# Sistema de Actualización Automática con TMDB para géneros
import json
import os
import re
import time
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from unicodedata import normalize
from datetime import datetime
import schedule

# Configuración de TMDB
TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '6e711704d7ada0c49876e5941de50431')  # Usar variable de entorno o fallback a la key local
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_LANGUAGE = "es-ES"

def limpiar_texto(texto):
    """Normalizar texto para comparación"""
    return normalize('NFKD', texto.lower()).replace('é', 'e')

def get_sort_name_perfect(item):
    """Función perfecta para ordenamiento"""
    name = item.get('name', '')
    clean_name = name
    
    # Remover prefijos comunes
    for prefix in ['[Activo]', '[Castellano]', '[Dual-Audio]', '[Multi-audio]', '[Tri-Audio]']:
        clean_name = clean_name.replace(prefix, '').strip()
    
    # Ignorar caracteres especiales al inicio para ordenamiento
    special_chars = ''
    while clean_name and clean_name[0] in '¡¿!#$%&()*+,-./:;<=>?@[\\]^_`{|}~':
        special_chars += clean_name[0]
        clean_name = clean_name[1:].strip()
    
    return limpiar_texto(clean_name)

def limpiar_nombre_para_tmdb(title):
    """Limpiar nombre para búsqueda en TMDB"""
    # Remover prefijos y sufijos comunes
    clean_title = title
    
    # Remover prefijos
    for prefix in ['[Activo]', '[Castellano]', '[Dual-Audio]', '[Multi-audio]', '[Tri-Audio]']:
        clean_title = clean_title.replace(prefix, '').strip()
    
    # Remover información técnica entre corchetes
    clean_title = re.sub(r'\[.*?\]', '', clean_title).strip()
    
    # Remover año del final (TMDB lo maneja mejor)
    clean_title = re.sub(r'\s*\(\d{4}\)$', '', clean_title).strip()
    
    # Remover información adicional
    clean_title = re.sub(r'\s*\[.*?\]\s*$', '', clean_title).strip()
    clean_title = re.sub(r'\s*\(\d{4}/\d{4}\)\s*$', '', clean_title).strip()
    
    return clean_title

def buscar_en_tmdb(title, year, media_type="tv"):
    """Buscar en TMDB y obtener información detallada"""
    try:
        # Limpiar nombre para búsqueda
        search_title = limpiar_nombre_para_tmdb(title)
        
        # Headers para TMDB (usando query parameter en lugar de Bearer token)
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Primero buscar el título
        search_url = f"{TMDB_BASE_URL}/search/{media_type}"
        params = {
            'api_key': TMDB_API_KEY,
            'query': search_title,
            'language': TMDB_LANGUAGE,
            'year': year if year > 0 else None,
            'page': 1
        }
        
        print(f"   🔍 Buscando en TMDB: '{search_title}' ({year})")
        
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        search_data = response.json()
        
        if search_data.get('results') and len(search_data['results']) > 0:
            # Tomar el primer resultado
            result = search_data['results'][0]
            item_id = result['id']
            
            # Obtener información detallada
            detail_url = f"{TMDB_BASE_URL}/{media_type}/{item_id}"
            detail_params = {
                'api_key': TMDB_API_KEY,
                'language': TMDB_LANGUAGE,
                'append_to_response': 'genres'
            }
            
            detail_response = requests.get(detail_url, headers=headers, params=detail_params, timeout=10)
            detail_response.raise_for_status()
            
            detail_data = detail_response.json()
            
            # Extraer géneros
            genres = detail_data.get('genres', [])
            genre_names = [genre['name'] for genre in genres]
            
            # Información adicional
            first_air_date = detail_data.get('first_air_date') if media_type == "tv" else detail_data.get('release_date')
            overview = detail_data.get('overview', '')
            vote_average = detail_data.get('vote_average', 0)
            origin_country = detail_data.get('origin_country', [])
            original_language = detail_data.get('original_language', '')
            
            return {
                'genres': genre_names,
                'first_air_date': first_air_date,
                'overview': overview[:200] + '...' if len(overview) > 200 else overview,
                'vote_average': vote_average,
                'tmdb_id': item_id,
                'original_title': detail_data.get('original_name') if media_type == "tv" else detail_data.get('original_title'),
                'poster_path': detail_data.get('poster_path'),
                'backdrop_path': detail_data.get('backdrop_path'),
                'origin_country': origin_country,
                'original_language': original_language
            }
        
        return None
        
    except Exception as e:
        print(f"   ⚠️ Error en TMDB: {str(e)[:50]}...")
        return None

def mapear_genero_tmdb_a_nuestro(tmdb_genres):
    """Mapear géneros de TMDB a nuestro sistema - solo 1 género, nunca 'Animación' ni 'General'"""
    if not tmdb_genres:
        return "Drama"  # Fallback a Drama en lugar de General
    
    # Mapeo de géneros TMDB a nuestros géneros (prioridad, excluyendo Animación) - soporte para español e inglés
    genero_mapping = {
        # Acción y Aventura
        'Action': 'Acción',
        'Adventure': 'Aventura',
        'Action & Adventure': 'Acción',  # Inglés
        'Acción': 'Acción',  # Español
        'Aventura': 'Aventura',  # Español
        'Acción y Aventura': 'Acción',  # Español compuesto
        
        # Fantasía y Ciencia Ficción
        'Fantasy': 'Fantasía',
        'Science Fiction': 'Ciencia Ficción',
        'Sci-Fi & Fantasy': 'Ciencia Ficción',  # Inglés
        'Sci-Fi': 'Ciencia Ficción',  # Inglés corto
        'Fantasía': 'Fantasía',  # Español
        'Ciencia Ficción': 'Ciencia Ficción',  # Español
        'Ciencia ficción': 'Ciencia Ficción',  # Español (minúscula)
        'Ciencia-Ficción': 'Ciencia Ficción',  # Español con guion
        
        # Romance y Drama
        'Romance': 'Romance',
        'Drama': 'Drama',
        
        # Comedia (prioridad alta)
        'Comedy': 'Comedia',
        'Comedia': 'Comedia',  # Español
        
        # Terror y Thriller
        'Horror': 'Terror',
        'Thriller': 'Suspenso',  # Traducción al español
        'Mystery': 'Misterio',
        'Terror': 'Terror',  # Español
        'Suspenso': 'Suspenso',  # Español
        'Misterio': 'Misterio',  # Español
        
        # Infantil y Familiar
        'Family': 'Infantil',
        'Kids': 'Infantil',
        'Infantil': 'Infantil',  # Español
        'Familiar': 'Infantil',  # Español
        'Niños': 'Infantil',  # Español alternativo
        
        # Deportes
        'Sport': 'Deportes',
        'Sports': 'Deportes',
        'Deportes': 'Deportes',  # Español
        
        # Musical
        'Music': 'Musical',
        'Musical': 'Musical',  # Español
        'Música': 'Musical',  # Español alternativo
        
        # Guerra y Histórico
        'War': 'Bélico',  # Traducción más común
        'History': 'Histórico',
        'War & Politics': 'Bélico',
        'Guerra': 'Bélico',  # Español
        'Histórico': 'Histórico',  # Español
        'Bélico': 'Bélico',  # Español
        
        # Crimen y Policial
        'Crime': 'Crimen',
        'Crimen': 'Crimen',  # Español
        'Policial': 'Policial',  # Español
        
        # Documental
        'Documentary': 'Documental',
        'Documental': 'Documental',  # Español
        
        # Western
        'Western': 'Western',
        'Western': 'Western',  # Español
        
        # Biográfico
        'Biography': 'Biográfico',
        'Biográfico': 'Biográfico',  # Español
        
        # Reality y Televisión
        'Reality': 'Reality',
        'Talk': 'Talk Show',
        'News': 'Noticias',
        
        # Otros
        'TV Movie': 'Película TV',
        'Foreign': 'Extranjero',
        'TV': 'Drama',  # Cambiado de General a Drama
        'Animation': 'Animación',  # Para filtrar
        'Animación': 'Animación'  # Para filtrar
    }
    
    # Priorizar géneros principales (excluyendo Animation) - Comedia tiene máxima prioridad
    generos_prioritarios = ['Comedia', 'Drama', 'Acción', 'Aventura', 'Fantasía', 'Ciencia Ficción', 'Romance', 'Terror', 'Suspenso', 'Misterio', 'Deportes', 'Musical', 'Infantil', 'Crimen', 'Bélico', 'Histórico', 'Documental', 'Western', 'Biográfico']
    
    # Filtrar géneros TMDB, excluyendo "Animation" y "Animación"
    tmdb_generos_filtrados = [g for g in tmdb_genres if g not in ['Animation', 'Animación']]
    
    # Buscar en el orden ORIGINAL de TMDB y devolver el primer género prioritario encontrado
    for tmdb_genre in tmdb_generos_filtrados:
        if tmdb_genre in genero_mapping:
            nuestro_genero = genero_mapping[tmdb_genre]
            if nuestro_genero in generos_prioritarios:
                return nuestro_genero
    
    # Si no hay coincidencias prioritarias, usar la primera coincidencia
    for tmdb_genre in tmdb_generos_filtrados:
        if tmdb_genre in genero_mapping:
            return genero_mapping[tmdb_genre]
    
    # Si todos los géneros eran "Animation" o no hay coincidencias, devolver "Drama" en lugar de "General"
    return "Drama"

def clasificar_anime_vs_dibujos(tmdb_data):
    """Clasificar automáticamente entre Anime (Japón) y Dibujos (otros países) usando datos de TMDB"""
    if not tmdb_data:
        return 'anime'  # Por defecto, asumir anime
    
    origin_country = tmdb_data.get('origin_country', [])
    original_language = tmdb_data.get('original_language', '')
    
    # Si el país de origen es Japón (JP) o el idioma es japonés (ja)
    if 'JP' in origin_country or original_language == 'ja':
        return 'anime'
    
    # Si el país de origen es USA, Canadá, o países occidentales
    paises_occidentales = ['US', 'CA', 'GB', 'FR', 'DE', 'AU', 'NZ', 'ES', 'IT']
    if any(country in origin_country for country in paises_occidentales):
        return 'dibujos'
    
    # Si el idioma es inglés u otros idiomas occidentales (y no japonés)
    if original_language in ['en', 'fr', 'de', 'es', 'it']:
        return 'dibujos'
    
    # Por defecto, clasificar como anime si no se puede determinar
    return 'anime'

def clasificar_tipo_contenido(title):
    """Clasificar si es serie o película"""
    title_lower = title.lower()
    
    # Indicadores de película (más completos)
    indicadores_pelicula = [
        'pelicula', 'movie', 'film', 'la pelicula', 'el film',
        'zero', 'the movie', 'la película', 'pelicula:', 'movie:',
        'jin-roh', 'steamboy', 'brigada del lobo'
    ]
    
    # Indicadores de serie live-action
    indicadores_serie_live = [
        '[/', 'episodios', 'capitulos', 'temporada', 'season',
        'episode', 'chapter', 'tv series', 'serie'
    ]
    
    # Indicadores de anime/dibujos (prioridad alta)
    indicadores_anime = [
        'lady georgie', 'macross', 'gundam', 'dragon ball', 'sailor moon',
        'saint seiya', 'candy candy', 'heidi', 'marco', 'remi',
        'kimagure orange road', 'los caballeros del zodiaco', 'slam dunk',
        'captain tsubasa', 'los chicos del ma', 'bola de dragón'
    ]
    
    # Verificar si es película primero (prioridad alta)
    for indicador in indicadores_pelicula:
        if indicador in title_lower:
            return 'pelicula'
    
    # Verificar si es anime (prioridad alta para f11-castellano)
    for indicador in indicadores_anime:
        if indicador in title_lower:
            return 'anime'
    
    # Verificar si es serie live-action
    for indicador in indicadores_serie_live:
        if indicador in title_lower:
            return 'serie'
    
    # Si contiene "pelicula" o "movie" en cualquier parte
    if 'pelicula' in title_lower or 'movie' in title_lower:
        return 'pelicula'
    
    # Casos especiales conocidos (expandido)
    casos_especiales_pelicula = [
        'no game no life: zero',
        'boruto: naruto la pelicula',
        'psycho-pass: la película',
        'jin-roh: la brigada del lobo',
        'steamboy',
        'una carta para momo',
        'viaje a agartha',
        'death note relight',
        'la chica que saltaba a través del tiempo',
        'xxxholic: el sueño de una noche de verano'
    ]
    
    casos_especiales_anime = [
        'lady georgie',
        'macross plus',
        'macross ii lovers again',
        'harlock saga',
        'ah my goddess',
        'no game no life',
        'kimagure orange road',
        'captain tsubasa'
    ]
    
    for caso in casos_especiales_pelicula:
        if caso in title_lower:
            return 'pelicula'
    
    for caso in casos_especiales_anime:
        if caso in title_lower:
            return 'anime'
    
    # Si el título contiene año y no tiene indicadores de serie live-action, probablemente es película o anime
    year_match = re.search(r'\((\d{4})\)', title)
    if year_match and not any(ind in title_lower for ind in indicadores_serie_live):
        # Si es de los 80s o 90s y tiene características de anime, es anime
        year = int(year_match.group(1))
        if year <= 2000 and any(ind in title_lower for ind in indicadores_anime):
            return 'anime'
        return 'pelicula'
    
    return 'anime'  # Por defecto para f11-castellano (más probable que sea anime)

def clasificar_con_tmdb(title, year, tipo_contenido):
    """Clasificar usando TMDB"""
    if tipo_contenido == 'serie':
        tmdb_data = buscar_en_tmdb(title, year, "tv")
    else:  # película
        tmdb_data = buscar_en_tmdb(title, year, "movie")
    
    if tmdb_data and tmdb_data.get('genres'):
        # Mapear géneros de TMDB a nuestro sistema
        genero_nuestro = mapear_genero_tmdb_a_nuestro(tmdb_data['genres'])
        
        print(f"   ✅ TMDB géneros: {', '.join(tmdb_data['genres'])}")
        print(f"   ✅ Género asignado: {genero_nuestro}")
        
        return genero_nuestro, tmdb_data
    
    # Si TMDB falla, usar clasificación básica
    print(f"   ⚠️ TMDB no encontró resultados, usando clasificación básica")
    return "Drama", None

def extraer_contenido_seccion(url_base, seccion_id):
    """Extraer contenido de una sección específica con clasificación TMDB"""
    contenido_encontrado = []
    
    print(f"\n🚀 INICIANDO EXTRACCIÓN:")
    print(f"   📂 Sección ID: {seccion_id}")
    print(f"   🔗 URL Base: {url_base}")
    
    try:
        # Headers más completos para simular un navegador real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Explorar primeras páginas
        max_paginas = 12  # Procesar hasta 12 páginas para encontrar todas las películas
        
        for page_num in range(0, max_paginas):
            if page_num == 0:
                url = url_base
            else:
                # Corregir paginación para diferentes formatos de URL
                if url_base == "https://animezoneesp.foroactivo.com/f14-castellano":
                    # Para f14-castellano: f14-castellanop12, f14-castellanop24, etc.
                    url = f"https://animezoneesp.foroactivo.com/f14-castellanop{page_num * 12}"
                elif url_base == "https://animezoneesp.foroactivo.com/f11-castellano":
                    # Para f11-castellano: f11-castellanop12, f11-castellanop24, etc.
                    url = f"https://animezoneesp.foroactivo.com/f11-castellanop{page_num * 12}"
                else:
                    # Para f17-series: f17p12, f17p24, etc.
                    start_topic = page_num * 12
                    url = f"https://animezoneesp.foroactivo.com/f17p{start_topic}"
            
            print(f"\n📖 Página {page_num + 1}: {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=30)
                print(f"   📊 Status: {response.status_code}")
                print(f"   📏 Tamaño: {len(response.content)} bytes")
                
                if response.status_code != 200:
                    print(f"   ❌ Error HTTP: {response.status_code}")
                    continue
                    
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                topics = soup.find_all('a', class_='topictitle')
                
                print(f"   ✅ Encontrados {len(topics)} temas")
                
                if not topics:
                    print(f"   ❌ No se encontraron temas en página {page_num + 1}")
                    # Intentar buscar con otro selector
                    topics_alt = soup.find_all('a', href=lambda x: x and '/t' in x)
                    print(f"   🔍 Búsqueda alternativa: {len(topics_alt)} enlaces")
                    if topics_alt:
                        topics = topics_alt[:10]  # Limitar a 10
                    else:
                        break
                
                # Limitar procesamiento para evitar timeouts - REMOVIDO para procesar todos
                # max_items = 3 if seccion_id == "11" else 5  # Limitar f11 a 3 items
                # topics = topics[:max_items]
                # print(f"   📊 Procesando solo primeros {len(topics)} items")
                
                for i, topic in enumerate(topics):
                    title = topic.get_text(strip=True)
                    topic_url = urljoin("https://animezoneesp.foroactivo.com/", topic.get('href'))
                        
                    print(f"   📝 Tema {i+1}: {title}")
                        
                    # Extraer año
                    year_match = re.search(r'\((\d{4})\)', title)
                    year = int(year_match.group(1)) if year_match else 0
                        
                    # Clasificar tipo
                    tipo_detectado = clasificar_tipo_contenido(title)
                    print(f"      🔍 Tipo detectado: {tipo_detectado}")
                        
                    # Filtrar según el tipo que buscamos
                    if seccion_id == "14":  # Sección de películas
                        if tipo_detectado in ['pelicula', 'pack_peliculas']:
                            print(f"      ✅ Aceptado como película/pack")
                            # Clasificar con TMDB
                            genero_especifico, tmdb_data = clasificar_con_tmdb(title, year, tipo_detectado)
                                
                            contenido_info = {
                                'name': title,
                                'year': year,
                                'url': topic_url,
                                'href': topic.get('href', ''),
                                'type': 'Película' if tipo_detectado == 'pelicula' else 'Pack',
                                'genre': 'Animación Japonesa',
                                'confianza': 90,  # Mayor confianza con TMDB
                                'razonClasificacion': f"Clasificado con TMDB: {', '.join(tmdb_data['genres']) if tmdb_data and tmdb_data.get('genres') else 'Sin datos TMDB'}",
                                'specificGenre': genero_especifico,
                                'originalGenre': 'Animación Japonesa'
                            }
                                
                            contenido_encontrado.append(contenido_info)
                            print(f"      � Añadido: {title} - {genero_especifico}")
                        else:
                            print(f"      ❌ Rechazado (no es película): {tipo_detectado}")
                            print(f"   � {len(contenido_encontrado)}. {title} - {genero_especifico}")
                        
                    elif seccion_id == "11":  # Sección de series
                        if tipo_detectado == 'serie':
                            # Clasificar con TMDB
                            genero_especifico, tmdb_data = clasificar_con_tmdb(title, year, tipo_detectado)
                            
                            # Clasificar automáticamente entre anime y dibujos
                            tipo_animacion = clasificar_anime_vs_dibujos(tmdb_data)
                            
                            contenido_info = {
                                'name': title,
                                'year': year,
                                'url': topic_url,
                                'href': topic.get('href', ''),
                                'type': 'Anime' if tipo_animacion == 'anime' else 'Dibujos',
                                'genre': 'Animación Japonesa' if tipo_animacion == 'anime' else 'Animación Occidental',
                                'confianza': 90,  # Mayor confianza con TMDB
                                'razonClasificacion': f"Clasificado con TMDB: {', '.join(tmdb_data['genres']) if tmdb_data and tmdb_data.get('genres') else 'Sin datos TMDB'}",
                                'specificGenre': genero_especifico,
                                'originalGenre': 'Animación Japonesa' if tipo_animacion == 'anime' else 'Animación Occidental',
                                'tmdb_type': tipo_animacion  # Guardar el tipo para filtrado
                            }
                            
                            contenido_encontrado.append(contenido_info)
                            tipo_label = "🎌 ANIME" if tipo_animacion == 'anime' else "📺 DIBUJOS"
                            print(f"   {tipo_label} {len(contenido_encontrado)}. {title} - {genero_especifico}")
                    
                    elif seccion_id == "17":  # Sección de series live-action
                        if tipo_detectado == 'serie':
                            # Clasificar con TMDB
                            genero_especifico, tmdb_data = clasificar_con_tmdb(title, year, 'serie')
                            
                            contenido_info = {
                                'name': title,
                                'year': year,
                                'url': topic_url,
                                'href': topic.get('href', ''),
                                'type': 'Serie Live-Action',
                                'genre': 'Live-Action',
                                'confianza': 90,  # Mayor confianza con TMDB
                                'razonClasificacion': f"Clasificado con TMDB: {', '.join(tmdb_data['genres']) if tmdb_data and tmdb_data.get('genres') else 'Sin datos TMDB'}",
                                'specificGenre': genero_especifico,
                                'originalGenre': 'Live-Action'
                            }
                            
                            contenido_encontrado.append(contenido_info)
                            print(f"   📺 SERIES {len(contenido_encontrado)}. {title} - {genero_especifico}")
                
                # Pausa más larga para evitar bloqueos (3 segundos)
                time.sleep(3)
                
            except Exception as e:
                print(f"   ⚠️ Error en página {page_num + 1}: {str(e)[:50]}...")
                continue
                
    except Exception as e:
        print(f"❌ Error general: {e}")
        return []
    
    return contenido_encontrado

def actualizar_top_json_con_tmdb():
    """Función principal de actualización automática con TMDB"""
    
    print(f"🔄 Actualización Automática con TMDB - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Verificar si hay API key de TMDB
    if TMDB_API_KEY == "TU_API_KEY_AQUI":
        print("❌ ERROR: Debes configurar tu API key de TMDB")
        print("📝 Para obtener una API key:")
        print("   1. Regístrate en https://www.themoviedb.org/")
        print("   2. Ve a Configuración > API > Solicitar API key")
        print("   3. Edita este archivo y reemplaza 'TU_API_KEY_AQUI' con tu key")
        return
    
    # Cargar TOP.json actual
    print("✅ Cargando TOP.json actual...")
    try:
        with open('TOP.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error al cargar TOP.json: {e}")
        return
    
    # Obtener contenido existente
    anime_existente = data.get('anime', [])
    dibujos_existente = data.get('dibujos', [])
    peliculas_existente = data.get('peliculas', [])
    
    # Asegurar que existe la sección series
    if 'series' not in data:
        data['series'] = []
        print(f"📋 Creando sección 'series' (no existía)")
    
    series_existente = data.get('series', [])
    
    # Asegurar que existe el resumen de series
    if 'series' not in data.get('resumen', {}):
        data['resumen']['series'] = 0
        print(f"📋 Añadiendo 'series' al resumen")
    
    print(f"✅ Cargados {len(anime_existente)} animes, {len(dibujos_existente)} dibujos, {len(peliculas_existente)} películas, {len(series_existente)} series")
    
    # Extraer contenido nuevo del foro con TMDB
    print(f"\n🎬 Buscando nuevas películas en sección castellano (con TMDB)...")
    print(f"🔗 URL: https://animezoneesp.foroactivo.com/f14-castellano")
    try:
        nuevas_peliculas = extraer_contenido_seccion("https://animezoneesp.foroactivo.com/f14-castellano", "14")
        print(f"📊 Resultado f14: {len(nuevas_peliculas)} películas encontradas")
        
        # Debug: Mostrar primeras películas encontradas
        if nuevas_peliculas:
            print(f"🔍 Primeras películas encontradas:")
            for i, pelicula in enumerate(nuevas_peliculas[:3]):
                print(f"   {i+1}. {pelicula.get('name', 'SIN NOMBRE')}")
        else:
            print(f"❌ No se encontraron películas en f14-castellano")
    except Exception as e:
        print(f"❌ ERROR en f14-castellano: {e}")
        nuevas_peliculas = []
    
    print(f"\n📺 Buscando nuevas series en sección castellano (con TMDB)...")
    try:
        nuevas_series = extraer_contenido_seccion("https://animezoneesp.foroactivo.com/f11-castellano", "11")
        print(f"📊 Resultado f11: {len(nuevas_series)} series encontradas")
    except Exception as e:
        print(f"❌ ERROR en f11-castellano: {e}")
        nuevas_series = []
    
    print(f"\n📋 Buscando nuevas series en sección Series (con TMDB)...")
    nuevas_series_f17 = extraer_contenido_seccion("https://animezoneesp.foroactivo.com/f17-series", "17")
    
    # Extraer también la página 12 de series
    print(f"\n📋 Buscando nuevas series en sección Series - Página 12 (con TMDB)...")
    nuevas_series_f17_p12 = extraer_contenido_seccion("https://animezoneesp.foroactivo.com/f17p12-series", "17")
    
    # Temporalmente comentado para diagnosticar f14
    # # Buscar también en otras secciones de películas
    # print(f"\n🎬 Buscando películas en sección Películas (con TMDB)...")
    # nuevas_peliculas_extra = extraer_contenido_seccion("https://animezoneesp.foroactivo.com/f5-peliculas", "5")
    
    # print(f"\n🎬 Buscando películas en sección Películas - Página 2 (con TMDB)...")
    # nuevas_peliculas_p2 = extraer_contenido_seccion("https://animezoneesp.foroactivo.com/f5p15-peliculas", "5")
    
    # Combinar todas las películas
    todas_peliculas = nuevas_peliculas
    print(f"\n🔍 Extracción de películas:")
    print(f"   f14-castellano: {len(nuevas_peliculas)}")
    print(f"   Total películas: {len(todas_peliculas)}")
    
    print(f"\n📋 Buscando nuevas series en sección Series (con TMDB)...")
    nuevas_series_f17 = extraer_contenido_seccion("https://animezoneesp.foroactivo.com/f17-series", "17")
    
    # Extraer también la página 12 de series
    print(f"\n📋 Buscando nuevas series en sección Series - Página 12 (con TMDB)...")
    nuevas_series_f17_p12 = extraer_contenido_seccion("https://animezoneesp.foroactivo.com/f17p12-series", "17")
    
    # Combinar todas las series de f17
    todas_series_f17 = nuevas_series_f17 + nuevas_series_f17_p12
    
    print(f"\n🔍 Extracción de series live-action:")
    print(f"   f17-series encontradas: {len(nuevas_series_f17)}")
    print(f"   f17p12-series encontradas: {len(nuevas_series_f17_p12)}")
    print(f"   Total series live-action: {len(todas_series_f17)}")
    
    # Mostrar las series encontradas
    if todas_series_f17:
        print(f"\n📋 Series live-action encontradas:")
        for i, serie in enumerate(todas_series_f17, 1):
            name = serie.get('name', '')
            print(f"   {i}. {name}")
    else:
        print(f"\n⚠️ No se encontraron series live-action en f17 o f17p12")
    
    # Filtrar contenido nuevo (que no existe ya)
    def filtrar_nuevos(contenido_nuevo, contenido_existente):
        nuevos = []
        nombres_existentes = set()
        
        print(f"\n🔍 FILTRADO DETALLADO:")
        print(f"   📥 Items nuevos a filtrar: {len(contenido_nuevo)}")
        print(f"   📋 Items existentes: {len(contenido_existente)}")
        
        # Crear conjunto de nombres existentes
        for item in contenido_existente:
            nombre_limpio = limpiar_texto(item.get('name', ''))
            nombres_existentes.add(nombre_limpio)
        
        print(f"   📝 Nombres existentes únicos: {len(nombres_existentes)}")
        
        # Filtrar solo los que no existen
        duplicados_encontrados = 0
        for i, item in enumerate(contenido_nuevo):
            nombre_limpio = limpiar_texto(item.get('name', ''))
            print(f"   📝 Item {i+1}: {nombre_limpio}")
            
            if nombre_limpio not in nombres_existentes:
                nuevos.append(item)
                nombres_existentes.add(nombre_limpio)
                print(f"      ✅ NUEVO: {nombre_limpio}")
            else:
                duplicados_encontrados += 1
                print(f"      ❌ DUPLICADO: {nombre_limpio}")
                # Mostrar qué nombre existente coincide
                for existente in nombres_existentes:
                    if existente == nombre_limpio:
                        print(f"         ↔️ Coincide con: {existente}")
                        break
        
        print(f"📊 Resultado filtrado: {len(nuevos)} nuevos, {duplicados_encontrados} duplicados")
        return nuevos
    
    # Para series de f17, guardar siempre (son live-action, van en su propia sección)
    series_nuevas_unicas = todas_series_f17  # No filtrar duplicados para series live-action
    peliculas_nuevas_unicas = filtrar_nuevos(todas_peliculas, peliculas_existente)
    
    # Búsqueda específica para películas que podrían estar en otras secciones
    print(f"\n🔍 Búsqueda específica de películas populares...")
    busqueda_especifica = ["no game no life", "no game no life zero", "game no life"]
    peliculas_perdidas = []
    
    for termino in busqueda_especifica:
        encontrado = False
        for pelicula in peliculas_existente:
            if termino in limpiar_texto(pelicula.get('name', '').lower()):
                encontrado = True
                print(f"✅ Encontrado: {termino} -> {pelicula.get('name', '')}")
                break
        if not encontrado:
            peliculas_perdidas.append(termino)
            print(f"❌ NO encontrado: {termino}")
    
    if peliculas_perdidas:
        print(f"\n⚠️ Películas no encontradas en el sistema: {', '.join(peliculas_perdidas)}")
        print(f"💡 Sugerencia: Podrían estar en otras secciones del foro no monitoreadas")
    
    # Las series de f17 van directamente a la sección series (son live-action, no animación)
    # No se clasifican como anime/dibujos porque son de personas reales
    
    print(f"\n📊 Resultados:")
    print(f"   Series encontradas en f17: {len(todas_series_f17)}")
    print(f"   Películas nuevas: {len(peliculas_nuevas_unicas)}")
    
    # Actualizar series de f17 (siempre que se encuentren)
    if todas_series_f17:
        print(f"\n🔄 Actualizando series de f17 (live-action)...")
        
        # Reemplazar series con las de f17 (son live-action)
        data['series'] = todas_series_f17
        
        # Ordenar series
        series_ordenadas = sorted(todas_series_f17, key=get_sort_name_perfect)
        data['series'] = series_ordenadas
        
        # Mostrar las series
        print(f"\n📋 Series de f17 (live-action):")
        for i, serie in enumerate(series_ordenadas, 1):
            name = serie.get('name', '')
            clean_name = re.sub(r'\[.*?\]', '', name).strip()
            genero = serie.get('specificGenre', '')
            tmdb_genres = serie.get('tmdb_genres', [])
            tmdb_text = f" (TMDB: {', '.join(tmdb_genres)})" if tmdb_genres else ""
            print(f"   {i}. {clean_name} - {genero}{tmdb_text}")
        
        print(f"   ✅ {len(series_ordenadas)} series actualizadas")
    
    # Añadir películas nuevas si hay
    if peliculas_nuevas_unicas:
        peliculas_existente.extend(peliculas_nuevas_unicas)
        print(f"   ✅ {len(peliculas_nuevas_unicas)} películas añadidas")
    
    # Actualizar resumen
    total_anime = len(anime_existente)
    total_dibujos = len(dibujos_existente)
    total_peliculas = len(peliculas_existente)
    total_series = len(data.get('series', []))
    total_nuevo = total_anime + total_dibujos + total_peliculas + total_series
    data['resumen']['total'] = total_nuevo
    data['resumen']['series'] = total_series
    data['resumen']['anime'] = total_anime
    data['resumen']['dibujos'] = total_dibujos
    data['resumen']['peliculas'] = total_peliculas
    
    # Guardar archivo
    print(f"\n💾 Guardando TOP.json actualizado...")
    try:
        with open('TOP.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ TOP.json actualizado exitosamente")
        print(f"🎉 ¡Actualización completada!")
        print(f"📊 Total de entradas: {total_nuevo}")
        print(f"� Series live-action: {total_series}")
    except Exception as e:
        print(f"❌ Error al guardar: {e}")
        return
    
    print(f"\n🏁 Proceso de actualización automática con TMDB finalizado.")

# Ejecutar actualización
if __name__ == "__main__":
    actualizar_top_json_con_tmdb()
