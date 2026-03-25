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
            
            return {
                'genres': genre_names,
                'first_air_date': first_air_date,
                'overview': overview[:200] + '...' if len(overview) > 200 else overview,
                'vote_average': vote_average,
                'tmdb_id': item_id,
                'original_title': detail_data.get('original_name') if media_type == "tv" else detail_data.get('original_title'),
                'poster_path': detail_data.get('poster_path'),
                'backdrop_path': detail_data.get('backdrop_path')
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

def clasificar_tipo_contenido(title):
    """Determinar si es película, serie o pack"""
    title_lower = title.lower()
    
    # Indicadores de película
    indicadores_pelicula = [
        'pelicula', 'película', '[1/1]', 'movie', 'film', 'the movie',
        'la película', 'la pelicula'
    ]
    
    # Packs de películas
    indicadores_pack_peliculas = [
        'pack películas', 'pack peliculas', 'peliculas pack',
        'pack movie', 'movie pack'
    ]
    
    # Indicadores de series
    indicadores_serie = [
        '[/', 'episodios', 'capitulos', 'temporada', 'season',
        'episode', 'chapter', 'tv series', 'serie'
    ]
    
    # Verificar si es serie
    for indicador in indicadores_serie:
        if indicador in title_lower:
            return 'serie'
    
    # Verificar si es película
    for indicador in indicadores_pelicula:
        if indicador in title_lower:
            return 'pelicula'
    
    # Verificar si es pack de películas
    for indicador in indicadores_pack_peliculas:
        if indicador in title_lower:
            return 'pack_peliculas'
    
    return 'serie'  # Por defecto

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
        max_paginas = 5
        
        for page_num in range(0, max_paginas):
            if page_num == 0:
                url = url_base
            else:
                start_topic = page_num * 12
                url = f"https://animezoneesp.foroactivo.com/f{seccion_id}p{start_topic}"
            
            print(f"📖 Explorando página {page_num + 1}: {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                topics = soup.find_all('a', class_='topictitle')
                
                if not topics:
                    print(f"   ❌ No se encontraron temas en página {page_num + 1}")
                    break
                
                print(f"   ✅ Encontrados {len(topics)} temas")
                
                for i, topic in enumerate(topics):
                    title = topic.get_text(strip=True)
                    topic_url = urljoin("https://animezoneesp.foroactivo.com/", topic.get('href'))
                    
                    # Extraer año
                    year_match = re.search(r'\((\d{4})\)', title)
                    year = int(year_match.group(1)) if year_match else 0
                    
                    # Clasificar tipo
                    tipo_detectado = clasificar_tipo_contenido(title)
                    
                    # Filtrar según el tipo que buscamos
                    if seccion_id == "14":  # Sección de películas
                        if tipo_detectado in ['pelicula', 'pack_peliculas']:
                            # Clasificar con TMDB
                            genero_especifico, tmdb_data = clasificar_con_tmdb(title, year, tipo_detectado)
                            
                            contenido_info = {
                                'name': title,
                                'year': year,
                                'url': topic_url,
                                'href': topic.get('href', ''),
                                'type': 'Película',
                                'genre': 'Animación Japonesa',
                                'confianza': 90,  # Mayor confianza con TMDB
                                'razonClasificacion': f"Clasificado con TMDB: {', '.join(tmdb_data['genres']) if tmdb_data and tmdb_data.get('genres') else 'Sin datos TMDB'}",
                                'specificGenre': genero_especifico,
                                'originalGenre': 'Animación Japonesa'
                            }
                            
                            contenido_encontrado.append(contenido_info)
                            print(f"   📺 {len(contenido_encontrado)}. {title} - {genero_especifico}")
                    
                    elif seccion_id == "11":  # Sección de series
                        if tipo_detectado == 'serie':
                            # Clasificar con TMDB
                            genero_especifico, tmdb_data = clasificar_con_tmdb(title, year, tipo_detectado)
                            
                            contenido_info = {
                                'name': title,
                                'year': year,
                                'url': topic_url,
                                'href': topic.get('href', ''),
                                'type': 'Anime',
                                'genre': 'Animación Japonesa',
                                'confianza': 90,  # Mayor confianza con TMDB
                                'razonClasificacion': f"Clasificado con TMDB: {', '.join(tmdb_data['genres']) if tmdb_data and tmdb_data.get('genres') else 'Sin datos TMDB'}",
                                'specificGenre': genero_especifico,
                                'originalGenre': 'Animación Japonesa'
                            }
                            
                            contenido_encontrado.append(contenido_info)
                            print(f"   📺 {len(contenido_encontrado)}. {title} - {genero_especifico}")
                
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
    peliculas_existente = data.get('peliculas', [])
    
    print(f"✅ Cargados {len(anime_existente)} animes, {len(peliculas_existente)} películas")
    
    # Extraer contenido nuevo del foro con TMDB
    print(f"\n📺 Buscando nuevas series en sección castellano (con TMDB)...")
    nuevas_series = extraer_contenido_seccion("https://animezoneesp.foroactivo.com/f11-castellano", "11")
    
    print(f"\n🎬 Buscando nuevas películas en sección castellano (con TMDB)...")
    nuevas_peliculas = extraer_contenido_seccion("https://animezoneesp.foroactivo.com/f14-castellano", "14")
    
    # Filtrar contenido nuevo (que no existe ya)
    def filtrar_nuevos(contenido_nuevo, contenido_existente):
        nuevos = []
        nombres_existentes = set()
        
        # Crear conjunto de nombres existentes
        for item in contenido_existente:
            nombre_limpio = limpiar_texto(item.get('name', ''))
            nombres_existentes.add(nombre_limpio)
        
        # Filtrar solo los que no existen
        for item in contenido_nuevo:
            nombre_limpio = limpiar_texto(item.get('name', ''))
            if nombre_limpio not in nombres_existentes:
                nuevos.append(item)
                nombres_existentes.add(nombre_limpio)
        
        return nuevos
    
    series_nuevas_unicas = filtrar_nuevos(nuevas_series, anime_existente)
    peliculas_nuevas_unicas = filtrar_nuevos(nuevas_peliculas, peliculas_existente)
    
    print(f"\n📊 Resultados:")
    print(f"   Series nuevas válidas: {len(series_nuevas_unicas)}")
    print(f"   Películas nuevas válidas: {len(peliculas_nuevas_unicas)}")
    
    # Si hay contenido nuevo, añadirlo
    if series_nuevas_unicas or peliculas_nuevas_unicas:
        print(f"\n➕ Añadiendo contenido nuevo...")
        
        # Añadir series nuevas
        if series_nuevas_unicas:
            anime_existente.extend(series_nuevas_unicas)
            print(f"   ✅ {len(series_nuevas_unicas)} series añadidas")
            
            # Mostrar las series añadidas
            print(f"\n📺 Series añadidas:")
            for i, serie in enumerate(series_nuevas_unicas, 1):
                name = serie.get('name', '')
                clean_name = re.sub(r'\[.*?\]', '', name).strip()
                genero = serie.get('specificGenre', '')
                tmdb_genres = serie.get('tmdb_genres', [])
                tmdb_text = f" (TMDB: {', '.join(tmdb_genres)})" if tmdb_genres else ""
                print(f"   {i}. {clean_name} - {genero}{tmdb_text}")
        
        # Añadir películas nuevas
        if peliculas_nuevas_unicas:
            peliculas_existente.extend(peliculas_nuevas_unicas)
            print(f"   ✅ {len(peliculas_nuevas_unicas)} películas añadidas")
            
            # Mostrar las películas añadidas
            print(f"\n🎬 Películas añadidas:")
            for i, pelicula in enumerate(peliculas_nuevas_unicas, 1):
                name = pelicula.get('name', '')
                clean_name = re.sub(r'\[.*?\]', '', name).strip()
                genero = pelicula.get('specificGenre', '')
                tmdb_genres = pelicula.get('tmdb_genres', [])
                tmdb_text = f" (TMDB: {', '.join(tmdb_genres)})" if tmdb_genres else ""
                print(f"   {i}. {clean_name} - {genero}{tmdb_text}")
        
        # Ordenar todo
        print(f"\n🔄 Ordenando contenido...")
        anime_existente = sorted(anime_existente, key=get_sort_name_perfect)
        peliculas_existente = sorted(peliculas_existente, key=get_sort_name_perfect)
        
        # Actualizar datos
        data['anime'] = anime_existente
        data['peliculas'] = peliculas_existente
        
        # Actualizar resumen
        total_actual = data['resumen']['total']
        total_nuevo = total_actual + len(series_nuevas_unicas) + len(peliculas_nuevas_unicas)
        data['resumen']['total'] = total_nuevo
        data['resumen']['anime'] = len(anime_existente)
        data['resumen']['peliculas'] = len(peliculas_existente)
        
        # Guardar archivo
        print(f"\n💾 Guardando TOP.json actualizado...")
        try:
            with open('TOP.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ TOP.json actualizado exitosamente")
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
            return
        
        print(f"\n🎉 ¡Actualización completada con TMDB!")
        print(f"📊 Total de entradas: {total_nuevo}")
        
    else:
        print(f"\n✅ No hay contenido nuevo válido. TOP.json está actualizado.")
    
    print(f"\n🏁 Proceso de actualización automática con TMDB finalizado.")

# Ejecutar actualización
if __name__ == "__main__":
    actualizar_top_json_con_tmdb()
