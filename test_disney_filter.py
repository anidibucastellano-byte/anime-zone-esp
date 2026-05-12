# Test para verificar el filtrado de Disney
items_disney = [
    {
        'name': 'Big Hero 6: La serie',
        'tipo': 'Dibujo Animado',
        'genre': 'Acción, Comedia, Superhéroes, Disney',
        'specificGenre': 'Acción, Disney'
    },
    {
        'name': 'Chip y Chop: Guardianes rescatadores',
        'tipo': 'Dibujo Animado',
        'genre': '',
        'specificGenre': 'Aventura, Disney'
    }
]

def test_disney_filter():
    currentTab = 'disney'
    
    for item in items_disney:
        print(f'Testing: {item["name"]}')
        
        # Simular la lógica del filtro
        itemTipo = (item.get('tipo', item.get('type', '') or '')).toString().lower().trim()
        tabTipo = currentTab.lower().trim()
        itemGenero = (item.get('specificGenre', item.get('genre', '') or '')).lower()
        
        print(f'  itemTipo: "{itemTipo}"')
        print(f'  tabTipo: "{tabTipo}"')
        print(f'  itemGenero: "{itemGenero}"')
        
        # Verificar si coincide con Disney
        tipoMatch = False
        if tabTipo == 'disney' and itemGenero and itemGenero.includes('disney'):
            tipoMatch = True
        
        print(f'  tipoMatch: {tipoMatch}')
        print()

if __name__ == '__main__':
    test_disney_filter()
