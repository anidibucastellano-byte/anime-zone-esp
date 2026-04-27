#!/usr/bin/env python3
"""
Re-extraer las 248 imágenes con tamaños incorrectos del foro
"""
import json
import os
from extraer_imagenes_foro import ForoImageExtractor

FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"

def safe_filename(nombre):
    import re
    nombre = re.sub(r'[<>:"/\\|?*]', '', nombre)
    nombre = nombre[:80]
    return nombre.strip()

def main():
    # Cargar lista de imágenes incorrectas
    with open('imagenes_incorrectas.json', 'r', encoding='utf-8') as f:
        incorrectas = json.load(f)
    
    # Cargar TOP.json
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"🔄 Re-extrayendo {len(incorrectas)} imágenes...\n")
    
    # Inicializar extractor
    extractor = ForoImageExtractor()
    
    # Login
    login_data = {
        'username': 'Admin',
        'password': '9XsBiygA2CpqgB9',
        'login': '1'
    }
    extractor.session.post(LOGIN_URL, data=login_data)
    print("✅ Login exitoso\n")
    
    descargadas = 0
    fallidas = 0
    
    for i, item_info in enumerate(incorrectas, 1):
        nombre = item_info['nombre']
        href = item_info['href']
        
        # Extraer tema_id del href
        import re
        match = re.search(r'/t(\d+)-', href)
        if not match:
            continue
        tema_id = f"t{match.group(1)}"
        
        print(f"[{i}/{len(incorrectas)}] {nombre[:50]}...")
        
        url_tema = f"{FORO_URL}/{tema_id}-"
        
        # Extraer nueva imagen
        imagen_url = extractor.extraer_imagen_de_tema(url_tema)
        
        if imagen_url:
            # Determinar categoría
            categoria = 'anime'  # default
            for cat in ['anime', 'dibujos', 'peliculas', 'series']:
                for item in data.get(cat, []):
                    if item.get('href', '') == href:
                        categoria = cat
                        break
            
            # Descargar imagen
            safe_name = safe_filename(nombre)
            ext = '.png' if 'png' in imagen_url.lower() else '.jpg'
            filename = f"{categoria}_{tema_id.replace('t', '')}_{safe_name}{ext}"
            filepath = os.path.join('images', filename)
            
            # Borrar imagen anterior si existe
            ruta_antigua = item_info['path'].replace('/', os.sep)
            if os.path.exists(ruta_antigua):
                try:
                    os.remove(ruta_antigua)
                    print(f"   🗑️ Imagen anterior eliminada")
                except:
                    pass
            
            if extractor.descargar_imagen(imagen_url, filepath):
                # Actualizar TOP.json
                for cat in ['anime', 'dibujos', 'peliculas', 'series']:
                    for item in data.get(cat, []):
                        if item.get('href', '') == href:
                            item['imagen'] = filepath.replace('\\', '/')
                            item['imagen_url'] = imagen_url
                            descargadas += 1
                            print(f"   ✅ Descargada: {imagen_url[:60]}...")
                            break
            else:
                fallidas += 1
                print(f"   ❌ Error descargando")
        else:
            fallidas += 1
            print(f"   ⚠️ No se encontró imagen")
    
    # Guardar TOP.json actualizado
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Descargadas: {descargadas}")
    print(f"   ❌ Fallidas: {fallidas}")
    print(f"   📁 Total: {len(incorrectas)}")

if __name__ == "__main__":
    main()
