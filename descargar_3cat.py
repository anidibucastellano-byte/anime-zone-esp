#!/usr/bin/env python3
"""
Descargador de videos de 3Cat (TV3)
Descarga todos los capítulos de una serie en la mejor calidad disponible
"""

import requests
import json
import re
import os
import sys
import subprocess
from pathlib import Path
from urllib.parse import urljoin, urlparse

class Descargador3Cat:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ca,es;q=0.9,en;q=0.8'
        })
        self.output_dir = Path('descargas_3cat')
        self.output_dir.mkdir(exist_ok=True)

    def obtener_ids_videos(self, url_capitols):
        """Obtiene los IDs de todos los capítulos desde la página de capítulos"""
        print(f"🔍 Analizando {url_capitols}...")
        
        todos_ids = []
        
        # Intentar obtener la página principal
        try:
            response = self.session.get(url_capitols)
            response.raise_for_status()
            html = response.text
            
            # Buscar enlaces a videos - múltiples patrones
            patrones = [
                r'/video/(\d+)/',
                r'video/(\d+)"',
                r'"id":\s*(\d+).*"tipo":\s*"video"',
                r'data-id="(\d+)"',
            ]
            
            for patron in patrones:
                ids_encontrados = re.findall(patron, html)
                for id_video in ids_encontrados:
                    if id_video not in todos_ids:
                        todos_ids.append(id_video)
            
            # Buscar datos JSON embebidos en la página (Next.js data)
            json_data_pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
            match = re.search(json_data_pattern, html, re.DOTALL)
            if match:
                try:
                    next_data = json.loads(match.group(1))
                    # Explorar la estructura para encontrar videos
                    self._extraer_ids_de_json(next_data, todos_ids)
                except:
                    pass
            
            # Intentar paginación / carga más contenido
            # Algunas páginas usan offset o page
            for offset in [0, 20, 40, 60]:
                try:
                    params = {'offset': offset, 'limit': 20}
                    resp = self.session.get(url_capitols, params=params, timeout=10)
                    if resp.status_code == 200:
                        html_pag = resp.text
                        for patron in patrones:
                            ids_pag = re.findall(patron, html_pag)
                            for id_video in ids_pag:
                                if id_video not in todos_ids:
                                    todos_ids.append(id_video)
                except:
                    break
                    
        except Exception as e:
            print(f"⚠️ Error al obtener página: {e}")
        
        print(f"📺 Encontrados {len(todos_ids)} capítulos únicos")
        return todos_ids
    
    def _extraer_ids_de_json(self, data, lista_ids):
        """Recursivamente extrae IDs de video de estructura JSON"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ('id', 'videoId', 'mediaId') and isinstance(value, (str, int)):
                    id_str = str(value)
                    if id_str not in lista_ids and len(id_str) > 5:
                        lista_ids.append(id_str)
                elif isinstance(value, (dict, list)):
                    self._extraer_ids_de_json(value, lista_ids)
        elif isinstance(data, list):
            for item in data:
                self._extraer_ids_de_json(item, lista_ids)

    def obtener_info_video(self, id_video):
        """Obtiene información del video desde la API de 3Cat"""
        # Intentar diferentes endpoints de API
        urls_api = [
            f"https://api-media.3cat.cat/gava/v1/media/{id_video}",
            f"https://api.3cat.cat/gava/v1/media/{id_video}",
        ]
        
        for url_api in urls_api:
            try:
                response = self.session.get(url_api, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        return data
            except Exception as e:
                continue
        
        return None

    def obtener_url_m3u8(self, id_video):
        """Obtiene la URL del stream HLS (m3u8)"""
        info = self.obtener_info_video(id_video)
        
        if not info:
            return None, None
        
        # Extraer datos relevantes
        media = info.get('media', info)
        
        # Buscar URL HLS
        url_hls = None
        urls = media.get('url', [])
        if isinstance(urls, list):
            for url_info in urls:
                if isinstance(url_info, dict):
                    # Buscar el de mayor calidad (normalmente HLS)
                    file_type = url_info.get('filetype', '').lower()
                    if 'hls' in file_type or 'm3u8' in file_type:
                        url_hls = url_info.get('file')
                        break
                    # Alternativa: buscar MP4
                    if not url_hls and ('mp4' in file_type or 'video' in file_type):
                        url_hls = url_info.get('file')
        
        # Obtener título
        titulo = media.get('titulo', f'capitulo_{id_video}')
        if not titulo:
            titulo = media.get('informacio', {}).get('titol', f'capitulo_{id_video}')
        
        # Limpiar título para usarlo como nombre de archivo
        titulo_limpio = re.sub(r'[^\w\s-]', '', titulo).strip()
        titulo_limpio = re.sub(r'\s+', '_', titulo_limpio)
        
        return url_hls, titulo_limpio

    def descargar_con_ytdlp(self, url, titulo):
        """Descarga el video usando yt-dlp (mejor método)"""
        archivo_salida = self.output_dir / f"{titulo}.mp4"
        
        if archivo_salida.exists():
            print(f"   ⏭️  Ya existe: {archivo_salida.name}")
            return True
        
        print(f"   ⬇️  Descargando: {titulo}")
        
        # Comando yt-dlp con mejor calidad
        cmd = [
            'yt-dlp',
            '--no-warnings',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '--merge-output-format', 'mp4',
            '-o', str(archivo_salida),
            '--add-metadata',
            '--embed-thumbnail',
            '--no-check-certificate',
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"   ✅ Completado: {archivo_salida.name}")
                return True
            else:
                print(f"   ❌ Error: {result.stderr[:200]}")
                return False
        except subprocess.TimeoutExpired:
            print(f"   ⏱️  Timeout al descargar")
            return False
        except FileNotFoundError:
            print(f"   ⚠️  yt-dlp no está instalado. Instalando...")
            subprocess.run(['pip', 'install', '-U', 'yt-dlp'], capture_output=True)
            return self.descargar_con_ytdlp(url, titulo)
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    def descargar_con_ffmpeg(self, url_hls, titulo):
        """Descarga usando ffmpeg (alternativa si yt-dlp falla)"""
        archivo_salida = self.output_dir / f"{titulo}.mp4"
        
        if archivo_salida.exists():
            print(f"   ⏭️  Ya existe: {archivo_salida.name}")
            return True
        
        print(f"   ⬇️  Descargando con ffmpeg: {titulo}")
        
        cmd = [
            'ffmpeg',
            '-i', url_hls,
            '-c', 'copy',  # Copiar sin recodificar
            '-bsf:a', 'aac_adtstoasc',  # Fix para audio AAC
            '-y',  # Sobrescribir si existe
            str(archivo_salida)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"   ✅ Completado: {archivo_salida.name}")
                return True
            else:
                print(f"   ❌ Error ffmpeg: {result.stderr[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    def descargar_serie(self, url_capitols):
        """Descarga todos los capítulos de una serie"""
        print("="*60)
        print("🎬 DESCARGADOR DE 3CAT")
        print("="*60)
        
        # Obtener IDs de videos
        ids_videos = self.obtener_ids_videos(url_capitols)
        
        if not ids_videos:
            print("❌ No se encontraron capítulos")
            return
        
        print(f"📁 Guardando en: {self.output_dir.absolute()}")
        print("-"*60)
        
        exitosos = 0
        fallidos = 0
        
        for i, id_video in enumerate(ids_videos, 1):
            print(f"\n[{i}/{len(ids_videos)}] Procesando ID: {id_video}")
            
            # Obtener URL del stream
            url_hls, titulo = self.obtener_url_m3u8(id_video)
            
            if not url_hls:
                # Intentar descargar directamente con yt-dlp usando el URL de la página
                url_pagina = f"https://www.3cat.cat/video/{id_video}/"
                titulo = f"capitulo_{id_video}"
                if self.descargar_con_ytdlp(url_pagina, titulo):
                    exitosos += 1
                else:
                    fallidos += 1
            else:
                # Intentar primero con yt-dlp
                if self.descargar_con_ytdlp(url_hls, titulo):
                    exitosos += 1
                else:
                    # Fallback a ffmpeg
                    if self.descargar_con_ffmpeg(url_hls, titulo):
                        exitosos += 1
                    else:
                        fallidos += 1
        
        print("\n" + "="*60)
        print(f"📊 RESUMEN:")
        print(f"   ✅ Exitosos: {exitosos}")
        print(f"   ❌ Fallidos: {fallidos}")
        print(f"   📁 Guardados en: {self.output_dir.absolute()}")
        print("="*60)


def instalar_ytdlp():
    """Instala yt-dlp si no está disponible"""
    print("📦 Instalando yt-dlp...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-U', 'yt-dlp'], 
                      capture_output=True, timeout=60)
        return True
    except:
        return False


def verificar_ytdlp():
    """Verifica si yt-dlp está instalado"""
    try:
        subprocess.run([sys.executable, '-m', 'yt_dlp', '--version'], capture_output=True, timeout=5)
        return True
    except:
        return False


def get_ytdlp_cmd():
    """Retorna el comando yt-dlp apropiado para el sistema"""
    return [sys.executable, '-m', 'yt_dlp']


def descargar_con_ytdlp_directo(url_playlist):
    """Método alternativo: usa yt-dlp directamente para descargar toda la playlist"""
    print("="*60)
    print("🎬 MÉTODO DIRECTO CON YT-DLP")
    print("="*60)
    
    # Verificar e instalar yt-dlp si es necesario
    if not verificar_ytdlp():
        print("⚠️  yt-dlp no encontrado. Intentando instalar...")
        if instalar_ytdlp():
            print("✅ yt-dlp instalado")
        else:
            print("❌ No se pudo instalar yt-dlp automáticamente")
            print("📝 Instálalo manualmente con: pip install yt-dlp")
            return
    
    output_dir = Path('descargas_3cat')
    output_dir.mkdir(exist_ok=True)
    
    # Obtener comando base
    ytdlp_cmd = get_ytdlp_cmd()
    
    # Primero listar los videos disponibles
    print("🔍 Listando videos disponibles...")
    cmd_list = ytdlp_cmd + ['--flat-playlist', '-J', url_playlist]
    
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            entries = data.get('entries', [])
            print(f"📺 Encontrados {len(entries)} videos")
            
            # Descargar cada uno
            for i, entry in enumerate(entries, 1):
                video_url = entry.get('url') or f"https://www.3cat.cat/video/{entry.get('id')}/"
                titulo = entry.get('title', f'capitulo_{i}').replace(' ', '_').replace('/', '-')
                
                print(f"\n[{i}/{len(entries)}] {titulo}")
                
                cmd_download = ytdlp_cmd + [
                    '--no-warnings',
                    '-f', 'best',
                    '-o', str(output_dir / f'{titulo}.%(ext)s'),
                    '--add-metadata',
                    video_url
                ]
                
                subprocess.run(cmd_download, capture_output=True, timeout=300)
                
        else:
            print("❌ No se pudo listar la playlist")
            print(f"   Error: {result.stderr[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    # URL de la serie Asha
    url = "https://www.3cat.cat/3cat/asha/capitols/"
    
    # Preguntar método
    print("="*60)
    print("🎬 DESCARGADOR DE 3CAT")
    print("="*60)
    print("\nMétodos disponibles:")
    print("1. Automático con yt-dlp (recomendado - detecta todos los videos)")
    print("2. Script Python con análisis de página")
    print()
    
    try:
        opcion = input("Selecciona método (1/2) [1]: ").strip() or "1"
    except:
        opcion = "1"
    
    if opcion == "1":
        descargar_con_ytdlp_directo(url)
    else:
        descargador = Descargador3Cat()
        descargador.descargar_serie(url)


if __name__ == "__main__":
    main()
