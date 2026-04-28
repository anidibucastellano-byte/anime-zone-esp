"""
Corregir todas las secuencias de escape en generar_html_foroactivo.py
"""

from pathlib import Path

ruta = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\generar_html_foroactivo.py')

with open(ruta, 'r', encoding='utf-8') as f:
    contenido = f.read()

# Reemplazar secuencias de escape dobles por simples (para JavaScript)
contenido = contenido.replace('\\s', '\s')
contenido = contenido.replace('\\d', '\d')
contenido = contenido.replace('\\[', '\[')
contenido = contenido.replace('\\]', '\]')
contenido = contenido.replace('\\(', '\(')
contenido = contenido.replace('\\)', '\)')
contenido = contenido.replace('\\u', '\u')

with open(ruta, 'w', encoding='utf-8') as f:
    f.write(contenido)

print("✅ Secuencias de escape corregidas")
