import json
import requests
from datetime import datetime
import os
import shutil
import logging
from logging.handlers import RotatingFileHandler

def configurar_logging():
    """Configurar sistema de logging profesional"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'anime_zone.log', 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def crear_backup():
    """Crear backup del TOP.json antes de modificar"""
    if not os.path.exists('TOP.json'):
        print("⚠️ TOP.json no existe, no se puede crear backup")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"TOP_backup_{timestamp}.json"
    
    try:
        shutil.copy2('TOP.json', backup_file)
        print(f"✅ Backup creado: {backup_file}")
        
        # Mantener solo los últimos 5 backups
        backups = [f for f in os.listdir('.') if f.startswith('TOP_backup_') and f.endswith('.json')]
        backups.sort()
        
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(old_backup)
                print(f"🗑️ Backup antiguo eliminado: {old_backup}")
        
        return True
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        return False

def validar_integridad_datos(data):
    """Validar que los datos sean consistentes"""
    errores = []
    warnings = []
    
    # Verificar estructura de cada item
    for tipo in ['anime', 'dibujos', 'peliculas', 'series']:
        items = data.get(tipo, [])
        for i, item in enumerate(items):
            if not item.get('name'):
                errores.append(f"{tipo}[{i}]: Falta nombre")
            if not item.get('url'):
                errores.append(f"{tipo}[{i}]: Falta URL")
            if not item.get('specificGenre'):
                warnings.append(f"{tipo}[{i}]: Falta género específico")
            if not item.get('tipo'):
                warnings.append(f"{tipo}[{i}]: Falta tipo")
    
    return errores, warnings

def generar_html_foroactivo():
    """Generar código HTML premium con filtros interactivos"""
    
    # Configurar logging
    logger = configurar_logging()
    tiempo_inicio = datetime.now()
    
    print(f"🔄 Iniciando generación HTML - {tiempo_inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    logger.info("Iniciando generación de HTML")
    
    # Crear backup antes de procesar
    print(f"💾 Creando backup automático...")
    backup_ok = crear_backup()
    logger.info(f"Backup creado: {backup_ok}")
    
    # Usar siempre el archivo local TOP.json
    print(f"📥 Cargando TOP.json local...")
    
    try:
        with open('TOP.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ TOP.json cargado correctamente")
        logger.info("TOP.json cargado exitosamente")
    except Exception as e:
        print(f"❌ Error al cargar TOP.json local: {e}")
        logger.error(f"Error cargando TOP.json: {e}")
        return
    
    # Validar integridad de los datos
    print(f"🔍 Validando integridad de datos...")
    errores, warnings = validar_integridad_datos(data)
    
    if errores:
        print(f"❌ Se encontraron {len(errores)} errores críticos:")
        for error in errores[:5]:  # Mostrar solo primeros 5
            print(f"   • {error}")
        if len(errores) > 5:
            print(f"   ... y {len(errores) - 5} errores más")
        return  # No continuar si hay errores críticos
    
    if warnings:
        print(f"⚠️ Se encontraron {len(warnings)} advertencias:")
        for warning in warnings[:3]:  # Mostrar solo primeras 3
            print(f"   • {warning}")
        if len(warnings) > 3:
            print(f"   ... y {len(warnings) - 3} advertencias más")
    
    print(f"✅ Validación completada sin errores críticos")
    
    # Validar que el JSON tenga la estructura correcta
    required_keys = ['anime', 'dibujos', 'peliculas', 'series', 'resumen']
    for key in required_keys:
        if key not in data:
            print(f"❌ Falta la clave '{key}' en TOP.json")
            data[key] = [] if key != 'resumen' else {}
    
    # Cargar datos con manejo robusto de errores
    try:
        animes = data.get('anime', [])
        print(f"✅ {len(animes)} animes cargados")
    except Exception as e:
        print(f"❌ Error cargando animes: {e}")
        animes = []
    
    try:
        dibujos = data.get('dibujos', [])
        print(f"✅ {len(dibujos)} dibujos cargados")
    except Exception as e:
        print(f"❌ Error cargando dibujos: {e}")
        dibujos = []
    
    try:
        peliculas = data.get('peliculas', [])
        print(f"✅ {len(peliculas)} películas cargadas")
    except Exception as e:
        print(f"❌ Error cargando películas: {e}")
        peliculas = []
    
    try:
        series = data.get('series', [])
        if not series:
            print("⚠️ Advertencia: No se encontraron series en TOP.json")
        else:
            print(f"✅ {len(series)} series cargadas")
    except Exception as e:
        print(f"❌ Error cargando series: {e}")
        series = []
    
    try:
        resumen = data.get('resumen', {})
        print(f"✅ Resumen cargado")
    except Exception as e:
        print(f"❌ Error cargando resumen: {e}")
        resumen = {}
    
    # Obtener todos los géneros únicos para el filtro
    todos_generos = set()
    for item in animes + dibujos + peliculas + series:
        genero = item.get('specificGenre', item.get('genre', 'N/A'))
        if genero and genero != 'N/A':
            todos_generos.add(genero)
    
    generos_ordenados = sorted(todos_generos)
    
    # Logging detallado del contenido
    print(f"\n📊 Resumen del contenido:")
    print(f"   Anime: {len(animes)}")
    print(f"   Dibujos: {len(dibujos)}")
    print(f"   Películas: {len(peliculas)}")
    print(f"   Series: {len(series)}")
    print(f"   Géneros únicos: {len(generos_ordenados)}")
    
    # Combinar todos los items con tipo
    todos_items = []
    for item in animes:
        item['tipo'] = 'anime'
        todos_items.append(item)
    for item in dibujos:
        item['tipo'] = 'dibujos'
        todos_items.append(item)
    for item in peliculas:
        item['tipo'] = 'peliculas'
        todos_items.append(item)
    for item in series:
        item['tipo'] = 'series'
        todos_items.append(item)
    
    print(f"   Total items: {len(todos_items)}")
    
    # Validar y corregir géneros
    items_sin_genero = 0
    for item in todos_items:
        if not item.get('specificGenre') or item['specificGenre'] == 'N/A':
            item['specificGenre'] = item.get('genre', 'Sin género')
            items_sin_genero += 1
    
    if items_sin_genero > 0:
        print(f"⚠️ Se corrigieron {items_sin_genero} items sin género específico")
    
    # Función para limpiar nombres en Python
    def limpiar_nombre(nombre):
        if not nombre:
            return ''
        import re
        # Quitar todo entre corchetes
        nombre = re.sub(r'\[.*?\]', '', nombre)
        # Quitar todo entre paréntesis (excepto años)
        nombre = re.sub(r'\((?!\d{4}).*?\)', '', nombre)
        # Quitar formatos técnicos
        nombre = re.sub(r'\d+/\d+', '', nombre)  # Episodios 45/45
        nombre = re.sub(r'\d+x\d+', '', nombre)  # Resoluciones 1440x1080
        nombre = re.sub(r'\d+MB', '', nombre, flags=re.IGNORECASE)  # Tamaños 425MB
        # Quitar múltiples espacios
        nombre = re.sub(r'\s+', ' ', nombre)
        return nombre.strip()
    
    # Limpiar todos los nombres antes de pasar a JavaScript
    for item in todos_items:
        item['nombre_limpio'] = limpiar_nombre(item.get('name', ''))
    
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anime Zone ESP - TOP Premium</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary-red: #c0392b;
            --dark-red: #922b21;
            --light-red: #fadbd8;
            --bg-dark: #0d0d0d;
            --bg-card: #1a1a1a;
            --bg-elevated: #252525;
            --text-primary: #ffffff;
            --text-secondary: #b3b3b3;
            --accent-gold: #f39c12;
            --border-red: #c0392b;
            --shadow: 0 8px 32px rgba(192, 57, 43, 0.3);
            --shadow-hover: 0 16px 48px rgba(192, 57, 43, 0.4);
        }}
        
        /* Animaciones y transiciones suaves */
        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        
        @keyframes shimmer {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.7; transform: scale(1.05); }}
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 50%, #0d0d0d 100%);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
            background: var(--bg-dark);
            border: 2px solid var(--primary-red);
            border-radius: 15px;
            box-shadow: var(--shadow);
        }}
        
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(180deg, rgba(192, 57, 43, 0.2) 0%, transparent 100%);
            border-bottom: 3px solid var(--primary-red);
            margin-bottom: 30px;
            position: relative;
        }}
        
        .header h1 {{
            font-family: 'Orbitron', sans-serif;
            font-size: 3.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, 
                #c0392b 0%, 
                #e74c3c 25%, 
                #f39c12 50%, 
                #e74c3c 75%, 
                #c0392b 100%);
            background-size: 200% 200%;
            animation: gradientShift 4s ease infinite;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-transform: uppercase;
            letter-spacing: 6px;
            margin-bottom: 10px;
            transition: all 0.3s ease;
        }}
        
        .header h1:hover {{
            transform: scale(1.05);
            filter: brightness(1.2);
        }}
        
        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: var(--bg-card);
            border: 2px solid var(--primary-red);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: var(--shadow);
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-hover);
        }}
        
        .stat-card .number {{
            font-family: 'Orbitron', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-red);
        }}
        
        .filters-section {{
            background: var(--bg-card);
            border: 2px solid var(--primary-red);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        
        .filters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .filter-select {{
            background: var(--bg-elevated);
            border: 2px solid #333;
            border-radius: 10px;
            padding: 12px 15px;
            color: var(--text-primary);
            font-size: 1rem;
            cursor: pointer;
            width: 100%;
        }}
        
        .tabs-container {{
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .tab-btn {{
            background: var(--bg-card);
            border: 2px solid #333;
            border-radius: 10px;
            padding: 15px 30px;
            color: var(--text-secondary);
            font-family: 'Orbitron', sans-serif;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .tab-btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(243, 156, 18, 0.3), 
                transparent);
            transition: left 0.5s ease;
        }}
        
        .tab-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(243, 156, 18, 0.3);
            border-color: var(--accent-gold);
            color: var(--text-primary);
        }}
        
        .tab-btn:hover::before {{
            left: 100%;
        }}
        
        .tab-btn.active {{
            background: var(--primary-red);
            border-color: var(--primary-red);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(192, 57, 43, 0.4);
        }}
        
        .sort-btn {{
            background: var(--bg-elevated);
            border: 2px solid #333;
            border-radius: 8px;
            padding: 10px 20px;
            color: var(--text-secondary);
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .sort-btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(192, 57, 43, 0.2), 
                transparent);
            transition: left 0.4s ease;
        }}
        
        .sort-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(192, 57, 43, 0.3);
            border-color: var(--primary-red);
            color: var(--text-primary);
        }}
        
        .sort-btn:hover::before {{
            left: 100%;
        }}
        
        .filter-select {{
            background: var(--bg-elevated);
            border: 2px solid #333;
            border-radius: 8px;
            padding: 12px 15px;
            color: var(--text-secondary);
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .filter-select:hover {{
            border-color: var(--primary-red);
            box-shadow: 0 4px 15px rgba(192, 57, 43, 0.2);
        }}
        
        .filter-select:focus {{
            outline: none;
            border-color: var(--accent-gold);
            box-shadow: 0 0 0 3px rgba(243, 156, 18, 0.3);
        }}
        
        .sort-btn.active {{
            background: var(--primary-red);
            border-color: var(--primary-red);
            color: white;
        }}
        
        .search-input {{
            background: var(--bg-elevated);
            border: 2px solid #333;
            border-radius: 25px;
            padding: 12px 20px;
            color: var(--text-primary);
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
            width: 100%;
            max-width: 500px;
        }}
        
        .search-input:hover {{
            border-color: var(--primary-red);
        }}
        
        .search-input:focus {{
            border-color: var(--primary-red);
            box-shadow: 0 0 15px rgba(192, 57, 43, 0.3);
        }}
        
        .content-section {{
            display: none;
        }}
        
        .content-section.active {{
            display: block;
        }}
        
        .items-grid {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .item-card {{
            background: var(--bg-card);
            border: 2px solid #333;
            border-radius: 10px;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateY(0);
            position: relative;
            display: flex;
            align-items: center;
            padding: 15px 20px;
        }}
        
        .item-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(243, 156, 18, 0.1), 
                transparent);
            transition: left 0.6s ease;
            z-index: 1;
        }}
        
        .item-card:hover {{
            transform: translateY(-8px) scale(1.02);
            border-color: var(--primary-red);
            box-shadow: 0 20px 40px rgba(192, 57, 43, 0.4);
            background: linear-gradient(135deg, 
                var(--bg-card) 0%, 
                rgba(192, 57, 43, 0.05) 100%);
        }}
        
        .item-card:hover::before {{
            left: 100%;
        }}
        
        .item-card:hover .item-number {{
            color: var(--accent-gold);
            transform: scale(1.1);
        }}
        
        .item-card:hover .item-title {{
            color: var(--text-primary);
        }}
        
        .item-header {{
            display: flex;
            align-items: center;
            flex: 1;
        }}
        
        .item-title {{
            font-size: 1rem;
            font-weight: 600;
        }}
        
        .item-number {{
            font-family: 'Orbitron', sans-serif;
            font-size: 1.5rem;
            font-weight: 900;
            color: var(--primary-red);
            min-width: 50px;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .item-body {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .item-meta {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        .meta-badge {{
            background: linear-gradient(135deg, var(--primary-red), var(--dark-red));
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 2px 8px rgba(192, 57, 43, 0.3);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        
        .meta-badge::after {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255, 255, 255, 0.2), 
                transparent);
            animation: shimmer 2s infinite;
        }}
        
        .meta-badge:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(192, 57, 43, 0.4);
        }}
        
        .genre-badge {{
            background: linear-gradient(135deg, var(--accent-gold), #e67e22);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .item-link {{
            background: linear-gradient(135deg, var(--primary-red), #e74c3c);
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            color: white;
            text-decoration: none;
            font-family: 'Orbitron', sans-serif;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .item-link::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255, 255, 255, 0.3), 
                transparent);
            transition: left 0.4s ease;
        }}
        
        .item-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(192, 57, 43, 0.5);
            background: linear-gradient(135deg, #e74c3c, var(--primary-red));
        }}
        
        .item-link:hover::before {{
            left: 100%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ANIMEZONEESP</h1>
        </div>
        
        <div class="stats-bar">
            <div class="stat-card">
                <div class="number">{len(animes)}</div>
                <div class="label">Anime</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(dibujos)}</div>
                <div class="label">Dibujos</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(peliculas)}</div>
                <div class="label">Peliculas</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(series)}</div>
                <div class="label">Series</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(animes) + len(dibujos) + len(peliculas) + len(series)}</div>
                <div class="label">Total</div>
            </div>
        </div>
        
        <div class="filters-section">
            <div class="filters-grid">
                <div>
                    <label style="color: var(--text-secondary); margin-bottom: 8px; display: block;">Década</label>
                    <select id="decadaFilter" class="filter-select" onchange="applyFilters()">
                        <option value="all">Todas las décadas</option>
                        <option value="2020">2020s (2020-2029)</option>
                        <option value="2010">2010s (2010-2019)</option>
                        <option value="2000">2000s (2000-2009)</option>
                        <option value="1990">1990s (1990-1999)</option>
                        <option value="1980">1980s (1980-1989)</option>
                        <option value="1970">1970s (1970-1979)</option>
                        <option value="1960">1960s (1960-1969)</option>
                        <option value="1950">1950s (1950-1959)</option>
                        <option value="1940">1940s (1940-1949)</option>
                        <option value="older">Anteriores a 1940</option>
                    </select>
                </div>
                <div>
                    <label style="color: var(--text-secondary); margin-bottom: 8px; display: block;">Género</label>
                    <select id="generoFilter" class="filter-select" onchange="applyFilters()">
                        <option value="all">Todos los géneros</option>
                        {''.join(f'<option value="{g}">{g}</option>' for g in generos_ordenados)}
                    </select>
                </div>
            </div>
        </div>
        
        <div class="tabs-container">
            <button class="tab-btn active" onclick="showTab('all')">TODO</button>
            <button class="tab-btn" onclick="showTab('series')">SERIES</button>
            <button class="tab-btn" onclick="showTab('anime')">ANIME</button>
            <button class="tab-btn" onclick="showTab('dibujos')">DIBUJOS</button>
            <button class="tab-btn" onclick="showTab('peliculas')">PELICULAS</button>
        </div>
        
        <div class="search-container" style="display: flex; justify-content: center; margin-bottom: 20px;">
            <input type="text" id="searchInput" class="search-input" placeholder="🔍 Buscar serie, película o género..." onkeyup="applyFilters()">
        </div>
        
        <div class="sort-container" style="display: flex; justify-content: center; gap: 10px; margin-bottom: 20px;">
            <button class="sort-btn" onclick="sortItems('name')">Ordenar por Nombre</button>
            <button class="sort-btn" onclick="sortItems('year')">Ordenar por Año</button>
        </div>
        
        <div id="content-all" class="content-section active">
            <div class="items-grid" id="grid-all"></div>
        </div>
        <div id="content-series" class="content-section">
            <div class="items-grid" id="grid-series"></div>
        </div>
        <div id="content-anime" class="content-section">
            <div class="items-grid" id="grid-anime"></div>
        </div>
        <div id="content-dibujos" class="content-section">
            <div class="items-grid" id="grid-dibujos"></div>
        </div>
        <div id="content-peliculas" class="content-section">
            <div class="items-grid" id="grid-peliculas"></div>
        </div>
        
        <div style="text-align: center; padding: 30px; margin-top: 40px; border-top: 2px solid var(--primary-red); color: var(--text-secondary);">
            <p>Última actualización: <span style="color: var(--primary-red); font-weight: 600;">{datetime.now().strftime('%d/%m/%Y %H:%M')}</span></p>
        </div>
    </div>
    
    <script>
        const allItems = {json.dumps(todos_items, ensure_ascii=False)};
        let currentTab = 'all';
        let currentSort = 'name';
        let sortDirection = 'asc';
        
        function showTab(tab) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
            document.getElementById('content-' + tab).classList.add('active');
            currentTab = tab;
            applyFilters();
        }}
        
        function sortItems(sortBy) {{
            if (currentSort === sortBy) {{
                sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
            }} else {{
                currentSort = sortBy;
                sortDirection = 'asc';
            }}
            
            allItems.sort((a, b) => {{
                let valA, valB;
                if (sortBy === 'name') {{
                    valA = (a.name || '').toLowerCase().replace('[activo]', '').trim();
                    valB = (b.name || '').toLowerCase().replace('[activo]', '').trim();
                }} else if (sortBy === 'year') {{
                    valA = parseInt(a.year) || 0;
                    valB = parseInt(b.year) || 0;
                }}
                
                if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
                if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
                return 0;
            }});
            
            applyFilters();
        }}
        
        function getDecade(year) {{
            if (!year || year === 'N/A') return null;
            const y = parseInt(year);
            if (y >= 2020) return '2020';
            if (y >= 2010) return '2010';
            if (y >= 2000) return '2000';
            if (y >= 1990) return '1990';
            if (y >= 1980) return '1980';
            if (y >= 1970) return '1970';
            if (y >= 1960) return '1960';
            if (y >= 1950) return '1950';
            if (y >= 1940) return '1940';
            return 'older';
        }}
        
        function applyFilters() {{
            const decada = document.getElementById('decadaFilter').value;
            const genero = document.getElementById('generoFilter').value;
            const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
            
            let filtered = allItems.filter(item => {{
                if (currentTab !== 'all' && item.tipo !== currentTab) return false;
                if (decada !== 'all' && getDecade(item.year) !== decada) return false;
                if (genero !== 'all' && (item.specificGenre || item.genre || 'N/A') !== genero) return false;
                
                // Búsqueda por texto
                if (searchTerm) {{
                    const nombre = (item.nombre_limpio || item.name || '').toLowerCase();
                    const itemGenero = (item.specificGenre || item.genre || '').toLowerCase();
                    const year = String(item.year || '').toLowerCase();
                    
                    if (!nombre.includes(searchTerm) && !itemGenero.includes(searchTerm) && !year.includes(searchTerm)) {{
                        return false;
                    }}
                }}
                
                return true;
            }});
            
            const gridId = currentTab === 'all' ? 'grid-all' : 'grid-' + currentTab;
            const grid = document.getElementById(gridId);
            
            if (filtered.length === 0) {{
                grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 60px; color: var(--text-secondary);"><div style="font-size: 4rem; margin-bottom: 20px;">�</div><p>No se encontraron resultados</p></div>';
                return;
            }}
            
            grid.innerHTML = filtered.map((item, index) => {{
                const nombre = item.nombre_limpio || item.name || '';
                const year = item.year || 'N/A';
                const genero = item.specificGenre || item.genre || 'N/A';
                const url = item.url || '#';
                
                return `<div class="item-card"><div class="item-number">#${{index + 1}}</div><div class="item-header"><div class="item-title">${{nombre}}</div></div><div class="item-body"><div class="item-meta"><span class="meta-badge">📅 ${{year}}</span><span class="meta-badge genre-badge">${{genero}}</span></div><a href="${{url}}" target="_blank" class="item-link">Ver</a></div></div>`;
            }}).join('');
        }}
        
        applyFilters();
    </script>
</body>
</html>'''
    
    with open('top_foroactivo.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Resumen final del proceso
    tiempo_final = datetime.now()
    duracion = tiempo_final - tiempo_inicio
    
    print(f"\n🎉 ¡Proceso completado exitosamente!")
    print(f"📊 Resumen final:")
    print(f"   • Total items procesados: {len(todos_items)}")
    print(f"   • Anime: {len(animes)}")
    print(f"   • Dibujos: {len(dibujos)}")
    print(f"   • Películas: {len(peliculas)}")
    print(f"   • Series: {len(series)}")
    print(f"   • Géneros únicos: {len(generos_ordenados)}")
    print(f"   • Backup creado: {'Sí' if backup_ok else 'No'}")
    print(f"   • Archivo generado: top_foroactivo.html")
    print(f"   • Duración: {str(duracion).split('.')[0]}")
    
    # Logging del resumen
    logger.info(f"HTML generado exitosamente - Total: {len(todos_items)} items")
    logger.info(f"Distribución - Anime: {len(animes)}, Dibujos: {len(dibujos)}, Películas: {len(peliculas)}, Series: {len(series)}")
    
    print(f"\n✅ HTML Premium generado con filtros interactivos")
    print(f"📁 Archivo guardado como: top_foroactivo.html")
    
    return {
        'total_items': len(todos_items),
        'animes': len(animes),
        'dibujos': len(dibujos),
        'peliculas': len(peliculas),
        'series': len(series),
        'generos': len(generos_ordenados),
        'backup_ok': backup_ok,
        'html_file': 'top_foroactivo.html'
    }

# Ejecutar la función
if __name__ == "__main__":
    generar_html_foroactivo()
