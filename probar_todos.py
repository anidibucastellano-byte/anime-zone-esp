#!/usr/bin/env python3
"""
Script de prueba para procesar TODOS los videos y ver qué títulos extrae
Muestra el texto transcrito para poder ajustar los patrones
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
    print("❌ Whisper no instalado. Ejecuta: pip install openai-whisper")
    sys.exit(1)

# ============ CONFIGURACIÓN ============
FFMPEG_PATH = r"C:\Users\Rafael\CascadeProjects\windsurf-project\ffmpeg-2026-05-11-git-17bc88e67f-essentials_build\bin\ffmpeg.exe"
CARPETA_VIDEOS = r"C:\Users\Rafael\Downloads\Telegram Desktop\Miles del futuro"

# Añadir ffmpeg al PATH
if os.path.exists(FFMPEG_PATH):
    ffmpeg_dir = os.path.dirname(FFMPEG_PATH)
    if ffmpeg_dir not in os.environ['PATH']:
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']

# Títulos conocidos para corregir
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
]

# ============ FUNCIONES ============

def extraer_audio(video_path, duracion=180):
    """Extrae audio del video"""
    audio_temp = video_path.parent / f"{video_path.stem}_temp.wav"
    
    ffmpeg_exe = FFMPEG_PATH if os.path.exists(FFMPEG_PATH) else 'ffmpeg'
    
    cmd = [
        ffmpeg_exe, '-y', '-i', str(video_path),
        '-t', str(duracion), '-vn',
        '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
        str(audio_temp)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=60)
        if audio_temp.exists() and audio_temp.stat().st_size > 1000:
            return audio_temp
    except Exception as e:
        print(f"❌ Error extrayendo audio: {e}")
    
    return None

def transcribir(audio_path, modelo="small"):
    """Transcribe audio con Whisper"""
    try:
        model = whisper.load_model(modelo)
        result = model.transcribe(str(audio_path), language='es', verbose=False)
        return result['text']
    except Exception as e:
        print(f"❌ Error transcribiendo: {e}")
        return None

def buscar_variante(texto, palabra):
    """Busca variante de palabra con errores típicos"""
    variantes = {
        'lanzadera': ['lanzadera', 'unzadera', 'lansadera', 'zadera', 'lanza', 'lansader'],
        'deriva': ['deriva', 'alaveriva', 'la deriva', 'aderiva', 'deriba'],
        'surf': ['surf', 'serf', 'surff', 'serff'],
        'remolino': ['remolino', 'remolina', 'remolín', 'molino', 'molina'],
        'hermanos': ['hermanos', 'ermanos', 'ermanitos', 'hermanitos'],
        'callisto': ['callisto', 'calisto', 'kalisto', 'calixto'],
        'estación': ['estación', 'estacion', 'esta ción', 'estaci'],
        'espacial': ['espacial', 'espasial', 'especial', 'espacial'],
        'planeta': ['planeta', 'planetta', 'planeta'],
        'galáctico': ['galáctico', 'galactico', 'galactiko'],
        'caballero': ['caballero', 'cabayero', 'caballero', 'caballos'],
        'nocturno': ['nocturno', 'noctuno', 'nocturn'],
        'relámpago': ['relámpago', 'relampago', 'relampo'],
        'mercurio': ['mercurio', 'merkuri', 'mercuryo'],
        'runaway': ['runaway', 'run away', 'runway'],
        'mamá': ['mamá', 'mama', 'mamá'],
        'miles': ['miles', 'mile', 'mailes'],
        'nave': ['nave', 'naves', 'naive'],
        'carrera': ['carrera', 'carera', 'carrers'],
        'mision': ['misión', 'mision', 'mission'],
        'unicornio': ['unicornio', 'unicorn', 'unicornios'],
        'detectives': ['detectives', 'detective', 'detectibes'],
        'exploradores': ['exploradores', 'explorador', 'exploradors'],
        'equipo': ['equipo', 'equipos', 'equipo'],
        'jet': ['jet', 'jets', 'yets'],
        'nueva': ['nueva', 'nuevas', 'neva'],
        'tierra': ['tierra', 'tierras', 'tierr'],
    }
    
    texto_lower = texto.lower()
    if palabra in variantes:
        for v in variantes[palabra]:
            if v in texto_lower:
                return v
    return None

def encontrar_titulo(texto):
    """Encuentra el título más cercano en el texto"""
    mejor_titulo = None
    mejor_score = 0
    
    for titulo in TITULOS_REALES:
        palabras = titulo.lower().split()
        score = 0
        palabras_encontradas = []
        
        for palabra in palabras:
            variante = buscar_variante(texto, palabra)
            if variante:
                score += 1
                palabras_encontradas.append(palabra)
        
        # Bonus si encontramos todas las palabras
        if score == len(palabras) and len(palabras) > 1:
            score += 2
        
        if score > mejor_score:
            mejor_score = score
            mejor_titulo = titulo
            mejor_palabras = palabras_encontradas
    
    # Necesitamos al menos 2 palabras coincidentes o 1 si es título corto
    if mejor_titulo and mejor_score >= 2:
        return mejor_titulo, mejor_score
    
    return None, 0

def procesar_video(video_path, num):
    """Procesa un video y retorna resultado"""
    print(f"\n{'='*80}")
    print(f"📹 VIDEO {num}: {video_path.name}")
    print(f"{'='*80}")
    
    # Extraer audio
    print("🔊 Extrayendo audio...")
    audio = extraer_audio(video_path)
    if not audio:
        print("❌ Falló extracción de audio")
        return None, "Sin audio"
    
    # Transcribir
    print("📝 Transcribiendo con Whisper...")
    texto = transcribir(audio)
    audio.unlink()
    
    if not texto:
        print("❌ Falló transcripción")
        return None, "Sin transcripción"
    
    # Mostrar texto (primeros 400 chars)
    print(f"\n🗣️  TEXTO TRANSCRITO:")
    print("-" * 80)
    print(texto[:400] + "..." if len(texto) > 400 else texto)
    print("-" * 80)
    
    # Buscar título
    titulo, score = encontrar_titulo(texto)
    
    if titulo:
        print(f"\n✅ TÍTULO DETECTADO: '{titulo}' (score: {score})")
        return titulo, "OK"
    else:
        # Buscar palabras individuales para diagnóstico
        print(f"\n🔍 No se detectó título. Buscando palabras individuales...")
        palabras_clave = ['lanzadera', 'surf', 'remolino', 'hermanos', 'callisto', 
                         'estación', 'mercurio', 'planeta', 'caballero', 'relámpago']
        encontradas = []
        for p in palabras_clave:
            v = buscar_variante(texto, p)
            if v:
                encontradas.append(f"{p} (como '{v}')")
        if encontradas:
            print(f"   Palabras similares encontradas: {', '.join(encontradas)}")
        
        print(f"\n⚠️  TÍTULO NO DETECTADO")
        return None, "No detectado"

def main():
    print("="*80)
    print("🧪 PRUEBA DE EXTRACCIÓN DE TÍTULOS - TODOS LOS VIDEOS")
    print("="*80)
    
    carpeta = Path(CARPETA_VIDEOS)
    if not carpeta.exists():
        print(f"❌ Carpeta no encontrada: {carpeta}")
        return
    
    # Buscar videos
    videos = sorted(carpeta.glob('*.mp4'))
    if not videos:
        print("❌ No se encontraron videos MP4")
        return
    
    print(f"📁 Carpeta: {carpeta}")
    print(f"🎬 Total de videos: {len(videos)}")
    print(f"\n{'='*80}")
    print("COMENZANDO PROCESAMIENTO...")
    print(f"{'='*80}\n")
    
    # Procesar todos
    resultados = []
    for i, video in enumerate(videos, 1):
        titulo, estado = procesar_video(video, i)
        resultados.append({
            'num': i,
            'archivo': video.name,
            'titulo': titulo,
            'estado': estado
        })
        
        # Pausa entre videos
        if i < len(videos):
            print(f"\n⏳ Pausa de 2 segundos...")
            import time
            time.sleep(2)
    
    # RESUMEN FINAL
    print(f"\n\n{'='*80}")
    print("📊 RESUMEN FINAL - TODOS LOS VIDEOS")
    print(f"{'='*80}\n")
    
    exitosos = sum(1 for r in resultados if r['titulo'])
    fallidos = len(resultados) - exitosos
    
    print(f"✅ Detectados correctamente: {exitosos}/{len(resultados)}")
    print(f"❌ Fallidos: {fallidos}/{len(resultados)}\n")
    
    print("Lista detallada:")
    print("-" * 80)
    for r in resultados:
        num = r['num']
        nombre = r['archivo'][:40]  # Truncar nombre largo
        if r['titulo']:
            print(f"{num:2d}. ✅ {nombre:<40} → '{r['titulo']}'")
        else:
            print(f"{num:2d}. ❌ {nombre:<40} → {r['estado']}")
    
    print(f"\n{'='*80}")
    
    # Guardar resultados en archivo
    archivo_salida = carpeta / "resultados_extraccion.txt"
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("RESULTADOS DE EXTRACCIÓN DE TÍTULOS\n")
        f.write("="*80 + "\n\n")
        for r in resultados:
            f.write(f"{r['num']:2d}. {r['archivo']}\n")
            if r['titulo']:
                f.write(f"    ✅ {r['titulo']}\n")
            else:
                f.write(f"    ❌ {r['estado']}\n")
            f.write("\n")
    
    print(f"\n📝 Resultados guardados en: {archivo_salida}")

if __name__ == "__main__":
    main()
