import json

with open('c:/Users/Rafael/CascadeProjects/windsurf-project/TOP.json', encoding='utf-8') as f:
    data = json.load(f)

todas = []
for v in data.values():
    todas.extend(v)

serie = [s for s in todas if 'Monster' in s.get('name', '')]
print(f'Encontrado: {len(serie)} series')
for i, s in enumerate(serie[:5]):
    print(f'{i+1}. {s.get("name")} -> Género: {s.get("genre")}')
