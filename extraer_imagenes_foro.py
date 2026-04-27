"""
Sistema de extracción de imágenes del foro Foroactivo
Extrae miniaturas/pósters de los temas de anime para usar en la web estilo Netflix
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
from urllib.parse import urljoin, urlparse
from pathlib import Path

# Configuración
FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"
USERNAME = "Admin"
PASSWORD = "9XsBiygA2CpqgB9"

# Directorio para guardar imágenes
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

class ForoImageExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.logged_in = False
        
    def login(self):
        """Iniciar sesión en el foro"""
        print(f"🔐 Intentando login en {FORO_URL}...")
        
        try:
            # Primero obtener la página de login para extraer tokens
            response = self.session.get(LOGIN_URL, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar el formulario de login
            login_form = soup.find('form', {'id': 'login'})
            if not login_form:
                # Probar con otros selectores
                login_form = soup.find('form', {'name': 'form_login'})
            
            # Preparar datos de login
            login_data = {
                'username': USERNAME,
                'password': PASSWORD,
                'login': 'Conectarse'
            }
            
            # Extraer campos ocultos si existen
            if login_form:
                for input_tag in login_form.find_all('input', {'type': 'hidden'}):
                    if input_tag.get('name'):
                        login_data[input_tag['name']] = input_tag.get('value', '')
            
            # Enviar petición de login
            post_url = login_form.get('action', LOGIN_URL) if login_form else LOGIN_URL
            if not post_url.startswith('http'):
                post_url = urljoin(FORO_URL, post_url)
            
            login_response = self.session.post(post_url, data=login_data, timeout=30)
            
            # Verificar si el login fue exitoso
            if 'desconectado' not in login_response.text.lower() and \
               (USERNAME.lower() in login_response.text.lower() or 
                'admin' in login_response.text.lower() or
                'panel' in login_response.text.lower()):
                self.logged_in = True
                print(f"✅ Login exitoso como {USERNAME}")
                return True
            else:
                print(f"❌ Login fallido")
                print(f"   Respuesta: {login_response.status_code}")
                # Guardar para debug
                with open('login_debug.html', 'w', encoding='utf-8') as f:
                    f.write(login_response.text)
                return False
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False
    
    def extraer_imagen_de_tema(self, tema_url):
        """Extraer la imagen principal de un tema del foro"""
        try:
            response = self.session.get(tema_url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar imágenes en el primer post (generalmente el más grande)
            # Foroactivo típicamente tiene la estructura: .post o .postbody
            
            imagenes = []
            
            # PALABRAS CLAVE PARA EXCLUIR (emojis, iconos, logos, etc)
            EXCLUIDAS = ['sinopsis', 'ficha_tecnica', 'banner', 'logo', 'portad', 'icono', 'icon', 
                         'smiles', 'emoji', 'mini', 'button', 'herz', 'smile', 'avatar', 'firma',
                         '2img.net', 'servimg.com/u/f', 'i/servimg', 'smiles']
            
            # 1. BUSCAR PRIMERO EN IMG TAGS DE CLOUDINARY (mejor calidad)
            # Las imágenes reales de portada suelen estar en img tags
            cloudinary_imgs = soup.find_all('img', src=lambda x: x and 'cloudinary.com' in x)
            for img in cloudinary_imgs:
                src = img.get('src', '')
                # Ignorar imágenes excluidas
                if any(bad in src.lower() for bad in EXCLUIDAS):
                    continue
                # Verificar tamaño si está disponible
                width = img.get('width', '')
                if width and int(width) < 150:  # Ignorar imágenes muy pequeñas
                    continue
                # Priorizar posters de TMDB o mis_archivos_elegidos
                if 'manual_poster' in src or 'tmdb' in src or 'mis_archivos_elegidos' in src:
                    imagenes.append((src, 1000))
                else:
                    # Otras imágenes de cloudinary con prioridad media
                    imagenes.append((src, 700))
            
            # 2. BUSCAR EN META TAGS (solo si no encontramos en img tags)
            if not imagenes:
                og_image = soup.find('meta', property='og:image')
                if og_image:
                    src = og_image.get('content', '')
                    # Solo usar si NO es el logo del foro ni excluida
                    if src and 'cloudinary.com' in src:
                        if not any(bad in src.lower() for bad in EXCLUIDAS):
                            imagenes.append((src, 500))
                
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                if twitter_image:
                    src = twitter_image.get('content', '')
                    if src and 'cloudinary.com' in src and src not in [x[0] for x in imagenes]:
                        if not any(bad in src.lower() for bad in EXCLUIDAS):
                            imagenes.append((src, 400))
            
            # 3. Buscar en el primer mensaje/tema (por si está ahí)
            if not imagenes:
                first_post = soup.find('div', {'class': ['post', 'postbody', 'content', 'post_content']})
                if first_post:
                    imgs = first_post.find_all('img')
                    for img in imgs:
                        src = img.get('src', '')
                        # Excluir gifs, emojis y URLs excluidas
                        if not src or src.endswith('.gif'):
                            continue
                        if any(bad in src.lower() for bad in EXCLUIDAS):
                            continue
                        # Filtrar por tamaño si está disponible
                        width = img.get('width', '')
                        height = img.get('height', '')
                        
                        # Preferir imágenes grandes (pósters)
                        if width and int(width) > 200:
                            imagenes.append((src, int(width)))
                        elif not width:  # Si no hay tamaño, solo si es cloudinary o similar
                            if 'cloudinary' in src or 'res.cloudinary' in src:
                                imagenes.append((src, 0))
            
            # 4. NO buscar en headerbar - ahí solo está el logo del foro
            # Solo buscar en servimg si está en el contenido del post (no en header)
            if not imagenes:
                headerbar = soup.find('div', {'class': 'headerbar'})
                all_servimg = soup.find_all('img', src=lambda x: x and 'servimg.com' in x)
                for img in all_servimg:
                    # Ignorar si está en headerbar
                    if headerbar and img.find_parent('div', {'class': 'headerbar'}):
                        continue
                    src = img.get('src', '')
                    # Usar lista EXCLUIDAS
                    if any(bad in src.lower() for bad in EXCLUIDAS):
                        continue
                    # Verificar tamaño si está disponible
                    width = img.get('width', '')
                    if width and int(width) < 150:
                        continue
                    imagenes.append((src, 500))
            
            # 5. Buscar enlaces a imágenes
            if not imagenes:
                links = soup.find_all('a', {'class': ['postlink', 'attach']})
                for link in links:
                    href = link.get('href', '')
                    if any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        imagenes.append((href, 0))
            
            # Devolver la imagen más grande o la primera encontrada
            if imagenes:
                # Ordenar por tamaño (mayor primero)
                imagenes.sort(key=lambda x: x[1], reverse=True)
                return imagenes[0][0]
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error extrayendo imagen de {tema_url}: {e}")
            return None
    
    def descargar_imagen(self, url, nombre_archivo):
        """Descargar y guardar una imagen"""
        try:
            # Hacer la URL absoluta si es relativa
            if not url.startswith('http'):
                url = urljoin(FORO_URL, url)
            
            # Descargar imagen
            response = self.session.get(url, timeout=30, stream=True)
            if response.status_code == 200:
                # Determinar extensión
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'webp' in content_type:
                    ext = '.webp'
                else:
                    ext = '.jpg'  # Default
                
                # Sanitizar nombre
                nombre_limpio = re.sub(r'[^\w\s-]', '', nombre_archivo).strip()
                nombre_limpio = re.sub(r'[-\s]+', '-', nombre_limpio)
                
                filepath = IMAGES_DIR / f"{nombre_limpio}{ext}"
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return str(filepath)
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error descargando imagen {url}: {e}")
            return None
    
    def procesar_top_json(self):
        """Procesar TOP.json y extraer imágenes para cada serie"""
        print("\n📂 Cargando TOP.json...")
        
        try:
            with open('TOP.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Error cargando TOP.json: {e}")
            return
        
        # Categorías a procesar
        categorias = ['anime', 'dibujos', 'peliculas', 'series']
        
        total_procesados = 0
        total_imagenes = 0
        
        for categoria in categorias:
            items = data.get(categoria, [])
            print(f"\n📁 Procesando {len(items)} items de '{categoria}'...")
            
            for i, item in enumerate(items, 1):
                nombre = item.get('name', 'Sin nombre')
                url = item.get('url', '')
                
                if not url:
                    continue
                
                print(f"   [{i}/{len(items)}] {nombre[:50]}...", end=' ')
                
                # Verificar si ya tiene imagen
                if item.get('imagen') and os.path.exists(item['imagen']):
                    print(f"✅ Ya tiene imagen")
                    continue
                
                # Extraer imagen del tema
                imagen_url = self.extraer_imagen_de_tema(url)
                
                if imagen_url:
                    # Descargar imagen
                    imagen_path = self.descargar_imagen(imagen_url, f"{categoria}_{i}_{nombre}")
                    
                    if imagen_path:
                        item['imagen'] = imagen_path
                        item['imagen_url'] = imagen_url
                        total_imagenes += 1
                        print(f"✅ Imagen guardada")
                    else:
                        print(f"❌ Error descargando")
                else:
                    print(f"⚠️ Sin imagen en el tema")
                
                total_procesados += 1
                
                # Pausa breve para no saturar el servidor
                time.sleep(0.5)
        
        # Guardar TOP.json actualizado
        print(f"\n💾 Guardando TOP.json actualizado...")
        try:
            with open('TOP.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ TOP.json guardado")
        except Exception as e:
            print(f"❌ Error guardando: {e}")
        
        print(f"\n📊 Resumen:")
        print(f"   Items procesados: {total_procesados}")
        print(f"   Imágenes descargadas: {total_imagenes}")
        print(f"   Imágenes guardadas en: {IMAGES_DIR.absolute()}")


def main():
    print("=" * 60)
    print("🎨 EXTRACTOR DE IMÁGENES DEL FORO")
    print("=" * 60)
    
    extractor = ForoImageExtractor()
    
    # Login
    if not extractor.login():
        print("\n❌ No se pudo iniciar sesión. Abortando.")
        return
    
    # Procesar JSON
    extractor.procesar_top_json()
    
    print("\n✅ Proceso completado!")
    print(f"📁 Las imágenes están en: {IMAGES_DIR.absolute()}")


if __name__ == "__main__":
    main()
