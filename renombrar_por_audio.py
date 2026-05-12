#!/usr/bin/env python3
"""
Renombra videos de "Miles del futuro" extrayendo el nombre del capítulo del audio
Usa Whisper de OpenAI para transcribir los primeros segundos
"""
import os
import re
import subprocess
import sys
from pathlib import Path
from glob import glob

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

def instalar_whisper():
    """Instala whisper y sus dependencias"""
    print("📦 Instalando Whisper...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-U', 'openai-whisper'], 
                      capture_output=True, timeout=120)
        print("✅ Whisper instalado. Reinicia el script.")
        return True
    except Exception as e:
        print(f"❌ Error al instalar: {e}")
        print("📝 Instala manualmente: pip install openai-whisper")
        return False

def extraer_audio(video_path, duracion=45):
    """Extrae los primeros N segundos de audio del video"""
    audio_temp = video_path.with_suffix('.wav')
    
    cmd = [
        'ffmpeg', '-y', '-i', str(video_path),
        '-t', str(duracion),  # Primeros N segundos
        '-vn',  # Sin video
        '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian
        '-ar', '16000',  # Sample rate 16kHz (recomendado para Whisper)
        '-ac', '1',  # Mono
        str(audio_temp)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=60)
        if audio_temp.exists():
            return audio_temp
    except Exception as e:
        print(f"   ❌ Error extrayendo audio: {e}")
    
    return None

def transcribir_audio(audio_path, modelo="base"):
    """Transcribe audio usando Whisper"""
    try:
        # Cargar modelo (tiny, base, small, medium, large)
        print(f"   🎙️  Transcribiendo con modelo {modelo}...")
        model = whisper.load_model(modelo)
        
        result = model.transcribe(str(audio_path), language='es')
        texto = result['text'].strip()
        
        return texto
    except Exception as e:
        print(f"   ❌ Error en transcripción: {e}")
        return None

def extraer_nombre_capitulo(texto):
    """Extrae el nombre del capítulo de la transcripción"""
    if not texto:
        return None
    
    # Normalizar texto
    texto = texto.lower()
    
    # Patrones comunes para "Miles del futuro"
    patrones = [
        # "miles del futuro" seguido de cualquier cosa hasta el final o pausa
        r'miles del futuro[,:]?\s*([^\.\n]{3,60})',
        # "capítulo" seguido de nombre
        r'cap[ií]tulo[\s\d]+([^\.\n]{3,60})',
        # "hoy" seguido de nombre del episodio
        r'hoy\s+(?:en\s+)?miles del futuro[,:]?\s*([^\.\n]{3,60})',
        # Buscar frases que suenan como títulos (después de introducción)
        r'(?:bienvenidos?|presentamos|hoy)[,:]?\s*([^\.\n]{3,60}miles[^\.\n]{0,40})',
    ]
    
    for patron in patrones:
        match = re.search(patron, texto)
        if match:
            titulo = match.group(1).strip()
            # Limpiar título
            titulo = re.sub(r'[^\w\s\-\'áéíóúñ]', '', titulo, flags=re.IGNORECASE)
            titulo = titulo.strip().title()
            if len(titulo) > 3:
                return titulo
    
    # Si no encontramos patrón específico, buscar líneas cortas que podrían ser títulos
    lineas = [l.strip() for l in texto.split('\n') if 10 < len(l.strip()) < 60]
    if lineas:
        # La primera línea de longitud media suele ser el título
        return lineas[0].title()
    
    return None

def detectar_numero_episodio(video_path):
    """Intenta detectar el número de episodio del nombre del archivo"""
    nombre = video_path.stem.lower()
    
    # Patrones comunes para números de episodio
    patrones = [
        r'[\s._-]?(\d{1,2})[\s._-]?\d{2}',  # S01E02 o 01x02
        r'ep(?:isodio)?[\s._-]?(\d{1,2})',
        r'cap(?:[ií]tulo)?[\s._-]?(\d{1,2})',
        r'\D(\d{1,2})\D',  # Números rodeados de no-dígitos
        r'^(\d{1,2})',  # Número al inicio
    ]
    
    for patron in patrones:
        match = re.search(patron, nombre)
        if match:
            return int(match.group(1))
    
    return None


def renombrar_video(video_path, nombre_serie, titulo_capitulo, num_episodio, tag="AzE"):
    """Renombra el archivo con formato [S01.E01] Serie - Capítulo [Tag]"""
    try:
        # Si no hay número de episodio, usar 0
        if num_episodio is None:
            num_episodio = 0
        
        # Construir nombre con formato [S01.E01] Serie - Capítulo [Tag]
        nuevo_nombre = f"[S01.E{num_episodio:02d}] {nombre_serie} - {titulo_capitulo} [{tag}]"
        
        # Limpiar caracteres inválidos para Windows
        nuevo_nombre = re.sub(r'[<>:"/\\|?*]', '', nuevo_nombre)
        nuevo_nombre = nuevo_nombre.strip()
        
        nuevo_path = video_path.parent / f"{nuevo_nombre}{video_path.suffix}"
        
        # Si ya existe, añadir número
        contador = 1
        base_nombre = nuevo_nombre
        while nuevo_path.exists():
            nuevo_nombre = f"{base_nombre} ({contador})"
            nuevo_path = video_path.parent / f"{nuevo_nombre}{video_path.suffix}"
            contador += 1
        
        video_path.rename(nuevo_path)
        return nuevo_path
    except Exception as e:
        print(f"   ❌ Error al renombrar: {e}")
        return None

def procesar_video(video_path, num_episodio, modelo_whisper="base", nombre_serie="Miles del Futuro", tag="AzE"):
    """Procesa un video completo: extrae audio, transcribe, renombra"""
    print(f"\n📹 Procesando: {video_path.name}")
    
    # Detectar número de episodio del nombre si no se proporcionó
    num_detectado = detectar_numero_episodio(video_path)
    if num_detectado is not None:
        num_episodio = num_detectado
        print(f"   🔢 Episodio detectado del nombre: {num_episodio:02d}")
    else:
        print(f"   🔢 Usando número de episodio: {num_episodio:02d}")
    
    # Extraer audio
    print("   🔊 Extrayendo audio (primeros 45 segundos)...")
    audio_temp = extraer_audio(video_path)
    if not audio_temp:
        print("   ❌ No se pudo extraer audio")
        return False, num_episodio
    
    try:
        # Transcribir
        texto = transcribir_audio(audio_temp, modelo_whisper)
        
        # Borrar audio temporal
        audio_temp.unlink()
        
        if not texto:
            print("   ❌ No se pudo transcribir")
            # Renombrar sin título
            nuevo_path = renombrar_video(video_path, nombre_serie, "Desconocido", num_episodio, tag)
            if nuevo_path:
                print(f"   ⚠️  Renombrado sin título: {nuevo_path.name}")
            return False, num_episodio
        
        print(f"   📝 Transcripción: {texto[:100]}...")
        
        # Extraer nombre del capítulo
        titulo = extraer_nombre_capitulo(texto)
        
        if titulo:
            print(f"   🎬 Título detectado: {titulo}")
            
            # Renombrar con formato [S01.E01] Serie - Capítulo [Tag]
            nuevo_path = renombrar_video(video_path, nombre_serie, titulo, num_episodio, tag)
            
            if nuevo_path:
                print(f"   ✅ Renombrado a: {nuevo_path.name}")
                return True, num_episodio
        else:
            print("   ⚠️  No se detectó título en el audio")
            print(f"   📝 Texto completo: {texto}")
            # Renombrar sin título detectado
            nuevo_path = renombrar_video(video_path, nombre_serie, "Sin Titulo", num_episodio, tag)
            if nuevo_path:
                print(f"   ⚠️  Renombrado sin título: {nuevo_path.name}")
                return True, num_episodio
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        if audio_temp.exists():
            audio_temp.unlink()
    
    return False, num_episodio

def main():
    print("="*60)
    print("🎬 RENOMBRADOR DE VIDEOS POR AUDIO - MILES DEL FUTURO")
    print("   Formato: [S01.E01] Serie - Capítulo [AzE]")
    print("="*60)
    
    # Verificar Whisper
    if not WHISPER_AVAILABLE:
        print("⚠️  Whisper no está instalado")
        if input("¿Instalar Whisper ahora? (s/n): ").lower() == 's':
            if instalar_whisper():
                return
        else:
            print("📝 Instala manualmente: pip install openai-whisper")
            return
    
    # Buscar videos MP4
    print("\n🔍 Buscando videos MP4...")
    videos = list(Path('.').glob('*.mp4'))
    
    if not videos:
        # Buscar en subcarpetas
        videos = list(Path('.').rglob('*.mp4'))
    
    if not videos:
        print("❌ No se encontraron videos MP4")
        return
    
    # Ordenar videos por nombre
    videos = sorted(videos, key=lambda v: v.name.lower())
    
    print(f"📁 Encontrados {len(videos)} videos")
    
    # Preguntar configuración
    print("\n📊 Modelos de Whisper disponibles:")
    print("   tiny   - Rápido, menos preciso")
    print("   base   - Equilibrado (recomendado)")
    print("   small  - Más preciso, más lento")
    print("   medium - Muy preciso, muy lento")
    
    modelo = input("\nElige modelo (base por defecto): ").strip() or "base"
    
    nombre_serie = input("Nombre de la serie (Miles del Futuro por defecto): ").strip()
    if not nombre_serie:
        nombre_serie = "Miles del Futuro"
    
    tag = input("Tag [AzE] por defecto: ").strip() or "AzE"
    
    ep_inicio = input("Número de episodio inicial (1 por defecto): ").strip()
    try:
        num_episodio = int(ep_inicio) if ep_inicio else 1
    except:
        num_episodio = 1
    
    print(f"\n📁 Guardando en: {Path('.').absolute()}")
    print("-"*60)
    
    # Procesar videos
    exitosos = 0
    fallidos = []
    
    for i, video in enumerate(videos, 1):
        print(f"\n🎞️  Video {i}/{len(videos)}")
        resultado, num_usado = procesar_video(video, num_episodio, modelo, nombre_serie, tag)
        
        if resultado:
            exitosos += 1
        else:
            fallidos.append((video.name, num_usado))
        
        # Incrementar número de episodio si no se detectó del nombre
        num_episodio = num_usado + 1
    
    print("\n" + "="*60)
    print(f"📊 RESUMEN: {exitosos}/{len(videos)} videos renombrados")
    if fallidos:
        print(f"   ❌ Fallidos: {len(fallidos)}")
        print("   📋 Lista de fallidos:")
        for nombre, num in fallidos:
            print(f"      - Ep {num:02d}: {nombre}")
    print("="*60)

if __name__ == "__main__":
    main()
