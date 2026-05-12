#!/usr/bin/env python3
"""
Renombrador automático de videos de "Miles del futuro"
Extrae el título del audio usando Whisper y renombra con formato [S01.E01]
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from time import sleep

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# ============ CONFIGURACIÓN ============
# Ajusta estas rutas según tu sistema
FFMPEG_PATH = r"C:\Users\Rafael\CascadeProjects\windsurf-project\ffmpeg-2026-05-11-git-17bc88e67f-essentials_build\bin\ffmpeg.exe"
CARPETA_VIDEOS = r"C:\Users\Rafael\Downloads\Telegram Desktop\Miles del futuro"

# Añadir ffmpeg al PATH si existe
if os.path.exists(FFMPEG_PATH):
    ffmpeg_dir = os.path.dirname(FFMPEG_PATH)
    if ffmpeg_dir not in os.environ['PATH']:
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']

# Lista de títulos reales de Miles del futuro
TITULOS_REALES = [
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
    "La Expedición al Planeta",
    "El Planeta Burbuja",
    "Misión Planeta",
    "La Estación Espacial",
    "Galáctico",
    "Jet",
    # Añade más según tus capítulos
]

# ============ FUNCIONES ============

def instalar_whisper():
    """Instala whisper"""
    print("📦 Instalando Whisper...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-U', 'openai-whisper'], 
                      capture_output=True, timeout=120)
        print("✅ Whisper instalado. Reinicia el script.")
        return True
    except:
        print("❌ Error al instalar Whisper")
        return False

def extraer_audio(video_path, duracion=180):
    """Extrae audio del video (3 minutos para saltar la intro)"""
    audio_temp = video_path.parent / f"{video_path.stem}_temp.wav"
    
    ffmpeg_exe = FFMPEG_PATH if os.path.exists(FFMPEG_PATH) else 'ffmpeg'
    
    cmd = [
        ffmpeg_exe, '-y', '-i', str(video_path),
        '-t', str(duracion),
        '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
        str(audio_temp)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=60)
        if audio_temp.exists():
            return audio_temp
    except Exception as e:
        print(f"   ❌ Error extrayendo audio: {e}")
    
    return None

def transcribir(audio_path, modelo="small"):
    """Transcribe audio con Whisper"""
    try:
        print(f"   🎙️  Transcribiendo...")
        model = whisper.load_model(modelo)
        result = model.transcribe(str(audio_path), language='es', verbose=False)
        return result['text']
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def buscar_con_typos(texto, palabra_base):
    """Busca palabra con tolerancia a errores de transcripción"""
    variantes = {
        'lanzadera': ['lanzadera', 'unzadera', 'lansadera', 'zadera', 'lanza'],
        'deriva': ['deriva', 'alaveriva', 'la deriva', 'aderiva'],
        'surf': ['surf', 'serf', 'surf'],
        'remolino': ['remolino', 'remolina', 'remolín'],
        'hermanos': ['hermanos', 'ermanos', 'ermanitos'],
        'callisto': ['callisto', 'calisto', 'kalisto'],
        'estación': ['estación', 'estacion', 'esta ción'],
        'espacial': ['espacial', 'espasial', 'especial'],
        'planeta': ['planeta', 'planetta', 'planeta'],
        'galáctico': ['galáctico', 'galactico', 'galactiko'],
        'caballero': ['caballero', 'cabayero'],
        'nocturno': ['nocturno', 'noctuno'],
        'relámpago': ['relámpago', 'relampago'],
        'mercurio': ['mercurio', 'merkuri'],
    }
    
    texto_lower = texto.lower()
    if palabra_base in variantes:
        for variante in variantes[palabra_base]:
            if variante in texto_lower:
                return variante
    return None

def corregir_titulo(texto_transcrito):
    """Encuentra el título real más cercano"""
    mejor_match = None
    mejor_puntuacion = 0
    
    for titulo_real in TITULOS_REALES:
        puntuacion = 0
        palabras = titulo_real.lower().split()
        
        for palabra in palabras:
            if buscar_con_typos(texto_transcrito, palabra):
                puntuacion += 1
        
        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_match = titulo_real
    
    # Necesita al menos 2 palabras coincidentes
    if mejor_match and mejor_puntuacion >= 2:
        return mejor_match
    
    return None

def extraer_titulo(texto):
    """Extrae y corrige el título del texto transcrito"""
    if not texto:
        return None
    
    # Intentar corrección con títulos reales
    titulo = corregir_titulo(texto)
    if titulo:
        return titulo
    
    # Si no hay coincidencia, intentar extraer línea con palabras clave
    lineas = texto.split('\n')
    for linea in lineas:
        linea_lower = linea.lower()
        palabras_clave = ['lanzadera', 'surf', 'remolino', 'hermanos', 'callisto', 
                          'estación', 'planeta', 'nave', 'caballero', 'relámpago', 'mercurio']
        if any(p in linea_lower for p in palabras_clave):
            if 10 < len(linea) < 60:
                return re.sub(r'[^\w\s\-áéíóúñ]', '', linea).strip().title()
    
    return None

def renombrar_video(video_path, titulo, num_episodio, nombre_serie="Miles del Futuro", tag="AzE"):
    """Renombra el video con el formato [S01.E01]"""
    try:
        nuevo_nombre = f"[S01.E{num_episodio:02d}] {nombre_serie} - {titulo} [{tag}]"
        nuevo_nombre = re.sub(r'[<>:"/\\|?*]', '', nuevo_nombre)
        
        nuevo_path = video_path.parent / f"{nuevo_nombre}{video_path.suffix}"
        
        # Evitar sobrescribir
        contador = 1
        while nuevo_path.exists():
            nuevo_nombre = f"[S01.E{num_episodio:02d}] {nombre_serie} - {titulo} ({contador}) [{tag}]"
            nuevo_path = video_path.parent / f"{nuevo_nombre}{video_path.suffix}"
            contador += 1
        
        video_path.rename(nuevo_path)
        return nuevo_path
    except Exception as e:
        print(f"   ❌ Error al renombrar: {e}")
        return None

def detectar_numero_episodio(nombre_archivo):
    """Extrae número de episodio del nombre del archivo"""
    patrones = [
        r'(\d{2,3})\s*[_\-\.]',
        r'[ep|cap]?\s*(\d{1,2})',
        r'^(\d{1,3})',
    ]
    for patron in patrones:
        match = re.search(patron, nombre_archivo.lower())
        if match:
            return int(match.group(1))
    return None

def procesar_video(video_path, num_episodio):
    """Procesa un video completo"""
    print(f"\n{'='*70}")
    print(f"📹 {video_path.name}")
    print(f"{'='*70}")
    
    # Detectar número del nombre si no se proporcionó
    num_detectado = detectar_numero_episodio(video_path.name)
    if num_detectado:
        num_episodio = num_detectado
    
    print(f"   🔢 Episodio: {num_episodio:02d}")
    
    # Extraer audio
    audio_temp = extraer_audio(video_path)
    if not audio_temp:
        print("   ❌ Falló extracción de audio")
        return False, num_episodio
    
    # Transcribir
    texto = transcribir(audio_temp)
    audio_temp.unlink()
    
    if not texto:
        print("   ❌ Falló transcripción")
        return False, num_episodio
    
    # Extraer título
    titulo = extraer_titulo(texto)
    
    if titulo:
        print(f"   ✅ Título: '{titulo}'")
        
        # Renombrar
        nuevo = renombrar_video(video_path, titulo, num_episodio)
        if nuevo:
            print(f"   📁 Renombrado a: {nuevo.name}")
            return True, num_episodio
    else:
        print("   ⚠️  No se detectó título, usando genérico")
        nuevo = renombrar_video(video_path, f"Capitulo {num_episodio}", num_episodio)
        if nuevo:
            return True, num_episodio
    
    return False, num_episodio

def main():
    print("="*70)
    print("🎬 RENOMBRADOR AUTOMÁTICO - MILES DEL FUTURO")
    print("   Formato: [S01.E01] Miles del Futuro - Título [AzE]")
    print("="*70)
    
    if not WHISPER_AVAILABLE:
        print("⚠️  Whisper no instalado")
        if input("¿Instalar ahora? (s/n): ").lower() == 's':
            if instalar_whisper():
                return
        return
    
    # Buscar videos
    carpeta = Path(CARPETA_VIDEOS)
    if not carpeta.exists():
        print(f"❌ Carpeta no existe: {carpeta}")
        carpeta = Path(input("Introduce ruta de la carpeta con videos: ") or ".")
    
    videos = sorted(carpeta.glob('*.mp4'))
    
    if not videos:
        print("❌ No se encontraron videos MP4")
        return
    
    print(f"\n📁 Carpeta: {carpeta}")
    print(f"🎬 Videos encontrados: {len(videos)}")
    
    # Configuración
    tag = input("\nTag [AzE]: ").strip() or "AzE"
    ep_inicio = input("Número de episodio inicial [1]: ").strip()
    num_ep = int(ep_inicio) if ep_inicio.isdigit() else 1
    
    print(f"\n{'='*70}")
    print("PROCESANDO VIDEOS...")
    print(f"{'='*70}")
    
    resultados = []
    for video in videos:
        ok, num_usado = procesar_video(video, num_ep)
        resultados.append((video.name, ok, num_usado))
        num_ep = num_usado + 1
        sleep(1)
    
    # Resumen
    print(f"\n{'='*70}")
    print("📊 RESUMEN")
    print(f"{'='*70}")
    
    exitosos = sum(1 for _, ok, _ in resultados if ok)
    print(f"✅ Exitosos: {exitosos}/{len(resultados)}\n")
    
    for nombre, ok, num in resultados:
        print(f"{'✅' if ok else '❌'} Ep {num:02d}: {nombre}")
    
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
