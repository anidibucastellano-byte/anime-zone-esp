#!/usr/bin/env python3
"""
Script de prueba para extraer el nombre del capítulo de un video específico
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️  Whisper no instalado. Ejecuta: pip install openai-whisper")

# CONFIGURACIÓN - Modifica estas rutas si es necesario
VIDEO_PATH = Path(r"C:\Users\Rafael\Downloads\Telegram Desktop\Miles del futuro\001_Miles del Futuro.mp4")

# Si ffmpeg no se encuentra automáticamente, especifica la ruta aquí:
# Ejemplo: FFMPEG_MANUAL = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_MANUAL = r"C:\Users\Rafael\CascadeProjects\windsurf-project\ffmpeg-2026-05-11-git-17bc88e67f-essentials_build\bin\ffmpeg.exe"

# Añadir ffmpeg al PATH para que Whisper lo encuentre
if FFMPEG_MANUAL and os.path.exists(FFMPEG_MANUAL):
    ffmpeg_dir = os.path.dirname(FFMPEG_MANUAL)
    if ffmpeg_dir not in os.environ['PATH']:
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']
        print(f"✅ Añadido ffmpeg al PATH: {ffmpeg_dir}")

def encontrar_ffmpeg():
    """Busca ffmpeg en el sistema"""
    # Si hay ruta manual configurada, usarla primero
    if FFMPEG_MANUAL and os.path.exists(FFMPEG_MANUAL):
        return FFMPEG_MANUAL
    
    # Primero intentar con shutil.which (busca en PATH)
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    # Buscar en ubicaciones comunes de Windows
    ubicaciones_comunes = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        r"C:\Users\%USERNAME%\ffmpeg\bin\ffmpeg.exe",
        r"C:\Windows\System32\ffmpeg.exe",
    ]
    
    for ubicacion in ubicaciones_comunes:
        # Expandir variables de entorno
        ubicacion = os.path.expandvars(ubicacion)
        if os.path.exists(ubicacion):
            return ubicacion
    
    return None

def verificar_ffmpeg():
    """Verifica si ffmpeg está disponible"""
    return encontrar_ffmpeg() is not None

def instalar_ffmpeg_windows():
    """Instrucciones para instalar ffmpeg en Windows"""
    print("\n📦 FFMPEG NO ENCONTRADO")
    print("="*60)
    print("Opción 1 - Instalación rápida con Chocolatey:")
    print("   choco install ffmpeg")
    print("\nOpción 2 - Descarga manual:")
    print("   1. Descarga de https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z")
    print("   2. Extrae en C:\\ffmpeg")
    print("   3. Añade C:\\ffmpeg\\bin al PATH de Windows")
    print("\nOpción 3 - Usar Python (instala estos paquetes):")
    print("   pip install ffmpeg-python pydub")
    print("="*60)
    return False

def extraer_audio_alternativo(video_path, duracion=60):
    """Extrae audio usando pydub como alternativa"""
    try:
        from pydub import AudioSegment
        
        print("   🔄 Intentando con pydub...")
        audio_temp = video_path.parent / f"{video_path.stem}_temp.wav"
        
        # Cargar video como audio
        audio = AudioSegment.from_file(str(video_path), format="mp4")
        
        # Cortar a la duración deseada (en milisegundos)
        audio = audio[:duracion * 1000]
        
        # Exportar a WAV con configuración para Whisper
        audio.export(str(audio_temp), format="wav", 
                    parameters=["-ac", "1", "-ar", "16000"])
        
        if audio_temp.exists():
            return audio_temp
    except Exception as e:
        print(f"   ❌ Error con pydub: {e}")
    
    return None

def extraer_audio(video_path, duracion=60):
    """Extrae los primeros N segundos de audio"""
    audio_temp = video_path.parent / f"{video_path.stem}_temp.wav"
    
    print(f"   📁 Audio temporal: {audio_temp}")
    print(f"   📹 Video fuente: {video_path}")
    print(f"   📹 Video existe: {video_path.exists()}")
    
    # Buscar ffmpeg
    ffmpeg_path = encontrar_ffmpeg()
    
    if not ffmpeg_path:
        print("⚠️  ffmpeg no encontrado en el sistema")
        # Intentar con método alternativo
        return extraer_audio_alternativo(video_path, duracion)
    
    print(f"   🎵 Usando ffmpeg: {ffmpeg_path}")
    print(f"   🎵 ffmpeg existe: {os.path.exists(ffmpeg_path)}")
    
    cmd = [
        ffmpeg_path, '-y', '-i', str(video_path),
        '-t', str(duracion),
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        '-ac', '1',
        str(audio_temp)
    ]
    
    print(f"   🔧 Comando: {' '.join(cmd[:5])}...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        print(f"   📊 ffmpeg return code: {result.returncode}")
        
        if result.returncode != 0:
            error_msg = result.stderr.decode() if result.stderr else "Sin error"
            print(f"   ⚠️  ffmpeg error: {error_msg[:300]}")
        
        print(f"   📁 Audio existe después de ffmpeg: {audio_temp.exists()}")
        
        if audio_temp.exists():
            print(f"   📊 Tamaño del audio: {audio_temp.stat().st_size} bytes")
            return audio_temp
        else:
            print("   ❌ El archivo de audio no se creó")
            
    except Exception as e:
        print(f"❌ Error con ffmpeg: {e}")
        import traceback
        traceback.print_exc()
        # Intentar método alternativo
        return extraer_audio_alternativo(video_path, duracion)
    
    return None

def transcribir_completo(audio_path, modelo="small"):  # Usar small para mejor precisión
    """Transcribe todo el audio"""
    try:
        # Verificar que el archivo existe
        audio_path = Path(audio_path)
        print(f"🔍 Verificando audio: {audio_path}")
        print(f"🔍 Audio existe: {audio_path.exists()}")
        print(f"🔍 Audio es archivo: {audio_path.is_file()}")
        
        if not audio_path.exists():
            print(f"❌ El archivo de audio no existe: {audio_path}")
            return None
        
        print(f"🎙️  Cargando modelo {modelo}...")
        model = whisper.load_model(modelo)
        
        print("📝 Transcribiendo (puede tardar unos segundos)...")
        result = model.transcribe(str(audio_path), language='es', verbose=False)
        
        return result['text']
    except Exception as e:
        print(f"❌ Error en transcribir_completo: {e}")
        import traceback
        traceback.print_exc()
        return None

def buscar_con_typos(texto, palabra_base):
    """Busca una palabra permitiendo errores comunes de transcripción"""
    texto_lower = texto.lower()
    
    # Mapeo de variantes comunes de errores de Whisper
    variantes = {
        'lanzadera': ['lanzadera', 'unzadera', 'lansadera', 'lansader', 'zadera', 'lanza'],
        'deriva': ['deriva', 'alaveriva', 'la deriva', 'aderiva', 'deriba'],
        'surf': ['surf', 'serf', 'surff'],
        'remolino': ['remolino', 'remolina', 'remolín', 'molino'],
        'hermanos': ['hermanos', 'ermanos', 'ermanitos'],
        'callisto': ['callisto', 'calisto', 'kalisto'],
        'estación': ['estación', 'estacion', 'esta ción'],
        'espacial': ['espacial', 'espasial', 'especial'],
        'caballero': ['caballero', 'cabayero', 'caballero'],
        'nocturno': ['nocturno', 'noctuno', 'nocturn'],
        'relámpago': ['relámpago', 'relampago', 'relampo'],
    }
    
    if palabra_base in variantes:
        for variante in variantes[palabra_base]:
            if variante in texto_lower:
                return variante
    
    return None

def extraer_titulo_mejorado(texto):
    """Versión mejorada para extraer títulos de capítulos de Miles del futuro"""
    if not texto:
        return None
    
    print(f"\n{'='*60}")
    print("TEXTO COMPLETO TRANSCRITO:")
    print(f"{'='*60}")
    print(texto[:800])  # Mostrar más caracteres
    print("...")
    print(f"{'='*60}\n")
    
    # Buscar combinaciones de títulos con tolerancia a errores
    titulos_compuestos = [
        ('lanzadera', 'deriva'),
        ('surf', 'remolino'),
        ('hermanos', 'callisto'),
        ('visita', 'estación'),
        ('mercurio', ''),
        ('runaway', ''),
        ('relámpago', ''),
        ('jet', ''),
        ('caballero', 'nocturno'),
        ('planeta', 'tierra'),
        ('mamá', 'callisto'),
    ]
    
    print("🔍 Buscando títulos compuestos (con tolerancia a errores)...")
    for parte1, parte2 in titulos_compuestos:
        found1 = buscar_con_typos(texto, parte1)
        if found1:
            if parte2:
                found2 = buscar_con_typos(texto, parte2)
                if found2:
                    # Encontrar el contexto completo
                    texto_lower = texto.lower()
                    idx1 = texto_lower.find(found1)
                    idx2 = texto_lower.find(found2)
                    
                    if idx1 >= 0 and idx2 >= 0:
                        # Extraer desde el inicio de la frase hasta el final
                        inicio = max(0, min(idx1, idx2) - 10)
                        fin = min(len(texto), max(idx1 + len(found1), idx2 + len(found2)) + 20)
                        contexto = texto[inicio:fin]
                        
                        print(f"   🎯 Encontrado '{parte1}' + '{parte2}': {contexto}")
                        
                        # Limpiar y construir título
                        titulo = re.sub(r'[^\w\s\-áéíóúñ]', '', contexto).strip()
                        titulo = re.sub(r'\s+', ' ', titulo)  # Normalizar espacios
                        
                        # Capitalizar correctamente
                        titulo = titulo.title()
                        
                        if 10 < len(titulo) < 60:
                            print(f"   ✅ Título compuesto extraído: '{titulo}'")
                            return titulo
            else:
                # Solo una parte (título simple)
                texto_lower = texto.lower()
                idx = texto_lower.find(found1)
                if idx >= 0:
                    inicio = max(0, idx - 20)
                    fin = min(len(texto), idx + len(found1) + 20)
                    contexto = texto[inicio:fin]
                    print(f"   🎯 Encontrado '{parte1}': {contexto}")
                    
                    titulo = re.sub(r'[^\w\s\-áéíóúñ]', '', contexto).strip()
                    titulo = titulo.title()
                    if 5 < len(titulo) < 50:
                        print(f"   ✅ Título simple extraído: '{titulo}'")
                        return titulo
    
    # Buscar frases que comiencen con "la" + palabra clave (ej: "La lanzadera...")
    print("🔍 Buscando frases con artículo...")
    frases_la = re.findall(r'la\s+([a-záéíóúñ\s]{5,35})(?:\.|!|\?|$|\n)', texto.lower())
    for frase in frases_la:
        frase_clean = frase.strip()
        # Verificar si contiene palabras de títulos
        palabras_titulo = ['lanzadera', 'unzadera', 'zadera', 'hermanos', 'callisto', 'estación', 
                          'planeta', 'nave', 'caballero', 'relámpago']
        if any(p in frase_clean for p in palabras_titulo):
            titulo = re.sub(r'[^\w\s\-áéíóúñ]', '', frase_clean).strip()
            titulo = titulo.title()
            if 10 < len(titulo) < 50:
                print(f"   ✅ Título con artículo: 'La {titulo}'")
                return f"La {titulo}"
    
    # Último recurso: buscar líneas que contengan palabras clave
    lineas = texto.split('\n')
    for linea in lineas:
        linea_lower = linea.lower()
        # Palabras que indican título
        indicadores = ['lanzadera', 'unzadera', 'zadera', 'surf', 'remolino',
                      'hermanos', 'callisto', 'estación', 'planeta', 'nave', 
                      'caballero', 'relámpago', 'mercurio']
        if any(ind in linea_lower for ind in indicadores):
            if 15 < len(linea) < 60:
                # Limpiar
                titulo = re.sub(r'[^\w\s\-áéíóúñ]', '', linea).strip()
                titulo = re.sub(r'\s+', ' ', titulo).strip()
                titulo = titulo.title()
                if len(titulo) > 5:
                    print(f"   ✅ Título encontrado por palabra clave: '{titulo}'")
                    return titulo
    
    return None

def corregir_con_titulos_reales(texto_crudo):
    """Corregir el título transcrito comparando con títulos reales de la serie"""
    # Lista de títulos reales de "Miles del futuro" (Temporadas 1 y 2)
    titulos_reales = [
        # Temporada 1
        "Lanzadera a la deriva",
        "Surf en el remolino",
        "Los Hermanos Callisto", 
        "Visita a la estación espacial",
        "Mamá Callisto",
        "El dia libre de Miles",
        "El Universo de Miles",
        "Runaway",
        "Mercurio",
        "Un Día Galáctico",
        "Relámpago",
        "Blastboard",
        "Planeta Tierra",
        "Caballero Nocturno",
        "Equipo Galáctico",
        "Exploradores espaciales",
        "Detectives espaciales",
        "La Nueva Nave",
        "Carrera Espacial",
        "El Planeta Unicornio",
        "Adventura en el Planeta Ice",
        "El Planeta Tierra",
        "La Expedición al Planeta",
        # Temporada 2 - añade más según tengas
        "El Planeta Burbuja",
        "Misión Planeta",
        "La Estación Espacial",
        # Añade más títulos según tus capítulos
    ]
    
    print("\n🔧 Corrigiendo con títulos reales...")
    
    # Normalizar texto transcrito
    texto_lower = texto_crudo.lower()
    
    # Buscar coincidencias aproximadas
    mejor_coincidencia = None
    mejor_puntuacion = 0
    
    for titulo_real in titulos_reales:
        puntuacion = 0
        palabras_titulo = titulo_real.lower().split()
        
        for palabra in palabras_titulo:
            # Buscar variantes de la palabra
            variante = buscar_con_typos(texto_crudo, palabra)
            if variante:
                puntuacion += 1
        
        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_coincidencia = titulo_real
    
    if mejor_coincidencia and mejor_puntuacion >= 2:
        print(f"   ✅ Corregido a título real: '{mejor_coincidencia}'")
        return mejor_coincidencia
    
    return None

def limpiar_titulo(texto):
    """Limpia un título transcrito eliminando palabras irrelevantes"""
    # Palabras a eliminar
    palabras_irrelevantes = [
        'futuro', 'listo', 'para', 'abatir', 'más', 'miles', 
        'hoy', 'presentamos', 'capítulo', 'episodio', 'nuestros',
        'records', 'de', 'velocidad', 'activando', 'modo', 'carrera'
    ]
    
    # Separar en palabras
    palabras = texto.lower().split()
    
    # Filtrar
    palabras_filtradas = [p for p in palabras if p not in palabras_irrelevantes]
    
    # Reconstruir
    resultado = ' '.join(palabras_filtradas).strip()
    
    # Limpiar caracteres
    resultado = re.sub(r'[^\w\s\-áéíóúñ]', '', resultado)
    resultado = re.sub(r'\s+', ' ', resultado).strip()
    
    return resultado.title()

def procesar_video_individual(video_path, modelo="small"):
    """Procesa un solo video y retorna el título extraído"""
    print(f"\n{'='*70}")
    print(f"📹 PROCESANDO: {video_path.name}")
    print(f"{'='*70}")
    
    if not video_path.exists():
        print(f"❌ No se encuentra el video")
        return None
    
    # Extraer audio - 3 minutos para saltar la intro y capturar el diálogo
    print("🔊 Extrayendo audio (primeros 3 minutos)...")
    audio_temp = extraer_audio(video_path, duracion=180)
    
    if not audio_temp:
        print("❌ No se pudo extraer audio")
        return None
    
    try:
        # Transcribir
        texto = transcribir_completo(audio_temp, modelo=modelo)
        
        # Borrar audio temporal
        audio_temp.unlink()
        
        if not texto:
            print("❌ No se pudo transcribir")
            return None
        
        # Intentar extraer título
        titulo = extraer_titulo_mejorado(texto)
        
        # Si encontramos un título, intentar corregirlo
        if titulo:
            # Intentar corregir con títulos reales
            titulo_corregido = corregir_con_titulos_reales(texto)
            if titulo_corregido:
                titulo = titulo_corregido
            else:
                # Limpiar palabras irrelevantes
                titulo = limpiar_titulo(titulo)
        
        if titulo:
            print(f"✅ TÍTULO FINAL: '{titulo}'")
            return titulo
        else:
            print("❌ No se pudo extraer el título")
            return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if audio_temp.exists():
            audio_temp.unlink()
        return None

def main():
    print("="*70)
    print("🧪 EXTRACCIÓN DE TÍTULOS - MILES DEL FUTURO")
    print("="*70)
    
    if not WHISPER_AVAILABLE:
        print("❌ Whisper no está instalado")
        print("📝 Ejecuta: pip install openai-whisper")
        return
    
    # Buscar carpeta del video
    carpeta_videos = VIDEO_PATH.parent if VIDEO_PATH.exists() else Path('.')
    
    print(f"\n📁 Buscando videos en: {carpeta_videos}")
    
    # Buscar todos los videos MP4
    videos = sorted(carpeta_videos.glob('*.mp4'))
    
    if not videos:
        print("❌ No se encontraron videos MP4")
        print(f"⚠️  Verifica que hay videos en: {carpeta_videos}")
        return
    
    print(f"🎬 Encontrados {len(videos)} videos")
    
    # Preguntar si procesar todos o uno específico
    print("\nOpciones:")
    print("   1 - Procesar TODOS los videos")
    print("   2 - Procesar solo el video de prueba (001_Miles del Futuro.mp4)")
    
    opcion = input("\nElige opción (1): ").strip() or "1"
    
    if opcion == "2":
        videos = [VIDEO_PATH] if VIDEO_PATH.exists() else videos[:1]
    
    # Procesar videos
    resultados = []
    for i, video in enumerate(videos, 1):
        print(f"\n\n[{i}/{len(videos)}] ", end="")
        titulo = procesar_video_individual(video, modelo="small")
        resultados.append((video.name, titulo))
    
    # Resumen final
    print(f"\n\n{'='*70}")
    print("📊 RESUMEN FINAL")
    print(f"{'='*70}")
    
    exitosos = sum(1 for _, t in resultados if t)
    print(f"✅ Exitosos: {exitosos}/{len(resultados)}")
    print()
    
    for nombre, titulo in resultados:
        estado = "✅" if titulo else "❌"
        titulo_str = f" - '{titulo}'" if titulo else " - Sin título"
        print(f"{estado} {nombre}{titulo_str}")
    
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
