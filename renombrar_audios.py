#!/usr/bin/env python3
"""
Script para renombrar pistas de audio en archivos de video masivamente.

Requiere: mkvtoolnix (mkvpropedit) o ffmpeg
Instalación: https://mkvtoolnix.download/downloads.html

Uso:
    python renombrar_audios.py --folder "C:/Mis Videos" --names "Castellano,Catalán,Japonés"
    
O modo interactivo:
    python renombrar_audios.py
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from glob import glob


def check_mkvpropedit():
    """Verificar que mkvpropedit está instalado"""
    try:
        result = subprocess.run(['mkvpropedit', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


def check_ffmpeg():
    """Verificar que ffmpeg está instalado"""
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True, text=True, timeout=5)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


def find_ffprobe():
    """Buscar ffprobe en PATH y ubicaciones comunes"""
    # Primero intentar en PATH
    try:
        subprocess.run(['ffprobe', '-version'], capture_output=True, timeout=5)
        return 'ffprobe'
    except FileNotFoundError:
        pass

    # Buscar en ubicaciones comunes
    common_paths = [
        r'C:\ffmpeg\bin\ffprobe.exe',
        r'C:\Program Files\ffmpeg\bin\ffprobe.exe',
        r'C:\Program Files (x86)\ffmpeg\bin\ffprobe.exe',
        r'C:\Users\%USERNAME%\ffmpeg\bin\ffprobe.exe',
        r'C:\ffmpeg\ffprobe.exe',
    ]

    for path in common_paths:
        expanded_path = os.path.expandvars(path)
        if os.path.exists(expanded_path):
            return expanded_path

    return None


def get_audio_tracks_ffmpeg(video_path):
    """Obtener información de pistas de audio usando ffprobe"""
    ffprobe_path = find_ffprobe()
    if not ffprobe_path:
        return None  # ffprobe no encontrado

    try:
        cmd = [
            ffprobe_path, '-v', 'error', '-select_streams', 'a',
            '-show_entries', 'stream=index,codec_name,codec_long_name,tags',
            '-of', 'json', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        return data.get('streams', [])
    except Exception as e:
        print(f"Error analizando {video_path}: {e}")
        return []


def rename_audio_tracks_mkv(video_path, audio_names, dry_run=False):
    """
    Renombrar pistas de audio en un archivo MKV usando mkvpropedit
    
    Args:
        video_path: Ruta al archivo de video
        audio_names: Lista de nombres para las pistas de audio
        dry_run: Si True, solo muestra lo que haría sin hacer cambios
    """
    if not video_path.lower().endswith('.mkv'):
        print(f"  ⚠️  Solo archivos MKV son soportados por mkvpropedit: {os.path.basename(video_path)}")
        return False
    
    # Obtener información actual
    tracks = get_audio_tracks_ffmpeg(video_path)
    audio_count = len(tracks)
    
    if audio_count == 0:
        print(f"  ⚠️  No se encontraron pistas de audio: {os.path.basename(video_path)}")
        return False
    
    if audio_count != len(audio_names):
        print(f"  ⚠️  El video tiene {audio_count} pistas de audio pero proporcionaste {len(audio_names)} nombres")
        print(f"      Archivo: {os.path.basename(video_path)}")
        print(f"      Pistas actuales:")
        for i, track in enumerate(tracks, 1):
            tags = track.get('tags', {})
            lang = tags.get('language', 'unknown')
            title = tags.get('title', 'Sin título')
            print(f"        {i}. {title} ({lang})")
        return False
    
    # Mostrar cambios planeados
    print(f"\n  📁 {os.path.basename(video_path)}")
    for i, (track, new_name) in enumerate(zip(tracks, audio_names), 1):
        tags = track.get('tags', {})
        old_title = tags.get('title', 'Sin título')
        print(f"     Pista {i}: '{old_title}' → '{new_name}'")
    
    if dry_run:
        return True
    
    # Aplicar cambios con mkvpropedit
    try:
        for i, new_name in enumerate(audio_names, 1):
            cmd = [
                'mkvpropedit', video_path,
                '--edit', f'track:a{i}',
                '--set', f'name={new_name}'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"  ❌ Error en pista {i}: {result.stderr}")
                return False
        
        print(f"  ✅ Renombrado exitosamente")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def convert_and_rename_generic(video_path, audio_names, source_ext, output_suffix="_converted", dry_run=False):
    """
    Convertir video a MKV usando mkvmerge y luego renombrar pistas de audio
    Usa las herramientas que el usuario ya tiene (MKVToolNix)

    Args:
        video_path: Ruta al archivo de video
        audio_names: Lista de nombres para las pistas de audio
        source_ext: Extensión de origen ('.mp4', '.ogm', etc.)
        output_suffix: Sufijo para los archivos de salida
        dry_run: Si True, solo muestra lo que haría
    """
    if not video_path.lower().endswith(source_ext.lower()):
        print(f"  ⚠️  Esta función solo funciona con archivos {source_ext.upper()}: {os.path.basename(video_path)}")
        return False

    # Verificar que mkvmerge existe
    mkvmerge_path = None
    try:
        subprocess.run(['mkvmerge', '--version'], capture_output=True, timeout=5)
        mkvmerge_path = 'mkvmerge'
    except FileNotFoundError:
        # Buscar en ubicaciones comunes
        common_paths = [
            r'C:\Program Files\MKVToolNix\mkvmerge.exe',
            r'C:\Program Files (x86)\MKVToolNix\mkvmerge.exe',
        ]
        for path in common_paths:
            if os.path.exists(path):
                mkvmerge_path = path
                break

    if not mkvmerge_path:
        print(f"  ❌ Error: mkvmerge no encontrado")
        print(f"     Asegúrate de que MKVToolNix esté instalado en C:\Program Files\MKVToolNix")
        return False

    # Verificar que mkvpropedit existe
    mkvpropedit_path = None
    try:
        subprocess.run(['mkvpropedit', '--version'], capture_output=True, timeout=5)
        mkvpropedit_path = 'mkvpropedit'
    except FileNotFoundError:
        common_paths = [
            r'C:\Program Files\MKVToolNix\mkvpropedit.exe',
            r'C:\Program Files (x86)\MKVToolNix\mkvpropedit.exe',
        ]
        for path in common_paths:
            if os.path.exists(path):
                mkvpropedit_path = path
                break

    if not mkvpropedit_path:
        print(f"  ❌ Error: mkvpropedit no encontrado")
        return False

    # Generar nombre de salida (cambiar extensión a .mkv)
    file_path = Path(video_path)
    output_path = file_path.parent / f"{file_path.stem}{output_suffix}.mkv"

    print(f"\n  📁 {os.path.basename(video_path)}")
    print(f"     → {output_path.name}")
    for i, new_name in enumerate(audio_names, 1):
        print(f"     Pista {i}: → '{new_name}'")

    if dry_run:
        return True

    # Paso 1: Convertir a MKV
    try:
        print(f"     🔄 Convirtiendo a MKV...")
        cmd = [mkvmerge_path, '-o', str(output_path), video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0 and result.returncode != 1:  # 1 es warning, no error
            print(f"  ❌ Error en mkvmerge: {result.stderr[:200]}")
            return False

        if not os.path.exists(output_path):
            print(f"  ❌ Error: No se creó el archivo MKV")
            return False

        print(f"     ✅ Convertido a MKV")
    except Exception as e:
        print(f"  ❌ Error convirtiendo: {e}")
        return False

    # Paso 2: Renombrar pistas de audio en el MKV
    try:
        print(f"     📝 Renombrando pistas de audio...")
        for i, new_name in enumerate(audio_names, 1):
            cmd = [
                mkvpropedit_path, str(output_path),
                '--edit', f'track:a{i}',
                '--set', f'name={new_name}'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"  ❌ Error renombrando pista {i}: {result.stderr}")
                # No borramos el MKV creado, el usuario puede renombrar manualmente
                return False

        print(f"  ✅ Creado: {output_path.name}")
        print(f"     (El archivo original se mantiene intacto)")
        return True
    except Exception as e:
        print(f"  ❌ Error renombrando: {e}")
        return False


def rename_audio_tracks_ffmpeg(video_path, audio_names, output_suffix="_renamed", dry_run=False):
    """
    Renombrar pistas de audio usando ffmpeg (crea nuevos archivos)
    Funciona con cualquier formato de video
    
    Args:
        video_path: Ruta al archivo de video
        audio_names: Lista de nombres para las pistas de audio
        output_suffix: Sufijo para los archivos de salida
        dry_run: Si True, solo muestra lo que haría
    """
    tracks = get_audio_tracks_ffmpeg(video_path)
    
    # Si ffprobe no está disponible, usar el número de nombres proporcionado
    if tracks is None:
        audio_count = len(audio_names)
    else:
        audio_count = len(tracks)
        if audio_count == 0:
            print(f"  ⚠️  No se encontraron pistas de audio: {os.path.basename(video_path)}")
            return False
    
    if audio_count != len(audio_names):
        print(f"  ⚠️  El video tiene {audio_count} pistas de audio pero proporcionaste {len(audio_names)} nombres")
        return False
    
    # Generar nombre de salida
    file_path = Path(video_path)
    output_path = file_path.parent / f"{file_path.stem}{output_suffix}{file_path.suffix}"
    
    print(f"\n  📁 {os.path.basename(video_path)}")
    print(f"     → {output_path.name}")
    for i, new_name in enumerate(audio_names, 1):
        print(f"     Pista {i}: → '{new_name}'")
    
    if dry_run:
        return True
    
    # Verificar que ffmpeg existe
    ffmpeg_path = None
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        ffmpeg_path = 'ffmpeg'
    except FileNotFoundError:
        # Buscar en ubicaciones comunes
        common_paths = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
        ]
        for path in common_paths:
            if os.path.exists(path):
                ffmpeg_path = path
                break
    
    if not ffmpeg_path:
        print(f"  ❌ Error: ffmpeg no encontrado")
        print(f"     Descarga desde: https://www.gyan.dev/ffmpeg/builds/")
        print(f"     Versión 'essentials', descomprime en C:\ffmpeg")
        return False
    
    # Construir comando ffmpeg
    try:
        cmd = [ffmpeg_path, '-i', video_path, '-c', 'copy']
        
        # Agregar metadatos para cada pista de audio
        for i, new_name in enumerate(audio_names, 1):
            cmd.extend(['-metadata:s:a:' + str(i-1), f'title={new_name}'])
        
        cmd.append(str(output_path))
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"  ❌ Error: {result.stderr[:200]}")
            return False
        
        print(f"  ✅ Creado: {output_path.name}")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def interactive_mode():
    """Modo interactivo para configurar el renombrado"""
    print("=" * 60)
    print("🎬  RENOMBRADOR DE PISTAS DE AUDIO")
    print("=" * 60)
    
    # Verificar herramientas disponibles
    has_mkvpropedit = check_mkvpropedit()
    has_ffmpeg = check_ffmpeg()
    
    if not has_mkvpropedit and not has_ffmpeg:
        print("\n❌ ERROR: No se encontró ni mkvpropedit ni ffmpeg")
        print("   Por favor instala MKVToolNix o FFmpeg:")
        print("   - MKVToolNix: https://mkvtoolnix.download/downloads.html")
        print("   - FFmpeg: https://ffmpeg.org/download.html")
        input("\nPresiona Enter para salir...")
        return
    
    print(f"\n✅ Herramientas detectadas:")
    if has_mkvpropedit:
        print("   • mkvpropedit (MKVToolNix) - Modifica archivos MKV in-place")
    if has_ffmpeg:
        print("   • ffmpeg - Crea nuevos archivos (funciona con cualquier formato)")
    
    # Pedir carpeta
    print("\n📁 Introduce la ruta de la carpeta con los videos:")
    folder = input("   > ").strip().strip('"')
    
    if not os.path.isdir(folder):
        print(f"\n❌ La carpeta no existe: {folder}")
        input("Presiona Enter para salir...")
        return
    
    # Buscar videos
    extensions = ['*.mkv', '*.mp4', '*.avi', '*.mov', '*.webm', '*.ogm', '*.ogg']
    videos = []
    for ext in extensions:
        videos.extend(glob(os.path.join(folder, ext)))
        videos.extend(glob(os.path.join(folder, ext.upper())))
    
    videos = list(set(videos))  # Eliminar duplicados
    
    if not videos:
        print(f"\n⚠️  No se encontraron videos en: {folder}")
        input("Presiona Enter para salir...")
        return
    
    print(f"\n📊 Se encontraron {len(videos)} archivos de video")
    
    # Analizar primer video para ver cuántas pistas de audio tiene
    sample_video = videos[0]
    print(f"\n🔍 Analizando primer video: {os.path.basename(sample_video)}")

    tracks = get_audio_tracks_ffmpeg(sample_video)

    if tracks is None:
        print("⚠️  ffprobe no encontrado. No se puede analizar automáticamente.")
        print("    Puedes especificar manualmente el número de pistas.")
        audio_count = None
    else:
        audio_count = len(tracks)

    if audio_count == 0:
        print("⚠️  No se encontraron pistas de audio en el video de muestra")
        print("    ¿Quieres especificar manualmente el número de pistas? (S/N)")
        respuesta = input("   > ").strip().lower()
        if respuesta == 's':
            print("\n¿Cuántas pistas de audio tienen los videos?")
            try:
                audio_count = int(input("   > ").strip())
            except ValueError:
                print("❌ Número inválido")
                input("Presiona Enter para salir...")
                return
        else:
            input("Presiona Enter para salir...")
            return
    elif audio_count is None:
        # ffprobe no disponible, preguntar manualmente
        print("\n¿Cuántas pistas de audio tienen los videos?")
        try:
            audio_count = int(input("   > ").strip())
        except ValueError:
            print("❌ Número inválido")
            input("Presiona Enter para salir...")
            return

    # Si tracks está disponible, mostrar información
    if tracks:
        print(f"\n🎵 Este video tiene {audio_count} pista(s) de audio:")
        for i, track in enumerate(tracks, 1):
            tags = track.get('tags', {})
            lang = tags.get('language', 'unknown')
            title = tags.get('title', 'Sin título')
            codec = track.get('codec_name', 'unknown')
            print(f"   {i}. {title} ({lang}) - {codec}")
    else:
        print(f"\n🎵 Configurando para {audio_count} pista(s) de audio")
    
    # Pedir nombres
    print(f"\n✏️  Introduce los nuevos nombres para las {audio_count} pistas de audio")
    print("   (separados por comas)")
    print("   Ejemplo: Castellano,Catalán,Japonés")
    print("   Ejemplo: Español,Inglés,Español (Latino)")
    
    names_input = input("\n   > ").strip()
    audio_names = [n.strip() for n in names_input.split(',')]
    
    if len(audio_names) != audio_count:
        print(f"\n❌ Error: El video tiene {audio_count} pistas pero proporcionaste {len(audio_names)} nombres")
        input("Presiona Enter para salir...")
        return
    
    print(f"\n📋 Nombres a asignar:")
    for i, name in enumerate(audio_names, 1):
        print(f"   Pista {i}: '{name}'")

    # Preguntar si es prueba (antes de elegir método)
    print(f"\n🧪 ¿Quieres hacer una prueba primero? (S/N)")
    print("   (Mostrará los cambios sin aplicarlos)")
    dry_run = input("   > ").strip().lower() == 's'

    # Elegir método
    print(f"\n🔧 Elige el método:")
    if has_mkvpropedit:
        print("   1. mkvpropedit (rápido, modifica archivos MKV in-place)")
    else:
        print("   1. mkvpropedit (no detectado - instala MKVToolNix)")

    if has_ffmpeg:
        print("   2. ffmpeg (crea nuevos archivos, compatible con todos los formatos)")
    else:
        print("   2. ffmpeg (no detectado - instala FFmpeg o especifica ruta)")

    # Opción 3: Convertir MP4 a MKV (usa las herramientas que ya tiene)
    print("   3. Convertir MP4 a MKV + renombrar (usa MKVToolNix, recomendado para MP4)")

    # Opción 4: Convertir OGM a MKV
    print("   4. Convertir OGM a MKV + renombrar (para videos OGM/Ogg Media)")

    method = input("\n   > ").strip()

    # Si eligió opción 3, usar la función de conversión
    if method == '3':
        # Verificar que tiene MKVToolNix
        try:
            subprocess.run(['mkvmerge', '--version'], capture_output=True, timeout=5)
            has_mkvmerge = True
        except FileNotFoundError:
            has_mkvmerge = False

        if not has_mkvmerge:
            print("\n❌ Error: mkvmerge no encontrado. Instala MKVToolNix primero.")
            input("Presiona Enter para salir...")
            return

        # Procesar videos con la función de conversión
        print(f"\n{'='*60}")
        print(f"🚀 CONVIRTIENDO {len(videos)} MP4 A MKV Y RENOMBRANDO...")
        print(f"{'='*60}")

        success_count = 0
        error_count = 0

        for video_path in videos:
            if video_path.lower().endswith('.mp4'):
                if convert_and_rename_generic(video_path, audio_names, '.mp4', '_mkv', dry_run=dry_run):
                    success_count += 1
                else:
                    error_count += 1
            else:
                print(f"\n  ⚠️  Saltando {os.path.basename(video_path)} (no es MP4)")

        print(f"\n{'='*60}")
        print(f"✅ COMPLETADO: {success_count} exitosos, {error_count} errores")
        print(f"{'='*60}")

        if dry_run:
            print("\n📝 Esto fue una prueba. No se hicieron cambios reales.")

        input("\nPresiona Enter para salir...")
        return

    # Si eligió opción 4 (OGM a MKV)
    if method == '4':
        # Verificar que tiene MKVToolNix
        try:
            subprocess.run(['mkvmerge', '--version'], capture_output=True, timeout=5)
            has_mkvmerge = True
        except FileNotFoundError:
            has_mkvmerge = False

        if not has_mkvmerge:
            print("\n❌ Error: mkvmerge no encontrado. Instala MKVToolNix primero.")
            input("Presiona Enter para salir...")
            return

        # Procesar videos OGM
        print(f"\n{'='*60}")
        print(f"🚀 CONVIRTIENDO {len(videos)} OGM A MKV Y RENOMBRANDO...")
        print(f"{'='*60}")

        success_count = 0
        error_count = 0

        for video_path in videos:
            if video_path.lower().endswith(('.ogm', '.ogg')):
                if convert_and_rename_generic(video_path, audio_names, '.ogm', '_mkv', dry_run=dry_run):
                    success_count += 1
                else:
                    error_count += 1
            else:
                print(f"\n  ⚠️  Saltando {os.path.basename(video_path)} (no es OGM/OGG)")

        print(f"\n{'='*60}")
        print(f"✅ COMPLETADO: {success_count} exitosos, {error_count} errores")
        print(f"{'='*60}")

        if dry_run:
            print("\n📝 Esto fue una prueba. No se hicieron cambios reales.")

        input("\nPresiona Enter para salir...")
        return

    # Si eligió ffmpeg pero no está detectado, pedir ruta manual
    if method == '2' and not has_ffmpeg:
        print("\n⚠️  FFmpeg no detectado en PATH")
        print("   Puedes:")
        print("   a) Introducir la ruta completa a ffmpeg.exe")
        print("   b) Presionar Enter para buscar en ubicaciones comunes")
        ffmpeg_path = input("   > ").strip().strip('"')
        
        if ffmpeg_path and os.path.exists(ffmpeg_path):
            os.environ['PATH'] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ.get('PATH', '')
            print(f"   ✅ Usando: {ffmpeg_path}")
        else:
            # Intentar buscar en ubicaciones comunes
            common_ffmpeg_paths = [
                r'C:\ffmpeg\bin\ffmpeg.exe',
                r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
                r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
            ]
            found = False
            for path in common_ffmpeg_paths:
                if os.path.exists(path):
                    os.environ['PATH'] = os.path.dirname(path) + os.pathsep + os.environ.get('PATH', '')
                    print(f"   ✅ Encontrado: {path}")
                    found = True
                    break
            
            if not found:
                print("   ❌ No se encontró ffmpeg. Descarga desde: https://ffmpeg.org/download.html")
                print("   ¿Continuar de todos modos? (S/N)")
                if input("   > ").strip().lower() != 's':
                    return

    # Confirmar antes de aplicar cambios
    if not dry_run:
        print(f"\n⚠️  ¿Estás seguro de que quieres aplicar estos cambios a {len(videos)} videos? (S/N)")
        confirm = input("   > ").strip().lower()
        if confirm != 's':
            print("\n❌ Cancelado")
            input("Presiona Enter para salir...")
            return
    
    # Procesar
    print(f"\n{'='*60}")
    print(f"🚀 PROCESANDO {len(videos)} VIDEOS...")
    print(f"{'='*60}")
    
    success_count = 0
    error_count = 0
    
    for video_path in videos:
        if method == '1' and has_mkvpropedit:
            if rename_audio_tracks_mkv(video_path, audio_names, dry_run=dry_run):
                success_count += 1
            else:
                error_count += 1
        else:
            if rename_audio_tracks_ffmpeg(video_path, audio_names, dry_run=dry_run):
                success_count += 1
            else:
                error_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETADO: {success_count} exitosos, {error_count} errores")
    print(f"{'='*60}")
    
    if dry_run:
        print("\n📝 Esto fue una prueba. No se hicieron cambios reales.")
        print("   Ejecuta de nuevo y selecciona 'N' en la prueba para aplicar.")
    
    input("\nPresiona Enter para salir...")


def main():
    parser = argparse.ArgumentParser(
        description='Renombrar pistas de audio en videos masivamente',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  Modo interactivo:
    python renombrar_audios.py
    
  Línea de comandos (con mkvpropedit):
    python renombrar_audios.py --folder "C:/Videos" --names "Castellano,Catalán,Japonés"
    
  Solo mostrar cambios (dry-run):
    python renombrar_audios.py --folder "C:/Videos" --names "Español,Inglés" --dry-run
    
  Usar ffmpeg (crea nuevos archivos):
    python renombrar_audios.py --folder "C:/Videos" --names "Español,Inglés" --method ffmpeg
        """
    )
    
    parser.add_argument('--folder', '-f', help='Carpeta con los videos')
    parser.add_argument('--names', '-n', help='Nombres de pistas separados por comas')
    parser.add_argument('--method', '-m', choices=['mkvpropedit', 'ffmpeg'], 
                       default='mkvpropedit', help='Método a usar (default: mkvpropedit)')
    parser.add_argument('--suffix', '-s', default='_renamed',
                       help='Sufijo para archivos con ffmpeg (default: _renamed)')
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help='Mostrar cambios sin aplicarlos')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Modo interactivo (ignora otros argumentos)')
    
    args = parser.parse_args()
    
    # Si no hay argumentos o se pide modo interactivo
    if args.interactive or (not args.folder and not args.names):
        interactive_mode()
        return
    
    # Modo línea de comandos
    if not args.folder or not args.names:
        parser.print_help()
        sys.exit(1)
    
    if not os.path.isdir(args.folder):
        print(f"❌ La carpeta no existe: {args.folder}")
        sys.exit(1)
    
    # Buscar videos
    extensions = ['*.mkv', '*.mp4', '*.avi', '*.mov', '*.webm', '*.ogm', '*.ogg']
    videos = []
    for ext in extensions:
        videos.extend(glob(os.path.join(args.folder, ext)))
        videos.extend(glob(os.path.join(args.folder, ext.upper())))
    
    videos = list(set(videos))
    
    if not videos:
        print(f"⚠️  No se encontraron videos en: {args.folder}")
        sys.exit(1)
    
    audio_names = [n.strip() for n in args.names.split(',')]
    
    print(f"📊 Procesando {len(videos)} videos con {len(audio_names)} nombres de pista")
    
    success_count = 0
    error_count = 0
    
    for video_path in videos:
        if args.method == 'mkvpropedit':
            if rename_audio_tracks_mkv(video_path, audio_names, dry_run=args.dry_run):
                success_count += 1
            else:
                error_count += 1
        else:
            if rename_audio_tracks_ffmpeg(video_path, audio_names, args.suffix, dry_run=args.dry_run):
                success_count += 1
            else:
                error_count += 1
    
    print(f"\n✅ Completado: {success_count} exitosos, {error_count} errores")


if __name__ == '__main__':
    main()
