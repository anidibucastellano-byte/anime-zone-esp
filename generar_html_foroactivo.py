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
    dibujos = data.get('dibujos', [])
    resumen = data.get('resumen', {})
    
    # Generar HTML
    html = f"""<!-- GENERADO AUTOMÁTICAMENTE - {datetime.now().strftime('%d/%m/%Y %H:%M')} -->
<div class="top-anime-container">
    
    <div class="resumen-stats" style="background: #1a1a1a; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; border: 2px solid #c0392b;">
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
        <h2 style="color: #c0392b; border-bottom: 3px solid #c0392b; padding-bottom: 10px;">🎌 Lista de Anime ({len(animes)} series)</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background: #922b21; color: white;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #641e16;">#</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #641e16;">Nombre</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #641e16;">Año</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #641e16;">Género</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #641e16;">Enlace</th>
                </tr>
            </thead>
            <tbody>"""
    
    # Añadir animes
    for i, anime in enumerate(animes, 1):
        nombre = anime.get('name', '').replace('[Activo]', '').strip()
        year = anime.get('year', 'N/A')
        genero = anime.get('specificGenre', anime.get('genre', 'N/A'))
        url = anime.get('url', '')
        
        bg_color = '#fadbd8' if i % 2 == 0 else '#ffffff'
        
        html += f"""
                <tr style="background: {bg_color};">
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;">{i}</td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa;">{nombre}</td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;">{year}</td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;"><span style="background: #c0392b; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{genero}</span></td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;"><a href="{url}" style="background: #922b21; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px;">Ver</a></td>
                </tr>"""
    
    html += """
            </tbody>
        </table>
    </div>

    <div class="lista-dibujos" style="margin-top: 30px;">
        <h2 style="color: #c0392b; border-bottom: 3px solid #c0392b; padding-bottom: 10px;">📺 Dibujos Animados ({len(dibujos)} series)</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background: #922b21; color: white;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #641e16;">#</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #641e16;">Nombre</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #641e16;">Año</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #641e16;">Género</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #641e16;">Enlace</th>
                </tr>
            </thead>
            <tbody>"""
    
    # Añadir dibujos
    for i, dibujo in enumerate(dibujos, 1):
        nombre = dibujo.get('name', '').replace('[Activo]', '').strip()
        year = dibujo.get('year', 'N/A')
        genero = dibujo.get('specificGenre', dibujo.get('genre', 'N/A'))
        url = dibujo.get('url', '')
        
        bg_color = '#fadbd8' if i % 2 == 0 else '#ffffff'
        
        html += f"""
                <tr style="background: {bg_color};">
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;">{i}</td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa;">{nombre}</td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;">{year}</td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;"><span style="background: #c0392b; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{genero}</span></td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;"><a href="{url}" style="background: #922b21; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px;">Ver</a></td>
                </tr>"""
    
    html += """
            </tbody>
        </table>
    </div>

    <div class="lista-peliculas" style="margin-top: 30px;">
        <h2 style="color: #922b21; border-bottom: 3px solid #922b21; padding-bottom: 10px;">🎬 Lista de Películas ({len(peliculas)} películas)</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background: #641e16; color: white;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #4a1210;">#</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #4a1210;">Nombre</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #4a1210;">Año</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #4a1210;">Género</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #4a1210;">Enlace</th>
                </tr>
            </thead>
            <tbody>"""
    
    # Añadir películas
    for i, pelicula in enumerate(peliculas, 1):
        nombre = pelicula.get('name', '').replace('[Activo]', '').strip()
        year = pelicula.get('year', 'N/A')
        genero = pelicula.get('specificGenre', pelicula.get('genre', 'N/A'))
        url = pelicula.get('url', '')
        
        bg_color = '#f5b7b1' if i % 2 == 0 else '#ffffff'
        
        html += f"""
                <tr style="background: {bg_color};">
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;">{i}</td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa;">{nombre}</td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;">{year}</td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;"><span style="background: #922b21; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{genero}</span></td>
                    <td style="padding: 10px; border: 1px solid #e6b0aa; text-align: center;"><a href="{url}" style="background: #641e16; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 12px;">Ver</a></td>
                </tr>"""
    
    html += """
            </tbody>
        </table>
    </div>

</div>

<style>
.top-anime-container { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; background: #1a1a1a; padding: 20px; border-radius: 10px; }
.top-anime-container table { box-shadow: 0 2px 8px rgba(0,0,0,0.3); border: 1px solid #c0392b; }
.top-anime-container th { font-weight: bold; }
.top-anime-container tr:hover { background: #f5b7b1 !important; }
.top-anime-container a:hover { opacity: 0.8; background: #c0392b !important; }
.top-anime-container h2 { text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
</style>"""
    
    # Guardar HTML
    with open('top_foroactivo.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML generado: top_foroactivo.html")
    print(f"📊 {len(animes)} animes + {len(dibujos)} dibujos + {len(peliculas)} películas")
    print(f"📝 Copia el contenido de top_foroactivo.html y pégalo en foroactivo")

if __name__ == "__main__":
    generar_html_foroactivo()
