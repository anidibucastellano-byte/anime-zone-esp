#!/usr/bin/env python3
"""
Descargador de 3Cat usando Selenium para scroll infinito
Esto carga TODOS los capítulos (52) haciendo scroll en la página
"""
import subprocess
import sys
import json
import re
from pathlib import Path
from time import sleep

# Intentar importar selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium no instalado. Instalando...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'selenium'], capture_output=True)
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        SELENIUM_AVAILABLE = True
    except:
        pass


class Descargador3CatSelenium:
    def __init__(self):
        self.output_dir = Path('descargas_3cat')
        self.output_dir.mkdir(exist_ok=True)
        self.driver = None
    
    def iniciar_navegador(self):
        """Inicia Chrome en modo headless"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"❌ Error al iniciar Chrome: {e}")
            print("📝 Asegúrate de tener Chrome instalado y chromedriver en el PATH")
            print("   O instala: pip install webdriver-manager")
            return False
    
    def obtener_todos_capitulos(self, url):
        """Hace scroll infinito para cargar todos los capítulos"""
        if not self.iniciar_navegador():
            return []
        
        print(f"🌐 Cargando página: {url}")
        self.driver.get(url)
        
        # Esperar a que cargue el contenido inicial
        sleep(3)
        
        urls_videos = set()
        scrolls = 0
        max_scrolls = 50  # Límite de intentos
        sin_cambios = 0
        
        print("📜 Haciendo scroll para cargar todos los capítulos...")
        
        while scrolls < max_scrolls and sin_cambios < 5:
            # Obtener URLs actuales
            html = self.driver.page_source
            
            # Buscar enlaces de video
            patron = r'href="(/3cat/[^"]+/video/\d+/)"'
            matches = re.findall(patron, html)
            
            count_before = len(urls_videos)
            
            for match in matches:
                url_video = f"https://www.3cat.cat{match}"
                urls_videos.add(url_video)
            
            # Verificar si encontramos nuevos
            if len(urls_videos) > count_before:
                print(f"   Scroll {scrolls}: {len(urls_videos)} capítulos encontrados")
                sin_cambios = 0
            else:
                sin_cambios += 1
            
            # Hacer scroll
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)  # Esperar a que cargue
            
            scrolls += 1
            
            # Si tenemos 52 o más, terminamos
            if len(urls_videos) >= 52:
                break
        
        # También intentar extraer del JSON de la página
        try:
            next_data = self.driver.execute_script(
                'return document.getElementById("__NEXT_DATA__")?.textContent'
            )
            if next_data:
                data = json.loads(next_data)
                urls_json = self._extraer_urls_de_json(data)
                for u in urls_json:
                    urls_videos.add(u)
        except:
            pass
        
        self.driver.quit()
        
        # Eliminar duplicados usando ID de video como clave
        urls_dict = {}
        for url in urls_videos:
            id_match = re.search(r'/video/(\d+)/', url)
            if id_match:
                video_id = id_match.group(1)
                if video_id not in urls_dict:
                    urls_dict[video_id] = url
        
        urls_list = list(urls_dict.values())
        print(f"\n✅ Total de capítulos únicos: {len(urls_list)}")
        return urls_list
    
    def _extraer_urls_de_json(self, data):
        """Extrae URLs recursivamente del JSON"""
        urls = []
        
        def buscar(obj, depth=0):
            if depth > 10:
                return
            if isinstance(obj, dict):
                # Buscar URL directa
                for key in ['url', 'permalink', 'href']:
                    if key in obj and obj[key] and 'video' in str(obj[key]):
                        url = obj[key]
                        if url.startswith('/'):
                            url = f"https://www.3cat.cat{url}"
                        if url not in urls:
                            urls.append(url)
                # Buscar ID para construir URL
                if 'id' in obj and 'titulo' in obj:
                    id_vid = obj['id']
                    titulo = re.sub(r'[^\w\s-]', '', obj['titulo']).strip().lower().replace(' ', '-')
                    url = f"https://www.3cat.cat/3cat/{titulo}/video/{id_vid}/"
                    if url not in urls:
                        urls.append(url)
                # Recursión
                for v in obj.values():
                    buscar(v, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    buscar(item, depth + 1)
        
        buscar(data)
        return urls
    
    def descargar_video(self, url, numero, total):
        """Descarga un video en máxima calidad"""
        
        # Extraer ID del video de la URL
        id_match = re.search(r'/video/(\d+)/', url)
        if id_match:
            video_id = id_match.group(1)
        else:
            video_id = "unknown"
        
        # Verificar si ya existe un archivo con este ID
        archivos_existentes = list(self.output_dir.glob(f'*_{video_id}.*'))
        if archivos_existentes:
            print(f"\n[{numero}/{total}] Video {video_id} ya existe, omitiendo...")
            return True
        
        print(f"\n[{numero}/{total}] {url}")
        
        # Intentar con formato best primero (más compatible)
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--no-warnings',
            '-f', 'best',
            '-o', str(self.output_dir / f'%(title)s_%(id)s.%(ext)s'),
            '--add-metadata',
            '--no-playlist',
            '--no-check-certificate',
            url
        ]
        
        try:
            print(f"   ⬇️  Descargando...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print(f"   ✅ Descargado")
                return True
            else:
                # Mostrar error para diagnóstico
                error_msg = result.stderr[-300:] if result.stderr else "Sin mensaje de error"
                print(f"   ❌ Error: {error_msg[:100]}...")
                
                # Intentar con URL alternativa (directa al video)
                return self._descargar_url_alternativa(video_id, url)
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️  Timeout (video muy largo)")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def _descargar_url_alternativa(self, video_id, original_url):
        """Intenta descargar usando URL de API directa"""
        print(f"   🔄 Intentando método alternativo...")
        
        # Verificar si ya existe
        archivos_existentes = list(self.output_dir.glob(f'*_{video_id}.*'))
        if archivos_existentes:
            print(f"   ✅ Ya existe (omitido)")
            return True
        
        # Intentar URL directa de API
        urls_alternativas = [
            f"https://api-media.3cat.cat/gava/v1/media/{video_id}",
            f"https://www.3cat.cat/video/{video_id}/",
            original_url,
        ]
        
        for url_alt in urls_alternativas:
            cmd = [
                sys.executable, '-m', 'yt_dlp',
                '--no-warnings',
                '-f', 'best',
                '-o', str(self.output_dir / f'%(title)s_%(id)s.%(ext)s'),
                '--no-check-certificate',
                url_alt
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=300)
                if result.returncode == 0:
                    print(f"   ✅ Descargado (método alternativo)")
                    return True
            except:
                continue
        
        print(f"   ❌ Falló el método alternativo")
        return False
    
    def descargar_todos(self, url):
        """Proceso completo"""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium no disponible")
            return
        
        print("="*60)
        print("🎬 DESCARGADOR 3CAT CON SCROLL INFINITO")
        print("="*60)
        
        urls = self.obtener_todos_capitulos(url)
        
        if not urls:
            print("❌ No se encontraron videos")
            return
        
        if len(urls) < 50:
            print(f"⚠️ Solo se encontraron {len(urls)} capítulos de 52")
            print("📝 Posible solución: Aumentar el tiempo de espera entre scrolls")
        
        print(f"\n📁 Guardando en: {self.output_dir.absolute()}")
        print("-"*60)
        
        exitosos = 0
        fallidos = []
        
        for i, video_url in enumerate(urls, 1):
            intentos = 0
            max_intentos = 2
            descargado = False
            
            while intentos < max_intentos and not descargado:
                if intentos > 0:
                    print(f"   🔄 Reintento {intentos}/{max_intentos-1}...")
                    sleep(3)
                
                descargado = self.descargar_video(video_url, i, len(urls))
                intentos += 1
            
            if descargado:
                exitosos += 1
            else:
                fallidos.append(video_url)
            
            sleep(2)  # Pausa entre videos
        
        # Guardar lista de fallidos
        if fallidos:
            archivo_fallidos = self.output_dir / 'videos_fallidos.txt'
            with open(archivo_fallidos, 'w', encoding='utf-8') as f:
                f.write('# Videos que no se pudieron descargar\n')
                f.write('# Para descargar manualmente:\n')
                f.write('# python -m yt_dlp -f best "URL"\n\n')
                for url in fallidos:
                    f.write(f'{url}\n')
            print(f"\n📝 Lista de fallidos guardada en: {archivo_fallidos}")
        
        print("\n" + "="*60)
        print(f"📊 RESUMEN: {exitosos}/{len(urls)} descargados")
        if fallidos:
            print(f"   ❌ Fallidos: {len(fallidos)}")
        print("="*60)


def main():
    url = "https://www.3cat.cat/3cat/asha/capitols/"
    descargador = Descargador3CatSelenium()
    descargador.descargar_todos(url)


if __name__ == "__main__":
    main()
