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
    
    # Validar y corregir géneros - genre (actualizado manualmente) tiene prioridad sobre specificGenre
    items_actualizados = 0
    for item in todos_items:
        if item.get('genre'):
            # Si existe genre (actualizado manualmente), usarlo como specificGenre
            item['specificGenre'] = item['genre']
            items_actualizados += 1
        elif not item.get('specificGenre') or item['specificGenre'] == 'N/A':
            item['specificGenre'] = 'Sin género'
            items_actualizados += 1
    
    if items_actualizados > 0:
        print(f"✅ Se actualizaron {items_actualizados} items con géneros correctos")
    
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
    <title>AnimeZoneEsp - Catalogo</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{
            margin: 0;
            padding: 0;
            width: 100%;
            max-width: 100%;
            overflow-x: hidden;
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
            background: 
                radial-gradient(ellipse at 20% 30%, rgba(192, 57, 43, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 70%, rgba(231, 76, 60, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(243, 156, 18, 0.08) 0%, transparent 60%),
                linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 50%, #0d0d0d 100%);
            background-attachment: fixed;
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
            margin: 0;
            padding: 0;
        }}
        
        .container {{
            max-width: 100%;
            width: 100%;
            margin: 0;
            padding: 20px;
            background: transparent;
            border: none;
            border-radius: 0;
        }}
        
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 30px;
            background: linear-gradient(180deg, rgba(192, 57, 43, 0.2) 0%, transparent 100%);
            border-bottom: 3px solid var(--primary-red);
            margin-bottom: 30px;
            position: relative;
            flex-wrap: wrap;
            gap: 15px;
        }}
        
        .header-left {{
            display: flex;
            align-items: center;
            gap: 15px;
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
            display: flex !important;
            justify-content: flex-end !important;
            gap: 8px !important;
            margin-bottom: 0 !important;
            flex-wrap: wrap !important;
        }}
        
        .stat-card {{
            background: var(--bg-card) !important;
            border: 1px solid var(--primary-red) !important;
            border-radius: 6px !important;
            padding: 8px 12px !important;
            text-align: center !important;
            transition: all 0.3s ease;
            box-shadow: var(--shadow) !important;
            min-width: 70px !important;
            max-width: 70px !important;
            width: 70px !important;
            flex: none !important;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px) !important;
            box-shadow: var(--shadow-hover) !important;
        }}
        
        .stat-card .number {{
            font-family: 'Orbitron', sans-serif !important;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            color: var(--primary-red) !important;
            line-height: 1.2 !important;
        }}
        
        .stat-card .label {{
            font-size: 0.6rem !important;
            color: var(--text-secondary) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            margin-top: 2px !important;
        }}
        
        .filters-section {{
            background: var(--bg-card);
            border: 1px solid var(--primary-red);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 20px;
        }}
        
        .filters-grid {{
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        
        .filter-select {{
            background: var(--bg-elevated) !important;
            border: 1px solid #333 !important;
            border-radius: 4px !important;
            padding: 4px 8px !important;
            color: var(--text-primary) !important;
            font-size: 0.75rem !important;
            cursor: pointer;
            width: 140px !important;
            height: 28px !important;
        }}
        
        /* Sidebar Menu Styles */
        .main-layout {{
            display: flex;
            gap: 20px;
            min-height: calc(100vh - 200px);
        }}
        
        .sidebar {{
            width: 200px;
            flex-shrink: 0;
            background: var(--bg-card);
            border: 1px solid var(--primary-red);
            border-radius: 8px;
            padding: 15px;
            height: fit-content;
            position: sticky;
            top: 20px;
        }}
        
        .sidebar-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--primary-red);
            margin-bottom: 15px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid var(--primary-red);
            padding-bottom: 10px;
        }}
        
        .sidebar-menu {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .sidebar-menu li {{
            margin-bottom: 5px;
        }}
        
        .sidebar-menu button {{
            width: 100%;
            background: transparent;
            border: 1px solid #333;
            border-radius: 6px;
            padding: 10px 15px;
            color: var(--text-secondary);
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: left;
            text-transform: uppercase;
        }}
        
        .sidebar-menu button:hover {{
            background: rgba(192, 57, 43, 0.1);
            border-color: var(--primary-red);
            color: var(--text-primary);
            transform: translateX(3px);
        }}
        
        .sidebar-menu button.active {{
            background: var(--primary-red);
            border-color: var(--primary-red);
            color: white;
            box-shadow: 0 4px 15px rgba(192, 57, 43, 0.3);
        }}
        
        .sidebar-filters {{
            padding: 0 5px;
        }}
        
        .sidebar-filters label {{
            display: block;
            margin-bottom: 4px;
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
        }}
        
        .sidebar-filters .filter-select {{
            width: 100% !important;
            margin-bottom: 10px;
            background: var(--bg-elevated);
            border: 1px solid #333;
            border-radius: 4px;
            padding: 4px 8px;
            color: var(--text-primary);
            font-size: 0.75rem;
            cursor: pointer;
        }}
        
        .main-content {{
            flex: 1;
            min-width: 0;
        }}
        
        @media (max-width: 768px) {{
            .main-layout {{
                flex-direction: column;
            }}
            .sidebar {{
                width: 100%;
                position: relative;
                top: 0;
            }}
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
        
        .search-suggestions {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: rgba(30, 30, 35, 0.98);
            border: 1px solid rgba(231, 76, 60, 0.3);
            border-radius: 8px;
            margin-top: 5px;
            max-height: 300px;
            overflow-y: auto;
            z-index: 99999;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
        }}
        
        .suggestion-item {{
            display: flex;
            align-items: center;
            padding: 10px 15px;
            cursor: pointer;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.2s ease;
        }}
        
        .suggestion-item:hover,
        .suggestion-item.active {{
            background: rgba(231, 76, 60, 0.3);
        }}
        
        .suggestion-img {{
            width: 40px;
            height: 60px;
            object-fit: cover;
            border-radius: 4px;
            margin-right: 12px;
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .suggestion-title {{
            font-weight: 600;
            color: var(--text-primary);
            font-size: 0.95rem;
        }}
        
        .suggestion-meta {{
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}
        
        .content-section {{
            display: none;
        }}
        
        .content-section.active {{
            display: block;
        }}
        
        .items-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            padding: 20px 0;
        }}
        
        @media (max-width: 768px) {{
            .items-grid {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 15px;
            }}
        }}
        
        /* Carruseles por género estilo Netflix */
        
        /* Carrusel destacado de últimas añadidas */
        .latest-section {{
            margin-bottom: 30px;
            position: relative;
            background: linear-gradient(180deg, rgba(192, 57, 43, 0.15) 0%, rgba(231, 76, 60, 0.08) 50%, transparent 100%);
            border-radius: 12px;
            padding: 25px 20px;
            border: 1px solid rgba(192, 57, 43, 0.3);
        }}
        
        .latest-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 1.4rem;
            font-weight: 900;
            color: var(--primary-red);
            margin: 0 0 20px 0;
            text-transform: uppercase;
            letter-spacing: 3px;
            text-align: center;
            text-shadow: 0 0 20px rgba(192, 57, 43, 0.5);
        }}
        
        
        .genre-section {{
            margin-bottom: 15px;
            position: relative;
        }}
        
        .genre-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            color: var(--text-primary);
            margin: 0 0 15px 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
            border-left: 4px solid var(--primary-red);
            padding-left: 15px;
            display: inline-block;
        }}
        
        .genre-title:hover {{
            color: var(--primary-red);
            transform: translateX(5px);
        }}
        
        /* Modal para ver todos los items de un género */
        .genre-modal-content {{
            max-width: 1400px;
            margin: 0 auto;
            background: var(--bg-card);
            border-radius: 12px;
            border: 2px solid var(--primary-red);
            overflow: hidden;
        }}
        
        .genre-modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 30px;
            background: linear-gradient(90deg, var(--primary-red), transparent);
            border-bottom: 2px solid var(--primary-red);
        }}
        
        .genre-modal-header h2 {{
            margin: 0;
            font-family: 'Orbitron', sans-serif;
            font-size: 1.5rem;
            color: white;
        }}
        
        .genre-modal-header .close-btn {{
            background: rgba(0,0,0,0.5);
            border: 2px solid white;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.2rem;
            transition: all 0.3s ease;
        }}
        
        .genre-modal-header .close-btn:hover {{
            background: var(--primary-red);
            transform: scale(1.1);
        }}
        
        .genre-modal-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            max-height: calc(100vh - 150px);
            overflow-y: auto;
        }}
        
        .carousel-container {{
            position: relative;
            display: block;
            padding: 0 20px;
            z-index: 1;
            width: 100%;
            max-width: 100%;
            margin: 0 auto;
        }}
        
        .carousel-scroll-area {{
            position: relative;
            overflow: hidden;
            padding: 10px 0;
            width: 100%;
            height: 260px;
            box-sizing: border-box;
        }}
        
        .carousel-scroll-area::-webkit-scrollbar {{
            display: none;
        }}
        
        .carousel-track {{
            display: flex;
            flex-direction: row;
            flex-wrap: nowrap;
            gap: 15px;
            padding: 0;
            width: max-content;
            position: relative;
            left: 0;
            transition: left 0.3s ease;
        }}
        
        .carousel-btn {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            width: 40px;
            height: 60px;
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid rgba(255, 255, 255, 0.3);
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            z-index: 100;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            pointer-events: auto;
            user-select: none;
            -webkit-user-select: none;
            touch-action: manipulation;
        }}
        
        .carousel-btn:hover,
        .carousel-btn:active {{
            background: rgba(192, 57, 43, 0.9);
            transform: translateY(-50%) scale(1.1);
            border-color: rgba(255, 255, 255, 0.8);
        }}
        
        .carousel-btn.carousel-prev {{
            left: 5px;
        }}
        
        .carousel-btn.carousel-next {{
            right: 5px;
        }}
        
        .carousel-btn.hidden {{
            display: none;
        }}
        
        /* Item card en carrusel */
        .carousel-track .item-card {{
            flex: 0 0 auto;
            width: 150px;
            aspect-ratio: 2/3;
        }}
        
        @media (max-width: 768px) {{
            .carousel-track .item-card {{
                width: 150px;
            }}
            
            .genre-title {{
                font-size: 0.9rem;
            }}
        }}
        
        .item-card {{
            background: var(--bg-card);
            border: 2px solid #333;
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            display: flex;
            flex-direction: column;
            cursor: pointer;
            aspect-ratio: 2/3;
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
            transform: translateY(-8px);
            border-color: var(--primary-red);
            box-shadow: 0 20px 40px rgba(192, 57, 43, 0.4);
            z-index: 10;
        }}
        
        .item-image {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: top;
            transition: transform 0.4s ease;
            position: absolute;
            top: 0;
            left: 0;
        }}
        
        .item-card:hover .item-image {{
            transform: scale(1.08);
        }}
        
        .item-image-placeholder {{
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            color: var(--primary-red);
        }}
        
        .item-content {{
            padding: 8px 10px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 60%, transparent 100%);
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 2;
        }}
        
        .item-title {{
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 5px;
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .item-meta {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .meta-badge {{
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        
        .item-link {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 5;
            text-decoration: none;
        }}
        
        .item-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(to bottom, 
                transparent 0%, 
                transparent 50%, 
                rgba(0,0,0,0.8) 100%);
            z-index: 1;
            opacity: 0.6;
            transition: opacity 0.3s ease;
        }}
        
        .item-card:hover .item-overlay {{
            opacity: 0.8;
        }}
        
        .item-card:hover::before {{
            left: 100%;
        }}
        
        .meta-badge:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(192, 57, 43, 0.4);
        }}
        
        .genre-badge {{
            background: linear-gradient(135deg, var(--accent-gold), #e67e22);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .item-link:hover {{
            background: rgba(192, 57, 43, 0.1);
        }}
        
        /* Modal estilo Netflix */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #000;
            z-index: 1000;
            justify-content: center;
            align-items: flex-start;
            padding: 0;
            margin: 0;
            box-sizing: border-box;
            overflow-y: auto;
        }}
        
        .modal-overlay.active {{
            display: flex;
        }}
        
        .modal-content {{
            background: transparent;
            border-radius: 0;
            max-width: 900px;
            width: 100%;
            min-height: 100vh;
            position: relative;
            overflow: hidden;
            margin: 0 auto;
        }}
        
        .modal-close {{
            position: absolute;
            top: 15px;
            right: 15px;
            width: 40px;
            height: 40px;
            background: rgba(0, 0, 0, 0.7);
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }}
        
        .modal-close:hover {{
            background: var(--primary-red);
            transform: scale(1.1);
        }}
        
        .modal-bg-image {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 70vh;
            min-height: 500px;
            object-fit: cover;
            object-position: center 20%;
            filter: blur(15px) brightness(0.4);
            z-index: 0;
        }}
        
        .modal-bg-gradient {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 70vh;
            min-height: 500px;
            background: linear-gradient(to bottom, 
                rgba(0,0,0,0.1) 0%, 
                rgba(0,0,0,0.3) 30%, 
                rgba(0,0,0,0.7) 60%, 
                #000 100%);
            z-index: 1;
        }}
        
        .modal-content-wrapper {{
            position: relative;
            z-index: 2;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: center;
            gap: 50px;
            padding: 40px;
            min-height: 100vh;
        }}
        
        .modal-poster {{
            width: 280px;
            height: 420px;
            object-fit: cover;
            border-radius: 12px;
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.9);
            flex-shrink: 0;
            z-index: 2;
            border: 3px solid rgba(255,255,255,0.15);
        }}
        
        .modal-info {{
            flex: 1;
            max-width: 600px;
            text-align: left;
            z-index: 2;
        }}
        
        
        .modal-title {{
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            line-height: 1.2;
        }}
        
        .modal-meta {{
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }}
        
        .modal-meta-badge {{
            background: var(--primary-red);
            color: white;
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 500;
        }}
        
        .modal-sinopsis {{
            font-size: 0.95rem;
            line-height: 1.6;
            color: var(--text-primary);
            margin: 20px 0;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: left;
            max-height: 300px;
            overflow-y: auto;
        }}
        
        .modal-sinopsis:empty {{
            display: none;
        }}
        
        .modal-sinopsis-label {{
            color: var(--primary-red);
            font-weight: 700;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
            display: block;
        }}
        
        /* Responsive para móviles */
        @media (max-width: 768px) {{
            .modal-content-wrapper {{
                flex-direction: column;
                align-items: center;
                padding: 40px 20px;
            }}
            
            .modal-poster {{
                width: 200px;
                height: 300px;
            }}
            
        }}
        
        .modal-info-extra {{
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }}
        
        .modal-info-extra h3 {{
            color: var(--primary-red);
            margin-bottom: 10px;
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .modal-info-extra p {{
            color: var(--text-secondary);
            line-height: 1.6;
            white-space: pre-line;
            font-size: 0.85rem;
        }}
        
        /* Ficha Técnica */
        .modal-ficha-tecnica {{
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }}
        
        .modal-ficha-tecnica h3 {{
            color: var(--primary-red);
            margin-bottom: 12px;
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .ficha-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 6px 15px;
        }}
        
        .ficha-item {{
            display: flex;
            align-items: baseline;
            gap: 4px;
            min-width: 0;
        }}
        
        .ficha-item.full-width {{
            grid-column: 1 / -1;
        }}
        
        .ficha-label {{
            color: var(--text-secondary);
            font-size: 0.75rem;
            font-weight: 500;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        
        .ficha-value {{
            color: var(--text-primary);
            font-size: 0.8rem;
            font-weight: 500;
            word-wrap: break-word;
            overflow-wrap: break-word;
            line-height: 1.3;
        }}
        
        .ficha-link {{
            color: var(--primary-red);
            text-decoration: underline;
            font-weight: 600;
            cursor: pointer;
        }}
        
        .ficha-link:hover {{
            color: var(--accent-gold);
        }}
        
        .modal-link {{
            display: inline-block;
            margin-top: 20px;
            background: var(--primary-red);
            color: white;
            padding: 12px 30px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .modal-link:hover {{
            background: #c0392b;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(192, 57, 43, 0.4);
        }}
        
        .modal-link-online {{
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            margin-left: 10px;
        }}
        
        .modal-link-online:hover {{
            background: linear-gradient(135deg, #229954, #27ae60);
        }}
        
        .modal-buttons {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        @media (max-width: 768px) {{
            .modal-image-container {{
                height: 250px;
            }}
            
            .modal-title {{
                font-size: 1.5rem;
            }}
            
            .modal-info {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <img src="https://i.servimg.com/u/f30/20/63/83/19/icono10.png" alt="Anime Zone ESP" class="header-logo" style="height: 50px; width: auto;">
                <h1 style="margin: 0;">ANIMEZONEESP</h1>
            </div>
            <div class="stats-bar">
                <div class="stat-card" style="padding: 8px 12px !important; width: 70px !important; min-width: 70px !important; max-width: 70px !important; border-radius: 6px !important;">
                    <div class="number" style="font-size: 0.85rem !important;">{len(animes)}</div>
                    <div class="label" style="font-size: 0.6rem !important;">Anime</div>
                </div>
                <div class="stat-card" style="padding: 8px 12px !important; width: 70px !important; min-width: 70px !important; max-width: 70px !important; border-radius: 6px !important;">
                    <div class="number" style="font-size: 0.85rem !important;">{len(dibujos)}</div>
                    <div class="label" style="font-size: 0.6rem !important;">Dibujos</div>
                </div>
                <div class="stat-card" style="padding: 8px 12px !important; width: 70px !important; min-width: 70px !important; max-width: 70px !important; border-radius: 6px !important;">
                    <div class="number" style="font-size: 0.85rem !important;">{len(peliculas)}</div>
                    <div class="label" style="font-size: 0.6rem !important;">Peliculas</div>
                </div>
                <div class="stat-card" style="padding: 8px 12px !important; width: 70px !important; min-width: 70px !important; max-width: 70px !important; border-radius: 6px !important;">
                    <div class="number" style="font-size: 0.85rem !important;">{len(series)}</div>
                    <div class="label" style="font-size: 0.6rem !important;">Series</div>
                </div>
                <div class="stat-card" style="padding: 8px 12px !important; width: 70px !important; min-width: 70px !important; max-width: 70px !important; border-radius: 6px !important;">
                    <div class="number" style="font-size: 0.85rem !important;">{len(animes) + len(dibujos) + len(peliculas) + len(series)}</div>
                    <div class="label" style="font-size: 0.6rem !important;">Total</div>
                </div>
            </div>
        </div>
        
        <!-- Carrusel destacado de últimas añadidas -->
        <div class="latest-section" id="latest-section">
            <h2 class="latest-title">Últimas Añadidas</h2>
            <div class="carousel-container">
                <button class="carousel-btn carousel-prev" data-scrollarea="scrollarea-latest" type="button">❮</button>
                <div class="carousel-scroll-area" id="scrollarea-latest">
                    <div class="carousel-track" id="carousel-latest">
                        <!-- Se llena dinámicamente con JS -->
                    </div>
                </div>
                <button class="carousel-btn carousel-next" data-scrollarea="scrollarea-latest" type="button">❯</button>
            </div>
        </div>
        
        <div class="main-layout">
            <aside class="sidebar">
                <div class="sidebar-title">Categorías</div>
                <ul class="sidebar-menu">
                    <li><button class="tab-btn active" onclick="showTab('all', this)">📁 TODO</button></li>
                    <li><button class="tab-btn" onclick="showTab('series', this)">📺 Series</button></li>
                    <li><button class="tab-btn" onclick="showTab('anime', this)">🎌 Anime</button></li>
                    <li><button class="tab-btn" onclick="showTab('dibujos', this)">🎨 Dibujos</button></li>
                    <li><button class="tab-btn" onclick="showTab('disney', this)">🏰 Disney</button></li>
                    <li><button class="tab-btn" onclick="showTab('peliculas', this)">🎬 Películas</button></li>
                </ul>
                
                <div class="sidebar-title" style="margin-top: 20px;">Filtros</div>
                <div class="sidebar-filters">
                    <label style="color: var(--text-secondary); margin-bottom: 4px; display: block; font-size: 0.65rem !important; text-transform: uppercase; letter-spacing: 0.5px;">Década</label>
                    <select id="decadaFilter" class="filter-select" onchange="applyFilters()" style="font-size: 0.75rem !important; height: 28px !important; padding: 4px 8px !important; width: 100% !important; margin-bottom: 10px;">
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
                    
                    <label style="color: var(--text-secondary); margin-bottom: 4px; display: block; font-size: 0.65rem !important; text-transform: uppercase; letter-spacing: 0.5px;">Género</label>
                    <select id="generoFilter" class="filter-select" onchange="applyFilters()" style="font-size: 0.75rem !important; height: 28px !important; padding: 4px 8px !important; width: 100% !important;">
                        <option value="all">Todos los géneros</option>
                        {''.join(f'<option value="{g}">{g}</option>' for g in generos_ordenados)}
                    </select>
                </div>
            </aside>
            
            <main class="main-content">
                <div class="search-container" style="display: flex; justify-content: center; margin-bottom: 20px; position: relative;">
                    <input type="text" id="searchInput" class="search-input" placeholder="🔍 Buscar serie, película o género..." onkeyup="handleSearchInput(event)" autocomplete="off">
                    <div id="searchSuggestions" class="search-suggestions" style="display: none;"></div>
                </div>
                
                <div class="sort-container" style="display: flex; justify-content: center; gap: 10px; margin-bottom: 20px;">
                    <button class="sort-btn" onclick="sortItems('name')">Ordenar por Nombre</button>
                    <button class="sort-btn" onclick="sortItems('year')">Ordenar por Año</button>
                </div>
                
                <div id="content-all" class="content-section active">
                    <div id="grid-all" class="genre-carousels"></div>
                </div>
                <div id="content-series" class="content-section">
                    <div id="grid-series" class="genre-carousels"></div>
                </div>
                <div id="content-anime" class="content-section">
                    <div id="grid-anime" class="genre-carousels"></div>
                </div>
                <div id="content-dibujos" class="content-section">
                    <div id="grid-dibujos" class="genre-carousels"></div>
                </div>
                <div id="content-disney" class="content-section">
                    <div id="grid-disney" class="genre-carousels"></div>
                </div>
                <div id="content-peliculas" class="content-section">
                    <div id="grid-peliculas" class="genre-carousels"></div>
                </div>
            </main>
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
        
        // Función para extraer ID de thread del href
        function getThreadId(item) {{
            const href = item.href || item.url || '';
            const match = href.match(/\/t(\d+)-/);
            return match ? parseInt(match[1]) : 0;
        }}
        
        // Función para llenar carrusel de últimas añadidas
        let latestCarouselInterval = null;
        
        function fillLatestCarousel() {{
            const latestTrack = document.getElementById('carousel-latest');
            const scrollArea = document.getElementById('scrollarea-latest');
            if (!latestTrack || !scrollArea) return;
            
            // Limpiar intervalo anterior si existe
            if (latestCarouselInterval) {{
                clearInterval(latestCarouselInterval);
            }}
            
            // Ordenar por ID de thread (descendente = más recientes primero)
            const sortedItems = [...allItems].sort((a, b) => getThreadId(b) - getThreadId(a));
            
            // Tomar los 15 items más recientes
            const latestItems = sortedItems.slice(0, 15);
            
            latestTrack.innerHTML = latestItems.map(item => generateItemHTML(item)).join('');
            
            // Asignar event listeners a los botones del carousel
            const prevBtn = document.querySelector('.latest-section .carousel-prev');
            const nextBtn = document.querySelector('.latest-section .carousel-next');
            
            if (prevBtn) {{
                prevBtn.addEventListener('click', function(e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    scrollCarouselArea('scrollarea-latest', -1);
                }});
            }}
            
            if (nextBtn) {{
                nextBtn.addEventListener('click', function(e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    scrollCarouselArea('scrollarea-latest', 1);
                }});
            }}
            
            // Auto-scroll lento
            let scrollPos = 0;
            const scrollStep = 1; // pixels por intervalo
            const scrollInterval = 50; // ms entre cada paso
            
            latestCarouselInterval = setInterval(() => {{
                const track = latestTrack;
                const trackWidth = track.scrollWidth;
                const containerWidth = scrollArea.clientWidth;
                
                if (trackWidth <= containerWidth) return;
                
                scrollPos += scrollStep;
                
                // Reiniciar al llegar al final
                if (scrollPos > trackWidth - containerWidth) {{
                    scrollPos = 0;
                }}
                
                scrollArea.scrollLeft = scrollPos;
            }}, scrollInterval);
            
            // Pausar auto-scroll al pasar el mouse
            scrollArea.addEventListener('mouseenter', () => {{
                if (latestCarouselInterval) clearInterval(latestCarouselInterval);
            }});
            
            scrollArea.addEventListener('mouseleave', () => {{
                scrollPos = scrollArea.scrollLeft;
                latestCarouselInterval = setInterval(() => {{
                    const track = latestTrack;
                    const trackWidth = track.scrollWidth;
                    const containerWidth = scrollArea.clientWidth;
                    
                    if (trackWidth <= containerWidth) return;
                    
                    scrollPos += scrollStep;
                    
                    if (scrollPos > trackWidth - containerWidth) {{
                        scrollPos = 0;
                    }}
                    
                    scrollArea.scrollLeft = scrollPos;
                }}, scrollInterval);
            }});
        }}
        
        function showTab(tab, btnElement) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            if (btnElement) btnElement.classList.add('active');
            document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
            document.getElementById('content-' + tab).classList.add('active');
            currentTab = tab;
            
            // Limpiar posiciones de carousels al cambiar de pestaña
            for (let key in carouselPositions) {{
                delete carouselPositions[key];
            }}
            
            // Aplicar filtros primero, luego reinicializar carousels
            applyFilters();
            
            // Reinicializar posiciones de carousels después de que el DOM se actualice
            setTimeout(() => {{
                initCarousels();
            }}, 100);
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
        
        // Función para generar HTML de item (global)
        function generateItemHTML(item) {{
            let nombre = item.nombre_limpio || item.name || '';
            const year = item.year || 'N/A';
            const genero = item.specificGenre || item.genre || 'N/A';
            const imagen = item.imagen_url || item.imagen || null;
            const tipo = item.tipo || item.type || 'anime';
            const href = item.href || item.url || '';
            
            // Quitar el año del nombre (patrón " (YYYY)")
            nombre = nombre.replace(/\s*\(\d{{4}}\)\s*$/, '').trim();
            
            const emojis = {{ 'anime': '🍜', 'dibujos': '🎨', 'peliculas': '🎬', 'series': '📺' }};
            const emoji = emojis[tipo] || '📺';
            
            const imagenHTML = imagen 
                ? `<img src="${{imagen}}" class="item-image" alt="${{nombre}}" loading="lazy" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"><div class="item-image-placeholder" style="display:none">${{emoji}}</div>`
                : `<div class="item-image-placeholder">${{emoji}}</div>`;
            
            // Usar href para abrir modal (evita problemas con JSON.stringify)
            const safeHref = href.replace(/"/g, '&quot;');
            return `<div class="item-card" title="${{nombre}} (${{year}})" onclick='openModalByHref("${{safeHref}}")' style="cursor: pointer;">
                ${{imagenHTML}}
                <div class="item-overlay"></div>
                <div class="item-content">
                    <div class="item-title">${{nombre}}</div>
                    <div class="item-meta">
                        <span class="meta-badge">📅 ${{year}}</span>
                    </div>
                </div>
            </div>`;
        }}
        
        // Función para manejar el autocompletado
        let selectedSuggestionIndex = -1;
        
        function handleSearchInput(event) {{
            console.log('handleSearchInput llamado:', event.key, document.getElementById('searchInput').value);
            const input = document.getElementById('searchInput');
            const suggestionsDiv = document.getElementById('searchSuggestions');
            const searchTerm = input.value.toLowerCase().trim();
            console.log('Buscando:', searchTerm, 'longitud:', searchTerm.length);
            
            // Si presiona Enter, abrir la primera sugerencia o aplicar filtro
            if (event.key === 'Enter') {{
                if (selectedSuggestionIndex >= 0) {{
                    const suggestions = suggestionsDiv.querySelectorAll('.suggestion-item');
                    if (suggestions[selectedSuggestionIndex]) {{
                        suggestions[selectedSuggestionIndex].click();
                        return;
                    }}
                }}
                applyFilters();
                suggestionsDiv.style.display = 'none';
                return;
            }}
            
            // Si presiona flechas, navegar entre sugerencias
            if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {{
                const suggestions = suggestionsDiv.querySelectorAll('.suggestion-item');
                if (suggestions.length === 0) return;
                
                if (event.key === 'ArrowDown') {{
                    selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, suggestions.length - 1);
                }} else {{
                    selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
                }}
                
                suggestions.forEach((s, i) => s.classList.toggle('active', i === selectedSuggestionIndex));
                return;
            }}
            
            // Si escapa, cerrar sugerencias
            if (event.key === 'Escape') {{
                suggestionsDiv.style.display = 'none';
                selectedSuggestionIndex = -1;
                return;
            }}
            
            // Si no hay texto, ocultar sugerencias
            if (searchTerm.length < 1) {{
                suggestionsDiv.style.display = 'none';
                return;
            }}
            
            // Buscar coincidencias
            const matches = allItems.filter(item => {{
                const name = String(item.name || '').toLowerCase();
                const genre = String(item.genre || '').toLowerCase();
                const specificGenre = String(item.specificGenre || '').toLowerCase();
                return name.includes(searchTerm) || genre.includes(searchTerm) || specificGenre.includes(searchTerm);
            }}).slice(0, 8); // Máximo 8 sugerencias
            
            console.log('Matches encontrados:', matches.length);
            
            if (matches.length === 0) {{
                suggestionsDiv.style.display = 'none';
                return;
            }}
            
            // Función para limpiar el nombre (extraer solo el título sin corchetes)
            function limpiarNombre(name) {{
                if (!name) return 'Sin nombre';
                // Eliminar [Activo], [Finalizado], etc. al inicio
                let limpio = name.replace(/^\[[^\]]+\]\s*/, '');
                // Extraer solo el nombre antes de cualquier corchete
                const match = limpio.match(/^([^\[]+)/);
                if (match) {{
                    limpio = match[1].trim();
                }}
                // Eliminar el año entre paréntesis si existe al final del nombre
                limpio = limpio.replace(/\s*\(\d{4}\)\s*$/, '');
                return limpio || 'Sin nombre';
            }}
            
            // Generar HTML de sugerencias
            let html = '';
            matches.forEach((item, index) => {{
                const imagen = item.imagen_url || item.imagen || '';
                const nombre = limpiarNombre(item.name);
                const year = item.year || '';
                const tipo = item.tipo || item.type || 'anime';
                
                html += `<div class="suggestion-item" onclick="openModalByHref('${{item.url || item.href}}'); document.getElementById('searchSuggestions').style.display='none';" data-index="${{index}}">
                    <img src="${{imagen}}" class="suggestion-img" alt="" onerror="this.style.display='none'">
                    <div class="suggestion-info">
                        <div class="suggestion-title">${{nombre}}</div>
                        <div class="suggestion-meta">📅 ${{year}} • ${{tipo}}</div>
                    </div>
                </div>`;
            }});
            
            suggestionsDiv.innerHTML = html;
            suggestionsDiv.style.display = 'block';
            console.log('Dropdown mostrado con', matches.length, 'sugerencias');
            selectedSuggestionIndex = -1;
        }}
        
        // Cerrar sugerencias al hacer clic fuera
        document.addEventListener('click', function(event) {{
            const searchContainer = document.querySelector('.search-container');
            const suggestionsDiv = document.getElementById('searchSuggestions');
            if (searchContainer && !searchContainer.contains(event.target)) {{
                suggestionsDiv.style.display = 'none';
            }}
        }});
        
        function applyFilters() {{
            const decada = document.getElementById('decadaFilter').value;
            const genero = document.getElementById('generoFilter').value;
            const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
            
            let filtered = allItems.filter(item => {{
                // Normalizar el tipo para comparación (minúsculas, quitar espacios extras)
                const itemTipo = (item.tipo || item.type || '').toString().toLowerCase().trim();
                const tabTipo = currentTab.toLowerCase().trim();
                const itemGenero = (item.specificGenre || item.genre || '').toLowerCase();
                
                // Comparación flexible: exacta o parcial
                let tipoMatch = false;
                if (currentTab === 'all') {{
                    tipoMatch = true;
                }} else if (itemTipo === tabTipo) {{
                    tipoMatch = true;
                }} else if (tabTipo === 'dibujos' && itemTipo.includes('dibujo')) {{
                    tipoMatch = true;
                }} else if (tabTipo === 'disney' && itemGenero && itemGenero.toLowerCase().includes('disney')) {{
                    tipoMatch = true;
                }} else if (tabTipo === 'peliculas' && (itemTipo.includes('pelicula') || itemTipo === 'película')) {{
                    tipoMatch = true;
                }} else if (tabTipo === 'series' && itemTipo.includes('serie')) {{
                    tipoMatch = true;
                }} else if (tabTipo === 'anime' && itemTipo.includes('anime')) {{
                    tipoMatch = true;
                }}
                
                if (!tipoMatch) return false;
                if (decada !== 'all' && getDecade(item.year) !== decada) return false;
                if (currentTab !== 'disney' && genero !== 'all' && (item.specificGenre || item.genre || 'N/A') !== genero) return false;
                
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
                grid.innerHTML = '<div style="text-align: center; padding: 60px; color: var(--text-secondary);"><div style="font-size: 4rem; margin-bottom: 20px;">🔍</div><p>No se encontraron resultados</p></div>';
                return;
            }}
            
            // Función para normalizar géneros (quitar tildes, minúsculas, trim)
            function normalizeGenre(g) {{
                return g.toLowerCase()
                    .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // quitar tildes
                    .replace(/[^a-z0-9\s]/g, '') // quitar caracteres especiales
                    .trim();
            }}
            
            // Mapeo de géneros normalizados a nombre original (para mostrar)
            const genreDisplayNames = {{}};
            
            // Agrupar por género - cada item SOLO UNA VEZ, usando SOLO el PRIMER género
            const groupedByGenre = {{}};
            const usedIndexes = new Set(); // Índices de items ya asignados
            
            // Asignar cada item a su PRIMER género (eliminando categorías compuestas)
            filtered.forEach((item, index) => {{
                // Si ya fue asignado, saltar
                if (usedIndexes.has(index)) return;
                
                // Obtener género y separar por comas si es compuesto
                // Usar item.genre primero (géneros actualizados manualmente), luego specificGenre
                let fullGenre = item.genre || item.specificGenre || 'Sin Género';
                // Asegurar que sea string
                if (typeof fullGenre !== 'string') {{
                    fullGenre = String(fullGenre || 'Sin Género');
                }}
                // Tomar solo el primer género (antes de la primera coma)
                const originalGenre = fullGenre.split(',')[0].trim();
                const normalizedGenre = normalizeGenre(originalGenre);
                
                // Guardar nombre original para mostrar
                if (!genreDisplayNames[normalizedGenre]) {{
                    genreDisplayNames[normalizedGenre] = originalGenre;
                }}
                
                // Crear array del género si no existe (usando nombre normalizado como key)
                if (!groupedByGenre[normalizedGenre]) {{
                    groupedByGenre[normalizedGenre] = [];
                }}
                
                // Agregar item a su género y marcar índice como usado
                groupedByGenre[normalizedGenre].push(item);
                usedIndexes.add(index);
            }});
            
            // Obtener géneros ordenados alfabéticamente que tengan items
            const sortedGenres = Object.keys(groupedByGenre)
                .filter(g => groupedByGenre[g].length > 0)
                .sort();
            
            // Generar HTML de carruseles por género
            let carouselsHTML = '';
            sortedGenres.forEach((normalizedGenre, genreIndex) => {{
                const items = groupedByGenre[normalizedGenre];
                const itemCount = items.length;
                const displayName = genreDisplayNames[normalizedGenre] || normalizedGenre;
                const safeGenre = normalizedGenre.replace(/[^a-zA-Z0-9]/g, '-');
                // Incluir el tipo de pestaña en el ID para hacerlo único
                const tabPrefix = currentTab === 'all' ? 'all' : currentTab;
                const carouselId = `carousel-${{tabPrefix}}-${{safeGenre}}-${{genreIndex}}`;
                
                const safeId = carouselId.replace(/[^a-zA-Z0-9_-]/g, '-');
                const scrollAreaId = 'scrollarea-' + safeId;
                
                // Crear data attribute con los hrefs de los items
                const itemsHref = items.map(i => i.href || i.url).join(',');
                
                carouselsHTML += `
                <div class="genre-section">
                    <h2 class="genre-title" data-genre="${{displayName}}" data-items="${{itemsHref}}" data-count="${{itemCount}}" title="Ver todos los ${{itemCount}} items de ${{displayName}}">
                        ${{displayName}} <span style="color: var(--text-secondary); font-size: 0.8em;">(${{itemCount}})</span>
                    </h2>
                    <div class="carousel-container">
                        <button class="carousel-btn carousel-prev" data-scrollarea="${{scrollAreaId}}" type="button">❮</button>
                        <div class="carousel-scroll-area" id="${{scrollAreaId}}">
                            <div class="carousel-track" id="${{safeId}}">
                                ${{items.map(item => generateItemHTML(item)).join('')}}
                            </div>
                        </div>
                        <button class="carousel-btn carousel-next" data-scrollarea="${{scrollAreaId}}" type="button">❯</button>
                    </div>
                </div>`;
            }});
            
            grid.innerHTML = carouselsHTML;
            
            // Inicializar carousels con ancho correcto
            setTimeout(() => {{
                initCarousels();
            }}, 0);
            
            // Asignar event listeners a los botones del carousel
            setTimeout(() => {{
                console.log('Asignando event listeners a', grid.querySelectorAll('.carousel-prev').length, 'botones prev y', grid.querySelectorAll('.carousel-next').length, 'botones next');
                
                grid.querySelectorAll('.carousel-prev').forEach((btn, idx) => {{
                    btn.addEventListener('click', function(e) {{
                        e.preventDefault();
                        e.stopPropagation();
                        const scrollAreaId = this.getAttribute('data-scrollarea');
                        console.log('Botón prev #' + idx + ' clickeado, scrollArea:', scrollAreaId);
                        scrollCarouselArea(scrollAreaId, -1);
                    }});
                }});
                grid.querySelectorAll('.carousel-next').forEach((btn, idx) => {{
                    btn.addEventListener('click', function(e) {{
                        e.preventDefault();
                        e.stopPropagation();
                        const scrollAreaId = this.getAttribute('data-scrollarea');
                        console.log('Botón next #' + idx + ' clickeado, scrollArea:', scrollAreaId);
                        scrollCarouselArea(scrollAreaId, 1);
                    }});
                }});
                
                // Asignar event listeners a los títulos de género
                grid.querySelectorAll('.genre-title').forEach((title, idx) => {{
                    title.addEventListener('click', function(e) {{
                        e.preventDefault();
                        e.stopPropagation();
                        const genreName = this.getAttribute('data-genre');
                        const itemsHref = this.getAttribute('data-items');
                        const count = this.getAttribute('data-count');
                        console.log('Título de género clickeado:', genreName, 'Items:', count);
                        showAllByGenre(genreName, itemsHref, count);
                    }});
                }});
            }}, 0);
        }}
        
        // Objeto para almacenar posiciones de cada carousel
        const carouselPositions = {{}};
        
        // Función para inicializar carousels después de renderizar
        function initCarousels() {{
            document.querySelectorAll('.carousel-scroll-area').forEach(area => {{
                const track = area.querySelector('.carousel-track');
                if (track) {{
                    const itemCount = track.querySelectorAll('.item-card').length;
                    const itemWidth = 165; // 150px + 15px gap
                    const totalWidth = itemCount * itemWidth;
                    const areaId = area.id;
                    
                    // Reinicializar posición a 0
                    carouselPositions[areaId] = 0;
                    
                    // Aplicar estilos con !important para asegurar que se apliquen
                    track.style.setProperty('width', totalWidth + 'px', 'important');
                    track.style.setProperty('left', '0px', 'important');
                    track.style.setProperty('position', 'relative', 'important');
                    
                    // El ancho del contenedor es 100% via CSS, no fijo
                    
                    console.log('Carousel inicializado:', areaId, 'Items:', itemCount, 'Ancho:', totalWidth, 'Left:', track.style.left);
                }}
            }});
        }}
        
        // Función para scroll del área del carousel
        function scrollCarouselArea(scrollAreaId, direction) {{
            console.log('scrollCarouselArea llamado con ID:', scrollAreaId, 'dirección:', direction);
            const scrollArea = document.getElementById(scrollAreaId);
            
            if (!scrollArea) {{
                console.error('No se encontró el área de scroll con ID:', scrollAreaId);
                return;
            }}
            
            console.log('scrollArea encontrada:', scrollArea, 'ID:', scrollArea.id, 'Visible:', scrollArea.offsetParent !== null);
            
            // Obtener el ID del track desde el ID del scrollArea
            const trackId = scrollAreaId.replace('scrollarea-', '');
            let track = document.getElementById(trackId);
            
            // Fallback a querySelector si no se encuentra por ID
            if (!track) {{
                track = scrollArea.querySelector('.carousel-track');
            }}
            
            if (!track) {{
                console.error('No se encontró el track. ID buscado:', trackId);
                return;
            }}
            
            console.log('Track encontrado por ID:', trackId, 'Track:', track);
            
            try {{
                // Inicializar posición si no existe
                if (!carouselPositions[scrollAreaId]) {{
                    carouselPositions[scrollAreaId] = 0;
                }}
                
                const itemWidth = 165; // 150px + 15px gap
                
                // Calcular límites - usar ancho real del contenedor visible
                const containerWidth = scrollArea.clientWidth;
                const itemsPerPage = Math.max(1, Math.floor(containerWidth / itemWidth));
                const scrollAmount = itemWidth; // Mover de 1 en 1
                const itemCount = track.querySelectorAll('.item-card').length;
                const trackWidth = itemCount * itemWidth;
                const maxScroll = Math.max(0, trackWidth - containerWidth);
                
                console.log('Items en track:', itemCount, 'Ancho track:', trackWidth, 'Ancho container:', containerWidth, 'Scroll 1 item:', scrollAmount, 'Máximo:', maxScroll);
                
                // Calcular nueva posición
                let newPosition = carouselPositions[scrollAreaId] + (direction * scrollAmount);
                
                // Limitar posición
                newPosition = Math.max(0, Math.min(newPosition, maxScroll));
                
                console.log('Posición actual:', carouselPositions[scrollAreaId], 'Nueva posición:', newPosition, 'Máximo:', maxScroll);
                
                // Aplicar left para el scroll usando setProperty con !important
                const leftValue = -newPosition;
                track.style.setProperty('left', leftValue + 'px', 'important');
                
                // Guardar posición
                carouselPositions[scrollAreaId] = newPosition;
                
                console.log('Left aplicado:', leftValue + 'px', 'Elemento:', track.className, 'ID:', track.id);
                
                // Verificar que se aplicó
                const computedLeft = window.getComputedStyle(track).left;
                console.log('Computed left:', computedLeft);
                
            }} catch (e) {{
                console.error('Error en scrollCarouselArea:', e);
            }}
        }}
        
        // Función para mostrar todos los items de un género
        function showAllByGenre(genreName, itemsHrefStr, count) {{
            try {{
                // Dividir el string de hrefs separados por comas
                const hrefs = itemsHrefStr ? itemsHrefStr.split(',').filter(h => h) : [];
                const genreItems = allItems.filter(item => hrefs.includes(item.href || item.url));
                
                console.log('Mostrando género:', genreName, 'Hrefs:', hrefs.length, 'Items encontrados:', genreItems.length);
                
                // Crear modal con grid de items
                const modal = document.createElement('div');
                modal.className = 'genre-modal';
                modal.innerHTML = `
                    <div class="genre-modal-content">
                        <div class="genre-modal-header">
                            <h2>${{genreName}} (${{genreItems.length}} items)</h2>
                            <button class="close-btn" onclick="this.closest('.genre-modal').remove()">✕</button>
                        </div>
                        <div class="genre-modal-grid">
                            ${{genreItems.map(item => generateItemHTML(item)).join('')}}
                        </div>
                    </div>
                `;
                
                // Agregar estilos al modal
                modal.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.95);
                    z-index: 10000;
                    overflow-y: auto;
                    padding: 20px;
                    box-sizing: border-box;
                `;
                
                document.body.appendChild(modal);
                
                // Cerrar al hacer clic fuera
                modal.addEventListener('click', function(e) {{
                    if (e.target === modal) {{
                        modal.remove();
                    }}
                }});
                
            }} catch(e) {{
                console.error('Error mostrando género:', e);
            }}
        }}
        
        // Funciones del modal estilo Netflix
        function openModalByHref(href) {{
            const item = allItems.find(i => i.href === href || i.url === href);
            if (!item) return;
            openModal(item);
        }}
        
        function openModal(item) {{
            const modal = document.getElementById('netflixModal');
            const modalBgImage = document.getElementById('modalBgImage');
            const modalPoster = document.getElementById('modalPoster');
            const modalTitle = document.getElementById('modalTitle');
            const modalYear = document.getElementById('modalYear');
            const modalGenre = document.getElementById('modalGenre');
            const modalSinopsis = document.getElementById('modalSinopsis');
            const modalSinopsisText = document.getElementById('modalSinopsisText');
            const modalInfoExtra = document.getElementById('modalInfoExtra');
            const modalInfoText = document.getElementById('modalInfoText');
            const modalFichaTecnica = document.getElementById('modalFichaTecnica');
            const modalFichaContent = document.getElementById('modalFichaContent');
            const modalLink = document.getElementById('modalLink');
            const modalRentryLink = document.getElementById('modalRentryLink');
            
            // Llenar datos
            const imagen = item.imagen_url || item.imagen || '';
            const nombre = item.nombre_limpio || item.name || '';
            
            // Imagen de fondo (blur) y poster
            modalBgImage.src = imagen;
            modalPoster.src = imagen;
            modalPoster.alt = nombre;
            
            // Título y metadatos
            modalTitle.textContent = nombre;
            modalYear.textContent = '📅 ' + (item.year || 'N/A');
            modalGenre.textContent = item.specificGenre || item.genre || 'N/A';
            
            // Sinopsis
            if (item.sinopsis && item.sinopsis.length > 10) {{
                modalSinopsisText.textContent = item.sinopsis;
                modalSinopsis.style.display = 'block';
            }} else {{
                modalSinopsis.style.display = 'none';
            }}
            
            // Ficha Técnica
            if (item.ficha_tecnica && Object.keys(item.ficha_tecnica).length > 0) {{
                let fichaHTML = '<div class="ficha-grid">';
                const campos = {{
                    'genero': {{ "label": "Género", "icon": "🎭" }},
                    'ano': {{ "label": "Año", "icon": "📅" }},
                    'idioma': {{ "label": "Idioma", "icon": "🎙️" }},
                    'subtitulos': {{ "label": "Subtítulos", "icon": "💾" }},
                    'formato': {{ "label": "Formato", "icon": "📘" }},
                    'calidad': {{ "label": "Calidad", "icon": "™️" }},
                    'resolucion': {{ "label": "Resolución", "icon": "🖼️" }},
                    'peso': {{ "label": "Peso/Cap", "icon": "⚙️" }},
                    'temporadas': {{ "label": "Temporadas", "icon": "📺" }},
                    'episodios': {{ "label": "Episodios", "icon": "🎬" }},
                    'estudio': {{ "label": "Estudio", "icon": "🏢" }},
                    'director': {{ "label": "Director", "icon": "🎬" }},
                    'reparto': {{ "label": "Reparto", "icon": "👥" }},
                    'nfo': {{ "label": "NFO", "icon": "🎞️", "isLink": true }},
                    'trailer': {{ "label": "Trailer", "icon": "📽️", "isLink": true }}
                }};
                
                for (const [key, config] of Object.entries(campos)) {{
                    const value = item.ficha_tecnica[key];
                    if (value && value.trim() !== '' && value !== 'Año:' && value !== 'Enlace') {{
                        const isLong = value.length > 25 || key === 'genero' || key === 'reparto' || key === 'idioma' || key === 'subtitulos';
                        const className = isLong ? 'ficha-item full-width' : 'ficha-item';
                        let valueHTML;
                        
                        if (config["isLink"]) {{
                            // NFO y Trailer como enlaces
                            valueHTML = `<a href="${{value}}" target="_blank" class="ficha-link">${{value}}</a>`;
                        }} else {{
                            valueHTML = value;
                        }}
                        
                        fichaHTML += `<div class="${{className}}"><span class="ficha-label">${{config["icon"]}} ${{config["label"]}}:</span><span class="ficha-value">${{valueHTML}}</span></div>`;
                    }}
                }}
                fichaHTML += '</div>';
                modalFichaContent.innerHTML = fichaHTML;
                modalFichaTecnica.style.display = 'block';
            }} else {{
                modalFichaTecnica.style.display = 'none';
            }}
            
            // Info extra (desde Género: hasta Trailer:)
            if (item.info_extra && item.info_extra.length > 10) {{
                modalInfoText.textContent = item.info_extra;
                modalInfoExtra.style.display = 'block';
            }} else {{
                modalInfoExtra.style.display = 'none';
            }}
            
            // Link al foro
            modalLink.href = item.url || '#';
            
            // Link de Ver Online (rentry.co)
            if (item.rentry_url) {{
                modalRentryLink.href = item.rentry_url;
                modalRentryLink.style.display = 'inline-block';
            }} else {{
                modalRentryLink.style.display = 'none';
            }}
            
            // Mostrar modal
            modal.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevenir scroll
        }}
        
        function closeModal(event) {{
            if (event && event.target !== event.currentTarget) return;
            
            const modal = document.getElementById('netflixModal');
            modal.classList.remove('active');
            document.body.style.overflow = ''; // Restaurar scroll
            
            // Limpiar imagen
            setTimeout(() => {{
                document.getElementById('modalImage').src = '';
            }}, 300);
        }}
        
        // Cerrar modal con ESC
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') closeModal();
        }});
        
        // Llenar carrusel de últimas añadidas
        fillLatestCarousel();
        
        applyFilters();
    </script>
    
    <!-- Modal estilo Netflix -->
    <div class="modal-overlay" id="netflixModal" onclick="closeModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <!-- Imagen horizontal de fondo -->
            <img class="modal-bg-image" id="modalBgImage" src="" alt="">
            <!-- Gradiente para difuminar la transición -->
            <div class="modal-bg-gradient"></div>
            
            <button class="modal-close" onclick="closeModal()">×</button>
            
            <div class="modal-content-wrapper">
                <!-- Poster pequeño superpuesto -->
                <img class="modal-poster" id="modalPoster" src="" alt="">
                
                <div class="modal-info">
                    <h2 class="modal-title" id="modalTitle"></h2>
                    <div class="modal-meta">
                        <span class="modal-meta-badge" id="modalYear"></span>
                        <span class="modal-meta-badge" id="modalGenre"></span>
                    </div>
                    
                    <!-- Sinopsis con label -->
                    <div class="modal-sinopsis" id="modalSinopsis" style="display: none;">
                        <span class="modal-sinopsis-label">Sinopsis</span>
                        <span id="modalSinopsisText"></span>
                    </div>
                    
                    <!-- Ficha Técnica -->
                    <div class="modal-ficha-tecnica" id="modalFichaTecnica" style="display: none;">
                        <h3>Ficha Técnica</h3>
                        <div id="modalFichaContent"></div>
                    </div>
                    
                    <div class="modal-info-extra" id="modalInfoExtra" style="display: none;">
                        <h3>Información</h3>
                        <p id="modalInfoText"></p>
                    </div>
                    
                    <!-- Botones de acción -->
                    <div class="modal-buttons">
                        <a class="modal-link" id="modalLink" href="#" target="_blank">Ver en el foro →</a>
                        <a class="modal-link modal-link-online" id="modalRentryLink" href="#" target="_blank" style="display: none;">Ver Online →</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    # Guardar como index.html para GitHub Pages
    output_file = 'index.html'
    with open(output_file, 'w', encoding='utf-8') as f:
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
    print(f"   • Archivo generado: {output_file}")
    print(f"   • Duración: {str(duracion).split('.')[0]}")
    
    # Logging del resumen
    logger.info(f"HTML generado exitosamente - Total: {len(todos_items)} items")
    logger.info(f"Distribución - Anime: {len(animes)}, Dibujos: {len(dibujos)}, Películas: {len(peliculas)}, Series: {len(series)}")
    
    print(f"\n✅ HTML Premium con diseño Netflix generado")
    print(f"📁 Archivo guardado como: {output_file}")
    
    return {
        'total_items': len(todos_items),
        'animes': len(animes),
        'dibujos': len(dibujos),
        'peliculas': len(peliculas),
        'series': len(series),
        'generos': len(generos_ordenados),
        'backup_ok': backup_ok,
        'html_file': output_file
    }

# Ejecutar la función
if __name__ == "__main__":
    generar_html_foroactivo()
