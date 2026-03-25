import json
import requests
from datetime import datetime

def generar_html_foroactivo():
    """Generar código HTML para foroactivo a partir de TOP.json de GitHub"""
    
    # URL del TOP.json en GitHub
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/anidibucastellano-byte/anime-zone-esp/main/TOP.json"
    
    print(f"📥 Descargando TOP.json desde GitHub...")
    
    try:
        # Descargar TOP.json desde GitHub
        response = requests.get(GITHUB_RAW_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✅ TOP.json descargado correctamente")
    except Exception as e:
        print(f"❌ Error al descargar desde GitHub: {e}")
        print(f"📁 Intentando cargar archivo local...")
        # Fallback a archivo local
        with open('TOP.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    animes = data.get('anime', [])
    peliculas = data.get('peliculas', [])
    resumen = data.get('resumen', {})
    
    # Generar HTML
    html = f"""<!-- GENERADO AUTOMÁTICAMENTE - {datetime.now().strftime('%d/%m/%Y %H:%M')} -->
<div class="top-anime-container">
    
    <div class="resumen-stats" style="background: #2c3e50; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
        <h3>📊 Estadísticas del TOP</h3>
        <p>
            <strong>🎌 Anime:</strong> {resumen.get('anime', 0)} | 
            <strong>🎬 Películas:</strong> {resumen.get('peliculas', 0)} | 
            <strong>📺 Dibujos:</strong> {resumen.get('dibujos', 440)} | 
            <strong>📈 Total:</strong> {resumen.get('total', 0)}
        </p>
        <small>Última actualización: {resumen.get('ultima_actualizacion', 'N/A')}</small>
    </div>

    <div class="lista-anime">
        <h2 style="color: #e74c3c; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;">🎌 Lista de Anime ({len(animes)} series)</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background: #34495e; color: white;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #2c3e50;">#</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #2c3e50;">Nombre</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #2c3e50;">Año</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #2c3e50;">Género</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #2c3e50;">Enlace</th>
                </tr>
            </thead>
            <tbody>"""
    
    # Añadir animes
    for i, anime in enumerate(animes, 1):
        nombre = anime.get('name', '').replace('[Activo]', '').strip()
        year = anime.get('year', 'N/A')
        genero = anime.get('specificGenre', anime.get('genre', 'N/A'))
        url = anime.get('url', '')
        
        bg_color = '#ecf0f1' if i % 2 == 0 else '#ffffff'
        
        html += f"""
                <tr style="background: {bg_color};">
                    <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: center;">{i}</td>
                    <td style="padding: 10px; border: 1px solid #bdc3c7;">{nombre}</td>
                    <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: center;">{year}</td>
                    <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: center;"><span style="background: #3498db; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{genero}</span></td>
                    <td style="padding: 10px; border: 1px solid #bdc3c7; text-align: center;"><a href="{url}" style="background: #27ae60; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px;">Ver</a></td>
                </tr>"""
    
    html += """
            </tbody>
        </table>
    </div>

    <div class="lista-peliculas" style="margin-top: 30px;">
        <h2 style="color: #9b59b6; border-bottom: 3px solid #9b59b6; padding-bottom: 10px;">🎬 Lista de Películas ({len(peliculas)} películas)</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background: #8e44ad; color: white;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #7d3c98;">#</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #7d3c98;">Nombre</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #7d3c98;">Año</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #7d3c98;">Género</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #7d3c98;">Enlace</th>
                </tr>
            </thead>
            <tbody>"""
    
    # Añadir películas
    for i, pelicula in enumerate(peliculas, 1):
        nombre = pelicula.get('name', '').replace('[Activo]', '').strip()
        year = pelicula.get('year', 'N/A')
        genero = pelicula.get('specificGenre', pelicula.get('genre', 'N/A'))
        url = pelicula.get('url', '')
        
        bg_color = '#f5eef8' if i % 2 == 0 else '#ffffff'
        
        html += f"""
                <tr style="background: {bg_color};">
                    <td style="padding: 10px; border: 1px solid #d5dbdb; text-align: center;">{i}</td>
                    <td style="padding: 10px; border: 1px solid #d5dbdb;">{nombre}</td>
                    <td style="padding: 10px; border: 1px solid #d5dbdb; text-align: center;">{year}</td>
                    <td style="padding: 10px; border: 1px solid #d5dbdb; text-align: center;"><span style="background: #9b59b6; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{genero}</span></td>
                    <td style="padding: 10px; border: 1px solid #d5dbdb; text-align: center;"><a href="{url}" style="background: #8e44ad; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px;">Ver</a></td>
                </tr>"""
    
    html += """
            </tbody>
        </table>
    </div>

</div>

<style>
.top-anime-container { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; }
.top-anime-container table { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.top-anime-container th { font-weight: bold; }
.top-anime-container tr:hover { background: #d5e8d4 !important; }
.top-anime-container a:hover { opacity: 0.8; }
</style>"""
    
    # Guardar HTML
    with open('top_foroactivo.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML generado: top_foroactivo.html")
    print(f"📊 {len(animes)} animes + {len(peliculas)} películas")
    print(f"📝 Copia el contenido de top_foroactivo.html y pégalo en foroactivo")

if __name__ == "__main__":
    generar_html_foroactivo()
