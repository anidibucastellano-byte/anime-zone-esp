#!/usr/bin/env python3
"""
Repara imágenes que se extrajeron mal (emojis, logos, etc.)
"""
import json
import os
from extraer_imagenes_foro import ForoImageExtractor

FORO_URL = "https://animezoneesp.foroactivo.com"
LOGIN_URL = f"{FORO_URL}/login"

# Patrones de URLs malas
URLS_MALAS = [
    'herz.png', 'smiles', '2img.net', 'servimg.com/u/f', 'icon', 'emoji',
    'sinopsis', 'ficha_tecnica', 'portad', 'logo'
]

def es_url_mala(url):
    """Verificar si una URL es mala"""
    if not url:
        return True
    url_lower = url.lower()
    return any(mala in url_lower for mala in URLS_MALAS)

def safe_filename(nombre):
    """Crear nombre de archivo seguro"""
    import re
    # Remover caracteres no seguros para archivos
    nombre = re.sub(r'[<>:"/\\|?*]', '', nombre)
    nombre = nombre[:80]  # Limitar longitud
    return nombre.strip()

def main():
    # Cargar TOP.json
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Encontrar items con imágenes malas
    items_malos = []
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        for item in data.get(categoria, []):
            url_imagen = item.get('imagen_url', '')
            if es_url_mala(url_imagen):
                items_malos.append({
                    'categoria': categoria,
                    'item': item
                })
    
    print(f"🔍 Encontradas {len(items_malos)} imágenes malas para reparar")
    
    if not items_malos:
        print("✅ No hay imágenes malas que reparar")
        return
    
    # Inicializar extractor
    extractor = ForoImageExtractor()
    
    # Login
    login_data = {
        'username': 'Admin',
        'password': '9XsBiygA2CpqgB9',
        'login': '1'
    }
    extractor.session.post(LOGIN_URL, data=login_data)
    print("✅ Login exitoso")
    
    # Reparar cada imagen mala
    reparadas = 0
    for info in items_malos:
        item = info['item']
        categoria = info['categoria']
        nombre = item.get('nombre', item.get('name', 'Sin nombre'))
        url_tema = item.get('url', '')
        
        print(f"\n🔄 Reparando: {nombre}")
        print(f"   URL anterior mala: {item.get('imagen_url', 'N/A')[:60]}...")
        
        if not url_tema:
            print("   ❌ No tiene URL de tema")
            continue
        
        # Extraer nueva imagen
        nueva_url = extractor.extraer_imagen_de_tema(url_tema)
        
        if nueva_url and not es_url_mala(nueva_url):
            # Descargar nueva imagen
            safe_name = safe_filename(nombre)
            ext = '.png' if 'png' in nueva_url.lower() else '.jpg'
            filename = f"{categoria}_{item.get('id', '')}_{safe_name}{ext}"
            filepath = os.path.join('images', filename)
            
            if extractor.descargar_imagen(nueva_url, filepath):
                # Actualizar item
                item['imagen_url'] = nueva_url
                item['imagen'] = filepath.replace('\\', '/')
                reparadas += 1
                print(f"   ✅ Reparada: {nueva_url[:60]}...")
            else:
                print(f"   ❌ Error descargando nueva imagen")
        else:
            print(f"   ⚠️ No se encontró imagen válida (nueva: {nueva_url})")
    
    # Guardar TOP.json actualizado
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 TOP.json guardado")
    print(f"📊 Total reparadas: {reparadas}/{len(items_malos)}")

if __name__ == "__main__":
    main()
