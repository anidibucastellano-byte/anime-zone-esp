#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

# Cargar TOP.json
with open('TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Sinopsis correctas para Digimon
sinopsis_digimon_adventure = """Siete niños disfrutan de sus vacaciones de verano en un campamento, cuando de repente, se ven envueltos en un misterioso mundo: El Mundo Digital. Un mundo paralelo al suyo formado a partir de datos digitales. Allí conocen a sus compañeros los digimon, y juntos tendrán que solucionar los extraños sucesos que aterran la Isla File, provocados por Devimon. Pero tal vez no sea ese el único motivo por el que aparecieron en aquel misterioso mundo, tendrán que enfrentarse a más de una aventura para descubrir el verdadero propósito de su viaje."""

sinopsis_digimon_02 = """Han pasado tres años desde que los niños elegidos salvaron el Mundo Digital. Ahora, un nuevo grupo de niños es elegido para proteger ambos mundos. Con nuevos digimon y nuevas evoluciones, deberán enfrentarse a nuevas amenazas mientras descubren los misterios que conectan ambos mundos."""

# Buscar y actualizar Digimon
for cat in ['anime', 'series', 'dibujos', 'peliculas']:
    for item in data.get(cat, []):
        nombre = item.get('name', '').lower()
        
        # Digimon Adventure (1999)
        if 'digimon adventure' in nombre and '1999' in str(item.get('year', '')):
            print(f"✅ Actualizando: {item['name']}")
            item['sinopsis'] = sinopsis_digimon_adventure
            print(f"   Sinopsis actualizada: {len(sinopsis_digimon_adventure)} chars")
        
        # Digimon 02 Adventure (2000)
        elif 'digimon' in nombre and ('02' in nombre or item.get('year') == 2000) and 'adventure' in nombre:
            print(f"✅ Actualizando: {item['name']}")
            item['sinopsis'] = sinopsis_digimon_02
            print(f"   Sinopsis actualizada: {len(sinopsis_digimon_02)} chars")
            # Corregir imagen si es necesario
            if 'mushiking' in item.get('imagen', '').lower():
                item['imagen'] = "images/anime_187_ActivoDigimon-02-Adventure-2000-Dual-Audio-5050-DVD-Rip-944x720-395580-MB-Mega-Ver-Online.jpg"
                print("   Imagen corregida")

# Guardar
with open('TOP.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n✅ Archivo actualizado")
