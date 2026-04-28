"""
Script para corregir géneros en TOP.json usando el archivo nuevo1.txt
Formato del archivo:
- Línea impar: Nombre de serie (a veces con año entre paréntesis)
- Línea par: Géneros separados por comas
"""

import json
import re
from pathlib import Path

def limpiar_nombre(nombre):
    """Limpia el nombre de la serie para facilitar la búsqueda"""
    # Quitar etiquetas como [Activo], [Dual-Audio], etc.
    nombre = re.sub(r'\[.*?\]', '', nombre)
    # Quitar información técnica entre paréntesis al final
    nombre = re.sub(r'\s*\([^)]*\)\s*$', '', nombre)
    # Limpiar espacios extras
    nombre = nombre.strip()
    return nombre

def normalizar_nombre(nombre):
    """Normaliza el nombre para comparación"""
    # Quitar año entre paréntesis
    nombre = re.sub(r'\s*\(\d{4}\)\s*', ' ', nombre)
    # Convertir a minúsculas
    nombre = nombre.lower()
    # Quitar caracteres especiales
    nombre = re.sub(r'[^a-z0-9\s]', '', nombre)
    # Normalizar espacios
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    return nombre

def parsear_archivo_correcciones(ruta_archivo):
    """Parsea el archivo de correcciones y devuelve un diccionario"""
    correcciones = {}
    
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        lineas = [linea.strip() for linea in f.readlines() if linea.strip()]
    
    # Procesar de dos en dos (nombre, géneros)
    i = 0
    while i < len(lineas):
        nombre_serie = lineas[i]
        if i + 1 < len(lineas):
            generos = lineas[i + 1]
            correcciones[nombre_serie] = generos
        i += 2
    
    return correcciones

def buscar_y_actualizar(top_data, correcciones):
    """Busca coincidencias y actualiza los géneros"""
    actualizaciones = 0
    no_encontrados = []
    
    # Para cada corrección
    for nombre_corr, generos_corr in correcciones.items():
        # Extraer año si existe en el nombre de corrección
        year_match = re.search(r'\((\d{4})\)', nombre_corr)
        year_corr = int(year_match.group(1)) if year_match else None
        
        # Normalizar nombre de corrección
        nombre_corr_norm = normalizar_nombre(nombre_corr)
        
        encontrado = False
        
        # Buscar en todas las categorías
        for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
            if categoria not in top_data:
                continue
                
            for item in top_data[categoria]:
                if 'name' not in item:
                    continue
                    
                nombre_item = item['name']
                nombre_item_limpio = limpiar_nombre(nombre_item)
                nombre_item_norm = normalizar_nombre(nombre_item_limpio)
                
                # Verificar coincidencia
                coincidencia = False
                
                # Coincidencia exacta normalizada
                if nombre_item_norm == nombre_corr_norm:
                    coincidencia = True
                # Coincidencia parcial (si el nombre de corrección está contenido)
                elif nombre_corr_norm in nombre_item_norm or nombre_item_norm in nombre_corr_norm:
                    # Verificar año si está disponible
                    if year_corr and item.get('year'):
                        if abs(item['year'] - year_corr) <= 1:
                            coincidencia = True
                    else:
                        coincidencia = True
                
                if coincidencia:
                    # Actualizar géneros
                    item['specificGenre'] = generos_corr
                    item['genre'] = generos_corr.split(',')[0].strip()  # Primer género como género principal
                    actualizaciones += 1
                    print(f"✅ Actualizado: {nombre_item_limpio} -> {generos_corr}")
                    encontrado = True
                    break
            
            if encontrado:
                break
        
        if not encontrado:
            no_encontrados.append(nombre_corr)
    
    return actualizaciones, no_encontrados

def main():
    ruta_correcciones = Path(r'c:\Users\Rafael\Desktop\nuevo1.txt')
    ruta_top = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
    ruta_backup = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP_backup_generos.json')
    
    # Verificar archivos
    if not ruta_correcciones.exists():
        print(f"❌ No se encontró el archivo de correcciones: {ruta_correcciones}")
        return
    
    if not ruta_top.exists():
        print(f"❌ No se encontró el archivo TOP.json: {ruta_top}")
        return
    
    # Cargar TOP.json
    print("📂 Cargando TOP.json...")
    with open(ruta_top, 'r', encoding='utf-8') as f:
        top_data = json.load(f)
    
    # Crear backup
    print("💾 Creando backup...")
    with open(ruta_backup, 'w', encoding='utf-8') as f:
        json.dump(top_data, f, indent=2, ensure_ascii=False)
    
    # Parsear correcciones
    print("📖 Parseando archivo de correcciones...")
    correcciones = parsear_archivo_correcciones(ruta_correcciones)
    print(f"   Encontradas {len(correcciones)} correcciones")
    
    # Buscar y actualizar
    print("🔍 Buscando coincidencias y actualizando...")
    actualizaciones, no_encontrados = buscar_y_actualizar(top_data, correcciones)
    
    # Guardar cambios
    print("💾 Guardando cambios...")
    with open(ruta_top, 'w', encoding='utf-8') as f:
        json.dump(top_data, f, indent=2, ensure_ascii=False)
    
    # Resultados
    print("\n" + "="*60)
    print(f"✅ Actualizaciones completadas: {actualizaciones}/{len(correcciones)}")
    
    if no_encontrados:
        print(f"\n⚠️  No se encontraron {len(no_encontrados)} series:")
        for nombre in no_encontrados:
            print(f"   - {nombre}")
    
    print(f"\n💾 Backup guardado en: {ruta_backup}")
    print("="*60)

if __name__ == "__main__":
    main()
