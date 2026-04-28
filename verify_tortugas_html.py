"""
Verificar que Las Tortugas Ninja (2012) tiene la imagen correcta en el HTML
"""

from pathlib import Path

ruta_html = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\index.html')

url_esperada = "https://res.cloudinary.com/ddaxoi1n4/image/upload/v1770837461/mis_archivos_elegidos/manual_poster_tmdb_Las_Tortugas_Ninja.jpg"

with open(ruta_html, 'r', encoding='utf-8') as f:
    contenido = f.read()

if 'Las Tortugas Ninja' in contenido:
    print("✅ Las Tortugas Ninja (2012) está en el HTML")
else:
    print("❌ Las Tortugas Ninja (2012) NO está en el HTML")

if url_esperada in contenido:
    print(f"✅ La URL de Cloudinary está en el HTML")
    # Encontrar el contexto
    idx = contenido.find(url_esperada)
    contexto = contenido[max(0, idx-100):idx+200]
    print(f"   Contexto: ...{contexto}...")
else:
    print(f"❌ La URL de Cloudinary NO está en el HTML")
    print(f"   Buscando variantes...")
    # Buscar cualquier URL de tortugas
    import re
    urls = re.findall(r'https://[^"\'>\s]*tortugas[^"\'>\s]*', contenido, re.IGNORECASE)
    if urls:
        print(f"   URLs encontradas: {urls[:3]}")
    else:
        print("   No se encontraron URLs con 'tortugas'")
