#!/usr/bin/env python3
"""
Corrige las 15 rutas de imágenes que tienen nombres incorrectos
"""
import json
import os

# Mapeo de tema_id -> nombre de archivo correcto
ARCHIVOS_CORRECTOS = {
    '1236': 'images/imagesanime_1236_Activo-Boogiepop-Phantom-2000-Dual-Audio-1212-DVD-Rip-960x720-42059jpg.jpg',
    '1239': 'images/imagesanime_1239_Activo-Don-Drácula-1982-Castellano-88-TV-RIP-360x272-140-MB-MegaPjpg.jpg',
    '1469': 'images/imagesanime_1469_Activo-Dos-fuera-de-serie-Juana-y-Sergio-1984-Castellano-5858-DVD-Ripjpg.jpg',
    '1090': 'images/imagesanime_1090_Activo-Dota-Sangre-de-dragón-2021-Tri-Audio-2424-WebDL-Rip-1920x1080jpg.jpg',
    '1253': 'images/imagesanime_1253_Activo-El-amor-a-través-de-un-prisma-2026-Multi-audio-2020-WebDL-Rip-jpg.jpg',
    '1494': 'images/imagesanime_1494_Activo-El-mundo-de-Rumiko-1991-Dual-Audio-0505-DVD-Rip-640x480-465Mjpg.jpg',
    '1444': 'images/imagesanime_1444_Activo-Estás-arrestado-1999-Tri-Audio-515101-DVD-Rip-960x720-230jpg.jpg',
    '1506': 'images/imagesanime_1506_Activo-Gunslinger-Girl-2003-Dual-Audio-1313-BD-Rip-1920x1080-735MB1jpg.jpg',
    '1320': 'images/imagesanime_1320_Activo-JoJos-Bizarre-Adventure-2012-Tri-Audio-190190-WebDL-Rip-1920xjpg.jpg',
    '1250': 'images/imagesanime_1250_Activo-La-melodía-del-olvido-2004-Castellano-2424-DVD-Rip-640x480-4jpg.jpg',
    '1470': 'images/imagesanime_1470_Activo-New-Getter-Robo-2004-Dual-Audio-1313-BD-Rip-1440x1080-645MB9jpg.jpg',
    '1209': 'images/imagesanime_1209_Activo-Niña-del-demonio-2022-Dual-Audio-1010-WebDL-Rip-1920x1080-54jpg.jpg',
    '1391': 'images/imagesanime_1391_Activo-Rin-Las-Hijas-de-Mnemosyne-Miniserie-2008-Tri-Audio-0606-WebDLjpg.jpg',
    '581': 'images/imagesanime_581_Activo-Utena-la-chica-revolucionaria-1997-Castellano-3939-WebDL-Rip-jpg.jpg',
    '1484': 'images/imagesanime_1484_Activo-Wolfs-Rain-2003-Castellano-3030-DVD-Rip-640x480-60MB100MBjpg.jpg',
}

def main():
    # Cargar TOP.json
    with open('TOP.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    corregidas = 0
    
    for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
        for item in data.get(categoria, []):
            href = item.get('href', '')
            
            # Extraer tema_id del href
            for tema_id in ARCHIVOS_CORRECTOS.keys():
                if href.startswith(f'/t{tema_id}-'):
                    archivo_correcto = ARCHIVOS_CORRECTOS[tema_id]
                    
                    # Verificar que el archivo existe
                    if os.path.exists(archivo_correcto.replace('/', os.sep)):
                        item['imagen'] = archivo_correcto
                        corregidas += 1
                        print(f'✅ t{tema_id}: {archivo_correcto}')
                    else:
                        print(f'❌ t{tema_id}: Archivo no existe')
                    break
    
    # Guardar TOP.json
    with open('TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f'\n📊 Total corregidas: {corregidas}/15')

if __name__ == "__main__":
    main()
