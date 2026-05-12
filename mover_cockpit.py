#!/usr/bin/env python3
import json

with open(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Buscar y mover The Cockpit de dibujos a anime
cockpit = None
for i, item in enumerate(data.get('dibujos', [])):
    if 'cockpit' in item.get('name', '').lower():
        cockpit = data['dibujos'].pop(i)
        print(f"✅ Encontrado y removido de 'dibujos': {item.get('name', 'N/A')[:50]}...")
        break

if cockpit:
    # Añadir a anime
    data['anime'].append(cockpit)
    print(f"✅ Movido a 'anime'")
    
    # Guardar cambios
    with open(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON guardado")
    print(f"\nAhora: Anime={len(data['anime'])}, Dibujos={len(data['dibujos'])}")
else:
    print("❌ No se encontró The Cockpit")
