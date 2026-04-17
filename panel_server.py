#!/usr/bin/env python3
"""
Servidor API para el Panel de Control de Anime Zone ESP
Permite leer y escribir en TOP.json de forma segura
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import subprocess
import shutil

app = Flask(__name__)
CORS(app)  # Permitir CORS para desarrollo local

# Ruta al archivo TOP.json
TOP_JSON_PATH = os.path.join(os.path.dirname(__file__), 'TOP.json')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups')

# Asegurar que existe el directorio de backups
os.makedirs(BACKUP_DIR, exist_ok=True)


def load_top_json():
    """Cargar TOP.json"""
    try:
        if os.path.exists(TOP_JSON_PATH):
            with open(TOP_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "resumen": {
                "anime": 0,
                "dibujos": 0,
                "peliculas": 0,
                "series": 0,
                "total": 0,
                "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "anime": [],
            "dibujos": [],
            "peliculas": [],
            "series": []
        }
    except Exception as e:
        print(f"❌ Error cargando TOP.json: {e}")
        return None


def save_top_json(data):
    """Guardar TOP.json con backup"""
    try:
        # Crear backup antes de guardar
        if os.path.exists(TOP_JSON_PATH):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(BACKUP_DIR, f'TOP_backup_{timestamp}.json')
            with open(TOP_JSON_PATH, 'r', encoding='utf-8') as f:
                with open(backup_path, 'w', encoding='utf-8') as bf:
                    bf.write(f.read())
        
        # Actualizar resumen
        data['resumen'] = {
            "anime": len(data.get('anime', [])),
            "dibujos": len(data.get('dibujos', [])),
            "peliculas": len(data.get('peliculas', [])),
            "series": len(data.get('series', [])),
            "total": (
                len(data.get('anime', [])) +
                len(data.get('dibujos', [])) +
                len(data.get('peliculas', [])) +
                len(data.get('series', []))
            ),
            "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Guardar archivo
        with open(TOP_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"❌ Error guardando TOP.json: {e}")
        return False


@app.route('/')
def index():
    """Servir el panel de control"""
    return send_from_directory('.', 'panel_control.html')


@app.route('/<path:filename>')
def static_files(filename):
    """Servir archivos estáticos"""
    return send_from_directory('.', filename)


@app.route('/api/data', methods=['GET'])
def get_data():
    """Obtener todos los datos"""
    data = load_top_json()
    if data is None:
        return jsonify({"error": "No se pudo cargar TOP.json"}), 500
    return jsonify(data)


@app.route('/api/data', methods=['POST'])
def save_data():
    """Guardar todos los datos"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        # Validar estructura básica
        required_keys = ['anime', 'dibujos', 'peliculas', 'series']
        for key in required_keys:
            if key not in data:
                return jsonify({"error": f"Falta clave requerida: {key}"}), 400
        
        if save_top_json(data):
            return jsonify({"success": True, "message": "Datos guardados correctamente"})
        else:
            return jsonify({"error": "No se pudo guardar TOP.json"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtener estadísticas"""
    data = load_top_json()
    if data is None:
        return jsonify({"error": "No se pudo cargar TOP.json"}), 500
    
    return jsonify(data.get('resumen', {}))


@app.route('/api/series', methods=['GET'])
def get_series():
    """Obtener series con filtros opcionales"""
    data = load_top_json()
    if data is None:
        return jsonify({"error": "No se pudo cargar TOP.json"}), 500
    
    category = request.args.get('category', 'all')
    search = request.args.get('search', '').lower()
    
    series = []
    categories = ['anime', 'dibujos', 'peliculas', 'series'] if category == 'all' else [category]
    
    for cat in categories:
        if cat in data:
            for item in data[cat]:
                item['_categoria'] = cat
                series.append(item)
    
    # Aplicar búsqueda
    if search:
        series = [s for s in series if 
                  search in s.get('name', '').lower() or
                  search in s.get('genre', '').lower() or
                  search in str(s.get('year', '')).lower()]
    
    return jsonify(series)


@app.route('/api/series/add', methods=['POST'])
def add_series():
    """Añadir nueva serie"""
    try:
        data = request.get_json()
        print(f"[DEBUG] Datos recibidos: {data}")
        
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        # Verificar campos requeridos
        campos_requeridos = ['name', 'type', 'url']
        faltantes = [c for c in campos_requeridos if not data.get(c)]
        if faltantes:
            return jsonify({"error": f"Campos faltantes: {faltantes}"}), 400
        
        # Obtener catálogo actual
        catalogo = load_top_json()
        if catalogo is None:
            return jsonify({"error": "No se pudo cargar TOP.json"}), 500
        
        # Determinar categoría según tipo
        tipo = data.get('type', '')
        categoria_map = {
            'Anime': 'anime',
            'Dibujos': 'dibujos',
            'Película': 'peliculas',
            'Serie Live-Action': 'series'
        }
        categoria = categoria_map.get(tipo)
        print(f"[DEBUG] Tipo: {tipo}, Categoría: {categoria}")
        
        if not categoria:
            return jsonify({"error": f"Tipo no válido: {tipo}. Use: Anime, Dibujos, Película, Serie Live-Action"}), 400
        
        # Verificar duplicados
        nombre = data.get('name', '')
        nombre_normalizado = nombre.lower().strip()
        
        for cat in catalogo.values():
            if isinstance(cat, list):
                for item in cat:
                    if item.get('name', '').lower().strip() == nombre_normalizado:
                        return jsonify({"error": "Esta serie ya existe", "duplicate": True}), 409
        
        # Añadir metadatos
        data['fecha_adicion'] = datetime.now().isoformat()
        data['confianza'] = 100  # Manual = máxima confianza
        
        # Añadir a catálogo
        catalogo[categoria].append(data)
        
        if save_top_json(catalogo):
            return jsonify({
                "success": True, 
                "message": f"Serie añadida a {tipo}",
                "data": data
            })
        else:
            return jsonify({"error": "No se pudo guardar"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/series/<categoria>/<int:index>', methods=['PUT'])
def update_series(categoria, index):
    """Actualizar serie existente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        catalogo = load_top_json()
        if catalogo is None:
            return jsonify({"error": "No se pudo cargar TOP.json"}), 500
        
        if categoria not in catalogo or index >= len(catalogo[categoria]):
            return jsonify({"error": "Serie no encontrada"}), 404
        
        # Actualizar datos preservando metadatos originales
        original = catalogo[categoria][index]
        updated = {**original, **data, 'fecha_modificacion': datetime.now().isoformat()}
        catalogo[categoria][index] = updated
        
        if save_top_json(catalogo):
            return jsonify({
                "success": True,
                "message": "Serie actualizada",
                "data": updated
            })
        else:
            return jsonify({"error": "No se pudo guardar"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/series/<categoria>/<int:index>', methods=['DELETE'])
def delete_series(categoria, index):
    """Eliminar serie"""
    try:
        catalogo = load_top_json()
        if catalogo is None:
            return jsonify({"error": "No se pudo cargar TOP.json"}), 500
        
        if categoria not in catalogo or index >= len(catalogo[categoria]):
            return jsonify({"error": "Serie no encontrada"}), 404
        
        deleted = catalogo[categoria].pop(index)
        
        if save_top_json(catalogo):
            return jsonify({
                "success": True,
                "message": "Serie eliminada",
                "data": deleted
            })
        else:
            return jsonify({"error": "No se pudo guardar"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/backups', methods=['GET'])
def list_backups():
    """Listar backups disponibles"""
    try:
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith('TOP_backup_') and filename.endswith('.json'):
                filepath = os.path.join(BACKUP_DIR, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        backups.sort(key=lambda x: x['created'], reverse=True)
        return jsonify(backups)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/restore/<filename>', methods=['POST'])
def restore_backup(filename):
    """Restaurar desde backup"""
    try:
        backup_path = os.path.join(BACKUP_DIR, filename)
        if not os.path.exists(backup_path):
            return jsonify({"error": "Backup no encontrado"}), 404
        
        # Validar que es JSON válido
        with open(backup_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Guardar como TOP.json actual
        if save_top_json(data):
            return jsonify({"success": True, "message": "Backup restaurado"})
        else:
            return jsonify({"error": "No se pudo restaurar"}), 500
    
    except json.JSONDecodeError:
        return jsonify({"error": "Archivo de backup corrupto"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/extract', methods=['POST'])
def extract_from_url():
    """Extraer información de una URL del foro"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL requerida"}), 400
        
        url = data['url']
        default_type = data.get('defaultType', '')  # Tipo por defecto del batch
        
        # Validar URL del foro
        if 'animezoneesp.foroactivo.com' not in url:
            return jsonify({"error": "URL debe ser del foro animezoneesp"}), 400
        
        # Hacer scraping
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer título del tema - probar múltiples selectores
        title = ''
        
        # 1. Buscar h1 con clase page-title
        title_elem = soup.find('h1', class_='page-title')
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        # 2. Buscar en el título de la página (title tag)
        if not title:
            title_elem = soup.find('title')
            if title_elem:
                title = title_elem.get_text(strip=True)
        
        # 3. Buscar en h1 general
        if not title:
            title_elem = soup.find('h1')
            if title_elem:
                title = title_elem.get_text(strip=True)
        
        # 4. Buscar meta tag con título del tema
        if not title:
            meta_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'title'})
            if meta_title:
                title = meta_title.get('content', '')
        
        # Limpiar título agresivamente
        # Quitar prefijo del foro
        title = re.sub(r'^(Anime Zone ESP|Foroactivo)\s*-\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*-\s*(Anime Zone ESP|Foroactivo)$', '', title, flags=re.IGNORECASE)
        
        # Quitar [Activo], [Cerrado], etc. al inicio
        title = re.sub(r'^\[.*?\]\s*', '', title)
        
        # Quitar número de tema al inicio (ej: "t1701 - ")
        title = re.sub(r'^t\d+\s*-\s*', '', title, flags=re.IGNORECASE)
        
        # Extraer año ANTES de limpiar los paréntesis
        year_match = re.search(r'\((\d{4})\)', title)
        year = int(year_match.group(1)) if year_match else None
        
        # Quitar año entre paréntesis
        title = re.sub(r'\s*\(\d{4}\)', '', title)
        
        # Quitar TODA la información técnica entre corchetes
        title = re.sub(r'\s*\[.*?\]', '', title)
        
        # Limpiar espacios múltiples
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Determinar tipo basado en el título y URL
        tipo = detect_type(title, url)
        
        # Si no se detectó tipo y hay default_type, usar ese
        if not tipo or tipo == 'Anime':  # Anime es el default genérico
            if default_type:
                tipo = default_type
        
        # Extraer información adicional del primer post
        first_post = soup.find('div', class_='postbody')
        content = ''
        if first_post:
            content = first_post.get_text(separator=' ', strip=True)
        
        # Extraer género específico del contenido del post (patrón: 📺 Género: X, Y, Z)
        genero_principal, generos_especificos = extract_genre_from_post(content)
        
        # Si encontramos género en el post, usarlo
        if genero_principal:
            genero_default = genero_principal
        else:
            genero_default = get_default_genre(tipo)
        
        # Construir género específico incluyendo el género principal también
        genero_completo = generos_especificos if generos_especificos else genero_default
        
        result = {
            "success": True,
            "data": {
                "name": title,
                "year": year,
                "type": tipo,
                "genre": genero_default,  # Género principal (primer género encontrado)
                "specificGenre": genero_completo,  # Todos los géneros incluyendo el principal
                "url": url,
                "href": extract_href(url),
                "razonClasificacion": f"Extraído automáticamente del foro - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
        }
        
        return jsonify(result)
        
    except requests.RequestException as e:
        return jsonify({"error": f"Error conectando al foro: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error extrayendo información: {str(e)}"}), 500


def detect_type(title, url):
    """Detectar tipo de serie basado en título"""
    title_lower = title.lower()
    
    # Indicadores de película
    if any(x in title_lower for x in ['película', 'pelicula', 'movie', 'film']):
        return 'Película'
    
    # Indicadores de dibujos/animación occidental
    indicadores_dibujos = [
        'robocop', 'strange planet', 'un planeta extraño', 'sin supervision',
        'lucky luke', 'pingu', 'capitan biceps', 'jimmy neutron',
        'rick and morty', 'family guy', 'simpsons',
        'south park', 'futurama', 'archer', 'bojack', 'big mouth',
        'disenchantment', 'f is for family', 'love death robots',
        'invincible', 'harley quinn', 'primal', 'venture bros',
        'american dad', 'bob\'s burgers', 'king of the hill',
        'beavis', 'butt-head', 'daria', 'clone high',
        'spawn', 'aeon flux', 'reign', 'mission hill',
        'superman', 'batman', 'justice league', 'teen titans',
        'avatar', 'korra', 'last airbender',
        'gravity falls', 'adventure time', 'regular show',
        'steven universe', 'we bare bears', 'amphibia',
        'owl house', 'ducktales', 'darkwing duck',
        'gargoyles', 'aladdin', 'hercules', 'tarzan',
        'lion king', 'toy story', 'cars', 'finding nemo',
        'incredibles', 'shrek', 'kung fu panda',
        'madagascar', 'ice age', 'rio',
        'hotel transylvania', 'cloudy with a chance',
        'spider-verse', 'into the spider-verse',
        'coco', 'moana', 'frozen', 'tanglet',
        'brave', 'wreck-it ralph', 'zootopia',
        'big hero', 'baymax'
    ]
    
    if any(ind in title_lower for ind in indicadores_dibujos):
        return 'Dibujos'
    
    # Si tiene sección en la URL
    if '/f11-' in url or '/f14-' in url:
        # Por defecto anime para estas secciones, a menos que tenga indicadores de dibujos
        return 'Anime'
    
    if '/f17-' in url:
        return 'Serie Live-Action'
    
    # Por defecto
    return 'Anime'


def get_default_genre(tipo):
    """Obtener género por defecto según tipo"""
    genre_map = {
        'Anime': 'Animación Japonesa',
        'Dibujos': 'Animación Occidental',
        'Película': 'Animación Japonesa',
        'Serie Live-Action': 'Live-Action'
    }
    return genre_map.get(tipo, 'Animación Japonesa')


def extract_genre_from_post(content):
    """Extraer género del contenido del post (patrón: 📺 Género: X, Y, Z)"""
    if not content:
        return None, ''
    
    # Buscar patrón 📺 Género: seguido de géneros
    # El género termina cuando aparece otro campo (Año:, Idioma:, etc.) o salto de línea
    patrones = [
        # 📺 Género: Animación, Comedia Año:... (capturar hasta "Año:" o salto de línea)
        r'📺\s*G[eé]nero:\s*([^\nA-Z][^\n]*?)(?=\s*(?:📺|Año:|Idioma:|Tipo:|\n|$))',
        # Género: Animación, Comedia (sin emoji)
        r'G[eé]nero:\s*([^\nA-Z][^\n]*?)(?=\s*(?:📺|Año:|Idioma:|Tipo:|\n|$))',
    ]
    
    for patron in patrones:
        match = re.search(patron, content, re.IGNORECASE)
        if match:
            generos_texto = match.group(1).strip()
            # Limpiar - quitar palabras clave de otros campos si se colaron
            generos_texto = re.sub(r'\s+Año:.*$', '', generos_texto, flags=re.IGNORECASE)
            generos_texto = re.sub(r'\s+Idioma:.*$', '', generos_texto, flags=re.IGNORECASE)
            generos_texto = re.sub(r'\s+Tipo:.*$', '', generos_texto, flags=re.IGNORECASE)
            
            # Limpiar y separar géneros (por coma, slash, o ' y ')
            generos = [g.strip() for g in re.split(r'[,/]|\s+y\s+', generos_texto, flags=re.IGNORECASE) if g.strip()]
            
            # Filtrar géneros válidos (no deben contener palabras de otros campos)
            generos_validos = [g for g in generos if not any(x in g.lower() for x in ['año', 'idioma', 'tipo', 'episodios'])]
            
            if generos_validos:
                # Géneros genéricos a ignorar completamente
                generos_genericos = ['animación', 'animation', 'aventura']  # Aventura es muy genérico
                
                # Filtrar géneros genéricos de la lista completa
                generos_filtrados = [g for g in generos_validos 
                                     if not any(gg in g.lower() for gg in generos_genericos)]
                
                # Si después de filtrar no queda nada, usar la lista original
                if not generos_filtrados:
                    generos_filtrados = generos_validos
                
                # Ranking de géneros preferidos (de más específico a menos)
                generos_preferidos = [
                    'acción', 'comedia', 'drama', 'terror', 'misterio', 'suspense',
                    'romance', 'fantasía', 'sci-fi', 'ciencia ficción', 'deportes',
                    'musical', 'thriller', 'psicológico', 'sobrenatural', 'mecha',
                    'isekai', 'shonen', 'shoujo', 'seinen', 'kodomo'
                ]
                
                # Buscar el mejor género según el ranking
                genero_principal = None
                
                # 1. Primero buscar en los géneros filtrados según preferencia
                for preferido in generos_preferidos:
                    for g in generos_filtrados:
                        if preferido in g.lower():
                            genero_principal = g
                            break
                    if genero_principal:
                        break
                
                # 2. Si no se encontró en filtrados, buscar en todos los válidos
                if not genero_principal:
                    for preferido in generos_preferidos:
                        for g in generos_validos:
                            if preferido in g.lower():
                                genero_principal = g
                                break
                        if genero_principal:
                            break
                
                # 3. Si aún no hay, usar el primero no-genérico
                if not genero_principal:
                    for g in generos_filtrados:
                        if not any(gg in g.lower() for gg in generos_genericos):
                            genero_principal = g
                            break
                
                # 4. Si todo falla, usar el primero disponible
                if not genero_principal and generos_filtrados:
                    genero_principal = generos_filtrados[0]
                if not genero_principal:
                    genero_principal = generos_validos[0]
                
                # Los géneros específicos son los filtrados (sin genéricos)
                generos_especificos = ', '.join(generos_filtrados)
                return genero_principal, generos_especificos
    
    return None, ''


def extract_genres(content, title):
    """Extraer géneros específicos del contenido (método alternativo)"""
    generos_comunes = [
        'Acción', 'Aventura', 'Comedia', 'Drama', 'Fantasía',
        'Ciencia Ficción', 'Terror', 'Misterio', 'Romance',
        'Thriller', 'Mecha', 'Shounen', 'Shoujo', 'Seinen',
        'Josei', 'Slice of Life', 'Deportes', 'Música',
        'Superhéroes', 'Policial', 'Bélico', 'Histórico',
        'Sobrenatural', 'Psicológico', 'Escolar'
    ]
    
    text = (content + ' ' + title).lower()
    encontrados = []
    
    for genero in generos_comunes:
        if genero.lower() in text:
            encontrados.append(genero)
    
    return ', '.join(encontrados[:3]) if encontrados else ''


def extract_href(url):
    """Extraer href de URL"""
    try:
        from urllib.parse import urlparse
        return urlparse(url).path
    except:
        match = re.search(r'/t\d+-[^/]+', url)
        return match.group(0) if match else url


# Ruta a git en Windows (ajustar según instalación)
GIT_PATH = r'C:\Program Files\Git\bin\git.exe'

@app.route('/api/git/push', methods=['POST'])
def git_push():
    """Hacer commit y push de TOP.json a GitHub"""
    try:
        # Verificar que git existe
        if not os.path.exists(GIT_PATH):
            return jsonify({"error": f"Git no encontrado en: {GIT_PATH}"}), 500
        
        # Directorio del proyecto
        project_dir = os.path.dirname(__file__)
        
        # Verificar que es un repositorio git
        git_dir = os.path.join(project_dir, '.git')
        if not os.path.exists(git_dir):
            return jsonify({
                "error": "Este proyecto no es un repositorio Git",
                "details": f"No se encontró {git_dir}.\n\nPara solucionarlo, ejecuta en Git Bash:\n\ncd '{project_dir}'\ngit init\ngit remote add origin https://github.com/anidibucastellano-byte/anime-zone-esp.git\ngit add .\ngit commit -m 'Initial commit'\ngit push -u origin main",
                "isGitRepo": False
            }), 400
        
        # Configurar git para este repo (evita errores de identidad)
        # Usar datos proporcionados por el usuario
        user_email = "anidibucastellano@gmail.com"
        user_name = "anidibucastellano-byte"
        
        subprocess.run([GIT_PATH, 'config', 'user.email', user_email], 
                      cwd=project_dir, capture_output=True, check=False)
        subprocess.run([GIT_PATH, 'config', 'user.name', user_name], 
                      cwd=project_dir, capture_output=True, check=False)
        
        # Ruta absoluta al TOP.json
        top_json_abs = os.path.abspath(TOP_JSON_PATH)
        
        # Verificar que el archivo existe
        if not os.path.exists(top_json_abs):
            return jsonify({"error": f"TOP.json no encontrado en: {top_json_abs}"}), 500
        
        # Ejecutar comandos git - orden correcto:
        # 1. Añadir y commitear cambios locales primero
        # 2. Pull para sincronizar
        # 3. Push para subir
        commands = [
            # Añadir todos los cambios (TOP.json y otros archivos)
            [GIT_PATH, 'add', '.'],
            # Hacer commit de cambios locales (puede fallar si no hay cambios, eso es ok)
            [GIT_PATH, 'commit', '-m', f'Actualizar catálogo - {datetime.now().strftime("%Y-%m-%d %H:%M")}'],
            # Descargar cambios del remoto y aplicar encima
            [GIT_PATH, 'pull', 'origin', 'main', '--rebase'],
            # Hacer push
            [GIT_PATH, 'push', 'origin', 'main']
        ]
        
        results = []
        for cmd in commands:
            result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True, shell=False)
            results.append({
                'command': ' '.join(cmd),
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            })
            
            # Debug: imprimir en consola del servidor
            print(f"[GIT] Command: {' '.join(cmd)}")
            print(f"[GIT] Return code: {result.returncode}")
            print(f"[GIT] Stderr: {result.stderr}")
            
            # Si hay error, reportarlo (con excepciones conocidas)
            if result.returncode != 0:
                stderr_lower = result.stderr.lower()
                # Ignorar error de commit si no hay cambios para commitear
                if cmd[2] == 'commit' and ('nothing to commit' in stderr_lower or 'nothing added to commit' in stderr_lower or 'no changes added to commit' in stderr_lower):
                    continue
                # Ignorar error si no hay cambios staged para commit
                if cmd[2] == 'commit' and 'nothing staged' in stderr_lower:
                    continue
                return jsonify({
                    "error": f"Error en comando: {' '.join(cmd)}",
                    "details": result.stderr,
                    "stdout": result.stdout,
                    "results": results
                }), 500
        
        return jsonify({
            "success": True,
            "message": "Cambios subidos a GitHub correctamente",
            "results": results
        })
        
    except Exception as e:
        return jsonify({"error": f"Error ejecutando git: {str(e)}"}), 500


if __name__ == '__main__':
    print("🎬 Panel de Control - Anime Zone ESP")
    print(f"📁 TOP.json: {TOP_JSON_PATH}")
    print(f"💾 Backups: {BACKUP_DIR}")
    print("\n🌐 Abre en tu navegador: http://localhost:5000")
    print("\n⚠️  Presiona Ctrl+C para detener el servidor\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
