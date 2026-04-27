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
        .genre-section {{
            margin-bottom: 40px;
            position: relative;
        }}
        
        .genre-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0 0 15px 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
            border-left: 4px solid var(--primary-red);
            padding-left: 15px;
        }}
        
        .carousel-container {{
            position: relative;
            overflow: hidden;
            padding: 0 40px;
        }}
        
        .carousel-track {{
            display: flex;
            gap: 15px;
            overflow-x: auto;
            scroll-behavior: smooth;
            scrollbar-width: none;
            -ms-overflow-style: none;
            padding: 10px 0 20px 0;
        }}
        
        .carousel-track::-webkit-scrollbar {{
            display: none;
        }}
        
        .carousel-btn {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            width: 40px;
            height: 60px;
            background: rgba(0, 0, 0, 0.7);
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            z-index: 10;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
        }}
        
        .carousel-btn:hover {{
            background: rgba(192, 57, 43, 0.9);
            transform: translateY(-50%) scale(1.1);
        }}
        
        .carousel-btn.prev {{
            left: 0;
        }}
        
        .carousel-btn.next {{
            right: 0;
        }}
        
        .carousel-btn.hidden {{
            display: none;
        }}
        
        /* Item card en carrusel */
        .carousel-track .item-card {{
            flex: 0 0 auto;
            width: 200px;
            aspect-ratio: 2/3;
        }}
        
        @media (max-width: 768px) {{
            .carousel-track .item-card {{
                width: 150px;
            }}
            
            .genre-title {{
                font-size: 1.2rem;
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
            padding: 12px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.7) 100%);
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 2;
        }}
        
        .item-title {{
            font-size: 0.9rem;
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
            font-size: 0.75rem;
            padding: 4px 8px;
            border-radius: 4px;
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
            
            .modal-info {{
                text-align: center;
                padding-top: 0;
            }}
            
            .modal-title {{
                font-size: 1.5rem;
            }}
        }}
        
        .modal-info-extra {{
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        .modal-info-extra h3 {{
            color: var(--primary-red);
            margin-bottom: 15px;
            font-size: 1.2rem;
        }}
        
        .modal-info-extra p {{
            color: var(--text-secondary);
            line-height: 1.8;
            white-space: pre-line;
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
            background: #a93226;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(192, 57, 43, 0.4);
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
        <div id="content-peliculas" class="content-section">
            <div id="grid-peliculas" class="genre-carousels"></div>
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
                grid.innerHTML = '<div style="text-align: center; padding: 60px; color: var(--text-secondary);"><div style="font-size: 4rem; margin-bottom: 20px;">🔍</div><p>No se encontraron resultados</p></div>';
                return;
            }}
            
            // Función para generar HTML de item
            function generateItemHTML(item) {{
                const nombre = item.nombre_limpio || item.name || '';
                const year = item.year || 'N/A';
                const genero = item.specificGenre || item.genre || 'N/A';
                const imagen = item.imagen_url || item.imagen || null;
                const tipo = item.tipo || 'anime';
                const href = item.href || item.url || '';
                
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
                            <span class="meta-badge genre-badge">${{genero}}</span>
                        </div>
                    </div>
                </div>`;
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
                const fullGenre = item.specificGenre || item.genre || 'Sin Género';
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
                const carouselId = `carousel-${{safeGenre}}-${{genreIndex}}`;
                
                carouselsHTML += `
                <div class="genre-section">
                    <h2 class="genre-title">${{displayName}} <span style="color: var(--text-secondary); font-size: 0.8em;">(${{itemCount}})</span></h2>
                    <div class="carousel-container">
                        <button class="carousel-btn prev" onclick="scrollCarousel('${{carouselId}}', -1)">❮</button>
                        <div class="carousel-track" id="${{carouselId}}">
                            ${{items.map(item => generateItemHTML(item)).join('')}}
                        </div>
                        <button class="carousel-btn next" onclick="scrollCarousel('${{carouselId}}', 1)">❯</button>
                    </div>
                </div>`;
            }});
            
            grid.innerHTML = carouselsHTML;
        }}
        
        // Función para scroll de carrusel
        function scrollCarousel(carouselId, direction) {{
            const track = document.getElementById(carouselId);
            if (track) {{
                const scrollAmount = 220 * 4; // 4 items por scroll
                track.scrollBy({{ left: direction * scrollAmount, behavior: 'smooth' }});
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
            const modalLink = document.getElementById('modalLink');
            
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
            
            // Info extra (desde Género: hasta Trailer:)
            if (item.info_extra && item.info_extra.length > 10) {{
                modalInfoText.textContent = item.info_extra;
                modalInfoExtra.style.display = 'block';
            }} else {{
                modalInfoExtra.style.display = 'none';
            }}
            
            // Link al foro
            modalLink.href = item.url || '#';
            
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
                    
                    <div class="modal-info-extra" id="modalInfoExtra" style="display: none;">
                        <h3>Información</h3>
                        <p id="modalInfoText"></p>
                    </div>
                    
                    <a class="modal-link" id="modalLink" href="#" target="_blank">Ver en el foro →</a>
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
