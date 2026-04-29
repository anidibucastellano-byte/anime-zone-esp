#!/usr/bin/env python3
"""Test rápido para verificar que el editor carga sin errores"""

import sys
sys.path.insert(0, r'c:\Users\Rafael\CascadeProjects\windsurf-project')

try:
    # Intentar importar el módulo
    import editor_compacto
    print("✅ Módulo importado correctamente")
    
    # Verificar que las clases existen
    if hasattr(editor_compacto, 'EditorCompacto'):
        print("✅ Clase EditorCompacto existe")
    else:
        print("❌ Clase EditorCompacto no encontrada")
        
    print("\n✅ Todo parece correcto. Ahora prueba ejecutar el editor.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
