#!/usr/bin/env python3
"""
Descargador de 3Cat con scraping manual de URLs individuales
"""
import requests
import re
import subprocess
import sys
import json
from pathlib import Path
from time import sleep

class Descargador3Cat:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        self.output_dir = Path('descargas_3cat')
        self.output_dir.mkdir(exist_ok=True)
    
    def obtener_todos_capitulos_api(self):
        """Intenta obtener todos los capítulos desde la API de 3Cat"""
        urls_videos = []
        
        # Intentar diferentes endpoints de API
        endpoints = [
            "https://api.3cat.cat/gava/v1/continguts?codi=asha&tipus=capitol&ordre=capitol&limit=100",
            "https://api.3cat.cat/gava/v1/programes/asha/capitols?limit=100",
            "https://www.3cat.cat/api/3cat/asha/capitols",
        ]
        
        for endpoint in endpoints:
            try:
                print(f"🔍 Probando API: {endpoint}")
                resp = self.session.get(endpoint, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    items = []
                    
                    if isinstance(data, list):
                        items = data
                    elif isinstance(data, dict):
                        for key in ['items', 'data', 'capitols', 'videos', 'continguts']:
                            if key in data and isinstance(data[key], list):
                                items = data[key]
                                break
                    
                    for item in items:
                        url = self._extraer_url(item)
                        if url and url not in urls_videos:
                            urls_videos.append(url)
                    
                    if len(urls_videos) >= 50:
                        print(f"   ✅ API encontró {len(urls_videos)} capítulos")
                        return urls_videos
                        
            except Exception as e:
                continue
        
        return urls_videos
    
    def obtener_urls_videos(self, url_capitols):
        """Scraping de la página para obtener URLs individuales de cada capítulo"""
        print(f"🔍 Analizando página: {url_capitols}")
        
        urls_videos = []
        
        # Primero intentar la API (más completa)
        urls_api = self.obtener_todos_capitulos_api()
        if urls_api:
            urls_videos.extend(urls_api)
        
        # Si no encontramos suficientes, hacer scraping de la página
        if len(urls_videos) < 30:
            try:
                response = self.session.get(url_capitols, timeout=30)
                response.raise_for_status()
                html = response.text
                
                # Buscar datos JSON de Next.js (donde están todos los datos)
                json_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
                
                if json_match:
                    try:
                        data = json.loads(json_match.group(1))
                        urls_json = self._buscar_urls_recursivo(data)
                        for url in urls_json:
                            if url not in urls_videos:
                                urls_videos.append(url)
                    except:
                        pass
                
                # Buscar en HTML directamente
                patrones = [
                    r'href="(/3cat/[^"]+/video/\d+/)"',
                    r'href="(https://www\.3cat\.cat/3cat/[^"]+/video/\d+/)"',
                ]
                for patron in patrones:
                    matches = re.findall(patron, html)
                    for url in matches:
                        if url.startswith('/'):
                            url = f"https://www.3cat.cat{url}"
                        if url not in urls_videos:
                            urls_videos.append(url)
                
                # Intentar con offset para cargar más (paginación)
                for offset in [0, 20, 40, 60, 80, 100]:
                    try:
                        params = {'offset': offset, 'limit': 20}
                        resp = self.session.get(url_capitols, params=params, timeout=10)
                        if resp.status_code == 200:
                            html_pag = resp.text
                            for patron in patrones:
                                matches = re.findall(patron, html_pag)
                                for url in matches:
                                    if url.startswith('/'):
                                        url = f"https://www.3cat.cat{url}"
                                    if url not in urls_videos:
                                        urls_videos.append(url)
                    except:
                        break
                        
            except Exception as e:
                print(f"⚠️ Error al obtener página: {e}")
        
        print(f"📺 Total de capítulos únicos: {len(urls_videos)}")
        return urls_videos
    
    def _extraer_url(self, item):
        """Extrae URL de un item de capítulo"""
        if not isinstance(item, dict):
            return None
        
        # Buscar en diferentes campos posibles
        for key in ['url', 'link', 'href', 'permalink', 'canonicalUrl']:
            if key in item and item[key]:
                url = item[key]
                if 'video' in url:
                    if url.startswith('/'):
                        url = f"https://www.3cat.cat{url}"
                    return url
        
        # Si tiene id y titulo, construir URL
        if 'id' in item:
            id_video = item['id']
            titulo = item.get('titulo', item.get('title', ''))
            if titulo:
                titulo_slug = re.sub(r'[^\w\s-]', '', titulo).strip().lower().replace(' ', '-')
                return f"https://www.3cat.cat/3cat/{titulo_slug}/video/{id_video}/"
        
        return None
    
    def _buscar_urls_recursivo(self, data, max_depth=5, current_depth=0):
        """Busca URLs recursivamente en estructura JSON"""
        if current_depth > max_depth:
            return []
        
        urls = []
        
        if isinstance(data, dict):
            # Verificar si este dict es un capítulo
            url = self._extraer_url(data)
            if url:
                urls.append(url)
            
            # Buscar en valores
            for value in data.values():
                if isinstance(value, (dict, list)):
                    urls.extend(self._buscar_urls_recursivo(value, max_depth, current_depth + 1))
                    
        elif isinstance(data, list):
            for item in data:
                urls.extend(self._buscar_urls_recursivo(item, max_depth, current_depth + 1))
        
        return list(dict.fromkeys(urls))  # Eliminar duplicados manteniendo orden
    
    def descargar_video(self, url, numero, total):
        """Descarga un video individual con yt-dlp en máxima calidad"""
        print(f"\n[{numero}/{total}] Analizando: {url}")
        
        # Primero listar formatos disponibles para debug
        cmd_list = [
            sys.executable, '-m', 'yt_dlp',
            '--no-warnings',
            '--list-formats',
            url
        ]
        
        try:
            result_list = subprocess.run(cmd_list, capture_output=True, text=True, timeout=30)
            # Buscar la mejor calidad disponible (normalmente 1080p o 720p)
            # Las mejores calidades suelen estar al final de la lista
        except:
            pass
        
        # Descargar con la mejor calidad posible
        # bestvideo+bestaudio: descarga video y audio por separado y los mezcla
        # Esto da mejor calidad que 'best' solo
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--no-warnings',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            '--merge-output-format', 'mp4',
            '-o', str(self.output_dir / f'%(title)s.%(ext)s'),
            '--add-metadata',
            '--embed-thumbnail',
            '--no-playlist',
            '--concurrent-fragments', '3',
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"   ✅ Descargado en máxima calidad")
                return True
            else:
                error = result.stderr[:200] if result.stderr else "Error desconocido"
                print(f"   ❌ {error}")
                # Intentar con calidad más baja si falla
                return self._descargar_calidad_baja(url)
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def _descargar_calidad_baja(self, url):
        """Fallback: descargar con calidad estándar si falla la máxima"""
        print(f"   🔄 Intentando con calidad estándar...")
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--no-warnings',
            '-f', 'best',
            '-o', str(self.output_dir / f'%(title)s.%(ext)s'),
            url
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"   ✅ Descargado (calidad estándar)")
                return True
        except:
            pass
        return False
    
    def descargar_todos(self, url_capitols):
        """Descarga todos los capítulos"""
        print("="*60)
        print("🎬 DESCARGADOR DE 3CAT - MODO SCRAPER")
        print("="*60)
        
        urls = self.obtener_urls_videos(url_capitols)
        
        if not urls:
            print("❌ No se encontraron videos")
            return
        
        print(f"📁 Guardando en: {self.output_dir.absolute()}")
        print("-"*60)
        
        exitosos = 0
        for i, url in enumerate(urls, 1):
            if self.descargar_video(url, i, len(urls)):
                exitosos += 1
            sleep(1)  # Pausa entre descargas
        
        print("\n" + "="*60)
        print(f"📊 RESUMEN: {exitosos}/{len(urls)} descargados")
        print("="*60)


def main():
    url = "https://www.3cat.cat/3cat/asha/capitols/"
    descargador = Descargador3Cat()
    descargador.descargar_todos(url)


if __name__ == "__main__":
    main()
