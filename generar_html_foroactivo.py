import json
import requests
from datetime import datetime

def generar_html_foroactivo():
    """Generar código HTML premium con filtros interactivos"""
    
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/anidibucastellano-byte/anime-zone-esp/main/TOP.json"
    
    print(f"📥 Descargando TOP.json desde GitHub...")
    
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✅ TOP.json descargado correctamente")
    except Exception as e:
        print(f"❌ Error al descargar desde GitHub: {e}")
        with open('TOP.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    animes = data.get('anime', [])
    dibujos = data.get('dibujos', [])
    peliculas = data.get('peliculas', [])
    resumen = data.get('resumen', {})
    
    # Obtener todos los géneros únicos para el filtro
    todos_generos = set()
    for item in animes + dibujos + peliculas:
        genero = item.get('specificGenre', item.get('genre', 'N/A'))
        if genero and genero != 'N/A':
            todos_generos.add(genero)
    
    generos_ordenados = sorted(todos_generos)
    
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
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 50%, #0d0d0d 100%);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
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
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(135deg, #c0392b 0%, #e74c3c 50%, #f39c12 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-transform: uppercase;
            letter-spacing: 4px;
            margin-bottom: 10px;
        }}
        
        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
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
            transition: all 0.3s ease;
        }}
        
        .tab-btn.active {{
            background: var(--primary-red);
            border-color: var(--primary-red);
            color: white;
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
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            padding: 15px 20px;
        }}
        
        .item-card:hover {{
            border-color: var(--primary-red);
            box-shadow: var(--shadow);
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
            background: var(--bg-elevated);
            border-radius: 20px;
            padding: 5px 12px;
            font-size: 0.85rem;
        }}
        
        .genre-badge {{
            background: var(--primary-red);
            color: white;
        }}
        
        .item-link {{
            background: var(--primary-red);
            color: white;
            text-align: center;
            padding: 8px 20px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            white-space: nowrap;
        }}
        
        .item-link:hover {{
            background: var(--dark-red);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Anime Zone ESP</h1>
        </div>
        
        <div class="stats-bar">
            <div class="stat-card">
                <div class="number">{len(animes)}</div>
                <div class="label">🎌 Anime</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(dibujos)}</div>
                <div class="label">📺 Dibujos</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(peliculas)}</div>
                <div class="label">🎬 Películas</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(animes) + len(dibujos) + len(peliculas)}</div>
                <div class="label">📈 Total</div>
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
            <button class="tab-btn active" onclick="showTab('all')">📋 Todo</button>
            <button class="tab-btn" onclick="showTab('anime')">🎌 Anime</button>
            <button class="tab-btn" onclick="showTab('dibujos')">📺 Dibujos</button>
            <button class="tab-btn" onclick="showTab('peliculas')">🎬 Películas</button>
        </div>
        
        <div id="content-all" class="content-section active">
            <div class="items-grid" id="grid-all"></div>
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
        
        function showTab(tab) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
            document.getElementById('content-' + tab).classList.add('active');
            currentTab = tab;
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
            
            let filtered = allItems.filter(item => {{
                if (currentTab !== 'all' && item.tipo !== currentTab) return false;
                if (decada !== 'all' && getDecade(item.year) !== decada) return false;
                if (genero !== 'all' && (item.specificGenre || item.genre || 'N/A') !== genero) return false;
                return true;
            }});
            
            const gridId = currentTab === 'all' ? 'grid-all' : 'grid-' + currentTab;
            const grid = document.getElementById(gridId);
            
            if (filtered.length === 0) {{
                grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 60px; color: var(--text-secondary);"><div style="font-size: 4rem; margin-bottom: 20px;">🔍</div><p>No se encontraron resultados</p></div>';
                return;
            }}
            
            grid.innerHTML = filtered.map((item, index) => {{
                const nombre = (item.name || '').replace('[Activo]', '').trim();
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
    
    print(f"✅ HTML Premium generado con filtros interactivos")

if __name__ == "__main__":
    generar_html_foroactivo()
