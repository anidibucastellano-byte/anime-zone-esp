"""
Editor Compacto para TOP.json
Diseño optimizado para pantallas pequeñas
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import re

class EditorCompacto:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor Compacto - AnimeZoneESP")
        self.root.geometry("1100x700")
        
        self.ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
        
        self.cargar_datos()
        self.crear_widgets()
        
    def cargar_datos(self):
        """Cargar datos del JSON"""
        with open(self.ruta_json, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.categorias = {
            'Anime': self.data.get('anime', []),
            'Dibujos': self.data.get('dibujos', []),
            'Peliculas': self.data.get('peliculas', []),
            'Series': self.data.get('series', [])
        }
        
        for cat_name, items in self.categorias.items():
            for item in items:
                item['_categoria'] = cat_name.lower()
        
        # Organizar por género (primer género de cada serie)
        self.generos = {}
        for cat_name, items in self.categorias.items():
            for item in items:
                # Obtener género, manejando casos donde genre es lista o está vacío
                genero = item.get('genre', '')
                if isinstance(genero, list):
                    genero = ', '.join(genero) if genero else ''
                if not genero or (isinstance(genero, str) and genero.strip() == ''):
                    genero = item.get('specificGenre', 'Sin Género')
                
                genero_completo = genero if genero else 'Sin Género'
                
                if isinstance(genero_completo, str):
                    primer_genero = genero_completo.split(',')[0].strip()
                    if not primer_genero:  # Si quedó vacío después del split
                        primer_genero = 'Sin Género'
                    # Normalizar: primera letra mayúscula, resto minúscula
                    primer_genero = primer_genero.capitalize()
                else:
                    primer_genero = 'Sin Género'
                
                if primer_genero not in self.generos:
                    self.generos[primer_genero] = []
                self.generos[primer_genero].append(item)
        
        # Ordenar géneros por cantidad
        self.generos_ordenados = sorted(self.generos.items(), key=lambda x: len(x[1]), reverse=True)
        
        total = sum(len(items) for items in self.categorias.values())
        print(f"📊 Total: {total} series en {len(self.generos)} géneros")
    
    def limpiar_nombre(self, nombre):
        """Limpiar nombre de formato técnico"""
        if not nombre:
            return 'Sin nombre'
        nombre = re.sub(r'\[.*?\]', '', nombre)
        nombre = nombre.replace('(Activo)', '').replace('(Finalizado)', '')
        nombre = re.sub(r'\(.*?\)', '', nombre)
        nombre = re.sub(r'\s+', ' ', nombre)
        return nombre.strip()
    
    def filtrar_animacion(self, genero):
        """Filtrar 'Animación' del género"""
        if not genero:
            return genero
        # Dividir por comas y filtrar
        generos = [g.strip() for g in genero.split(',')]
        generos_filtrados = [g for g in generos if g.lower() not in ['animación', 'animacion']]
        return ', '.join(generos_filtrados) if generos_filtrados else genero
    
    def normalizar_genero(self, genero):
        """Normalizar género: reemplazar 'Niños' por 'Infantil'"""
        if not genero:
            return genero
        # Reemplazar 'Niños' o 'Ninos' por 'Infantil'
        generos = [g.strip() for g in genero.split(',')]
        generos_normalizados = []
        for g in generos:
            if g.lower() in ['niños', 'ninos', 'ninos']:
                generos_normalizados.append('Infantil')
            else:
                generos_normalizados.append(g)
        return ', '.join(generos_normalizados)
    
    def crear_widgets(self):
        """Crear interfaz compacta"""
        # Frame superior compacto
        frame_top = ttk.Frame(self.root, padding="5")
        frame_top.pack(fill='x')
        
        ttk.Label(frame_top, text="🎬 Editor", font=('Arial', 11, 'bold')).pack(side='left')
        
        # Frame para búsqueda con autocompletado
        frame_busqueda = ttk.Frame(frame_top)
        frame_busqueda.pack(side='left', padx=10)
        
        self.entry_buscar = ttk.Entry(frame_busqueda, width=35)
        self.entry_buscar.pack(fill='x')
        self.entry_buscar.bind('<Return>', self.buscar_global)
        self.entry_buscar.bind('<KeyRelease>', self.actualizar_autocompletado)
        self.entry_buscar.bind('<Down>', self.seleccionar_siguiente_sugerencia)
        self.entry_buscar.bind('<Up>', self.seleccionar_anterior_sugerencia)
        
        # Listbox para autocompletado (inicialmente oculto)
        self.lista_sugerencias = tk.Listbox(frame_busqueda, height=5, font=('Arial', 9))
        self.lista_sugerencias.bind('<Return>', self.aplicar_sugerencia)
        self.lista_sugerencias.bind('<Double-Button-1>', self.aplicar_sugerencia)
        self.lista_sugerencias.bind('<FocusOut>', self.ocultar_sugerencias)
        
        ttk.Button(frame_top, text="🔍", command=self.buscar_global, width=4).pack(side='left')
        
        ttk.Button(frame_top, text="📋 Edición Masiva", command=self.edicion_masiva).pack(side='left', padx=10)
        ttk.Button(frame_top, text="📋 Copiar Lista", command=self.copiar_lista).pack(side='left', padx=2)
        ttk.Button(frame_top, text="🚀 Deploy", command=self.hacer_deploy).pack(side='left', padx=5)
        ttk.Button(frame_top, text="➕ Añadir Serie", command=self.nueva_serie, width=12).pack(side='left', padx=5)
        ttk.Button(frame_top, text="🧹 Limpiar", command=self.limpiar_todos_los_campos, width=10).pack(side='left', padx=5)
        
        # Botón para cambiar modo
        self.modo_actual = 'categorias'  # 'categorias' o 'generos'
        self.btn_cambiar_modo = ttk.Button(frame_top, text="🎭 Ver por Géneros", command=self.cambiar_modo, width=15)
        self.btn_cambiar_modo.pack(side='left', padx=5)
        ttk.Button(frame_top, text="💾 Guardar", command=self.guardar).pack(side='right', padx=2)
        ttk.Button(frame_top, text="🔄 HTML", command=self.regenerar_html).pack(side='right', padx=2)
        
        # Notebook con pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=2)
        
        self.tabs = {}
        self.trees = {}
        
        for cat_name in ['Anime', 'Dibujos', 'Peliculas', 'Series']:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"{cat_name} ({len(self.categorias[cat_name])})")
            self.tabs[cat_name] = tab
            self.crear_tab_categoria(tab, cat_name)
        
        # Panel inferior - Editor compacto (dos columnas)
        frame_editor = ttk.LabelFrame(self.root, text="✏️ Editar Serie", padding="5")
        frame_editor.pack(fill='x', side='bottom', padx=5, pady=2)
        
        # Frame izquierdo - Campos principales
        frame_izq = ttk.Frame(frame_editor)
        frame_izq.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Nombre
        ttk.Label(frame_izq, text="Nombre:").pack(anchor='w')
        self.entry_nombre = ttk.Entry(frame_izq, width=60)
        self.entry_nombre.pack(fill='x', pady=(0, 5))
        
        # Fila: Año | Categoría | Primer Género
        frame_fila1 = ttk.Frame(frame_izq)
        frame_fila1.pack(fill='x', pady=2)
        
        ttk.Label(frame_fila1, text="Año:").pack(side='left')
        self.entry_year = ttk.Entry(frame_fila1, width=8)
        self.entry_year.pack(side='left', padx=(2, 10))
        
        ttk.Label(frame_fila1, text="Cat:").pack(side='left')
        self.combo_categoria = ttk.Combobox(frame_fila1, values=['Anime', 'Dibujos', 'Peliculas', 'Series'], width=10, state='readonly')
        self.combo_categoria.pack(side='left', padx=2)
        self.combo_categoria.set('Anime')
        
        ttk.Label(frame_fila1, text="Clasif:").pack(side='left')
        self.label_primer_genero = ttk.Label(frame_fila1, text="-", foreground='blue', width=12)
        self.label_primer_genero.pack(side='left', padx=2)
        
        # Géneros
        ttk.Label(frame_izq, text="Géneros (coma separados):").pack(anchor='w', pady=(5, 0))
        self.entry_generos = ttk.Entry(frame_izq, width=60)
        self.entry_generos.pack(fill='x')
        self.entry_generos.bind('<KeyRelease>', self.actualizar_primer_genero)
        
        # URLs en fila
        frame_urls = ttk.Frame(frame_izq)
        frame_urls.pack(fill='x', pady=5)
        
        ttk.Label(frame_urls, text="Imagen:").pack(side='left')
        self.entry_imagen = ttk.Entry(frame_urls, width=50)
        self.entry_imagen.pack(side='left', fill='x', expand=True, padx=2)
        
        # Frame derecho - Sinopsis y botones
        frame_der = ttk.Frame(frame_editor)
        frame_der.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        ttk.Label(frame_der, text="Sinopsis:").pack(anchor='w')
        self.text_sinopsis = tk.Text(frame_der, width=50, height=4, wrap=tk.WORD)
        self.text_sinopsis.pack(fill='both', expand=True)
        
        # Botones de acción compactos
        frame_botones = ttk.Frame(frame_der)
        frame_botones.pack(fill='x', pady=(5, 0))
        
        ttk.Button(frame_botones, text="✅ Aplicar", command=self.aplicar_cambios, width=12).pack(side='left', padx=2)
        ttk.Button(frame_botones, text="🔄 Restaurar", command=self.cargar_serie, width=12).pack(side='left', padx=2)
        ttk.Button(frame_botones, text="➡️ Siguiente", command=self.siguiente_serie, width=12).pack(side='left', padx=2)
        ttk.Button(frame_botones, text="🗑️ Eliminar", command=self.eliminar_serie, width=12).pack(side='left', padx=2)
        
        # URLs adicionales
        frame_urls2 = ttk.Frame(frame_izq)
        frame_urls2.pack(fill='x', pady=2)
        
        ttk.Label(frame_urls2, text="URL Página:").pack(side='left')
        self.entry_url = ttk.Entry(frame_urls2, width=40)
        self.entry_url.pack(side='left', fill='x', expand=True, padx=2)
        
        ttk.Label(frame_urls2, text="Rentry:").pack(side='left')
        self.entry_rentry = ttk.Entry(frame_urls2, width=25)
        self.entry_rentry.pack(side='left', padx=2)
        
        # Campos técnicos en fila
        frame_tecnicos = ttk.Frame(frame_izq)
        frame_tecnicos.pack(fill='x', pady=2)
        
        ttk.Label(frame_tecnicos, text="Tipo:").pack(side='left')
        self.combo_tipo = ttk.Combobox(frame_tecnicos, values=['Anime', 'Dibujos', 'Series', 'Película'], width=12, state='readonly')
        self.combo_tipo.pack(side='left', padx=2)
        self.combo_tipo.set('Anime')  # Valor por defecto
        
        ttk.Label(frame_tecnicos, text="Href:").pack(side='left', padx=(10, 0))
        self.entry_href = ttk.Entry(frame_tecnicos, width=35)
        self.entry_href.pack(side='left', fill='x', expand=True, padx=2)
        
        
        
        # Ficha Técnica - Campos visibles
        frame_ficha_tecnica = ttk.LabelFrame(frame_izq, text="📋 Ficha Técnica", padding="3")
        frame_ficha_tecnica.pack(fill='x', pady=5)
        
        # Fila 1: Idioma | Subtítulos | Calidad | Resolución
        frame_ficha1 = ttk.Frame(frame_ficha_tecnica)
        frame_ficha1.pack(fill='x', pady=1)
        
        ttk.Label(frame_ficha1, text="Idioma:").pack(side='left')
        self.entry_idioma = ttk.Entry(frame_ficha1, width=12)
        self.entry_idioma.pack(side='left', padx=2)
        
        ttk.Label(frame_ficha1, text="Subs:").pack(side='left')
        self.entry_subtitulos = ttk.Entry(frame_ficha1, width=12)
        self.entry_subtitulos.pack(side='left', padx=2)
        
        ttk.Label(frame_ficha1, text="Calidad:").pack(side='left')
        self.entry_calidad = ttk.Entry(frame_ficha1, width=12)
        self.entry_calidad.pack(side='left', padx=2)
        
        ttk.Label(frame_ficha1, text="Resol:").pack(side='left')
        self.entry_resolucion = ttk.Entry(frame_ficha1, width=12)
        self.entry_resolucion.pack(side='left', padx=2)
        
        # Fila 2: Formato | Peso/Cap
        frame_ficha2 = ttk.Frame(frame_ficha_tecnica)
        frame_ficha2.pack(fill='x', pady=1)
        
        ttk.Label(frame_ficha2, text="Formato:").pack(side='left')
        self.entry_formato = ttk.Entry(frame_ficha2, width=15)
        self.entry_formato.pack(side='left', padx=2)
        
        ttk.Label(frame_ficha2, text="Peso/Cap:").pack(side='left')
        self.entry_peso = ttk.Entry(frame_ficha2, width=20)
        self.entry_peso.pack(side='left', fill='x', expand=True, padx=2)
        
        # Ficha técnica colapsable (adicional)
        self.frame_ficha = ttk.LabelFrame(frame_editor, text="Ficha Técnica ▼ (click para expandir)", padding="3")
        self.frame_ficha.pack(fill='x', pady=(5, 0))
        self.frame_ficha.bind('<Button-1>', self.toggle_ficha)
        self.frame_ficha_contenido = ttk.Frame(self.frame_ficha)
        # No mostrar contenido inicialmente
        
        self.entries_ficha = {}
        campos_ficha = [
            ('idioma', 'Idioma'), ('subtitulos', 'Subs'), ('calidad', 'Calidad'),
            ('resolucion', 'Resol.'), ('formato', 'Formato'), ('peso', 'Peso/Cap')
        ]
        
        for i, (campo, label) in enumerate(campos_ficha):
            row = i // 4
            col = (i % 4) * 2
            ttk.Label(self.frame_ficha_contenido, text=f"{label}:", font=('Arial', 8)).grid(row=row, column=col, sticky='e', padx=2)
            entry = ttk.Entry(self.frame_ficha_contenido, width=18, font=('Arial', 8))
            entry.grid(row=row, column=col+1, sticky='ew', padx=2, pady=1)
            self.entries_ficha[campo] = entry
        
        # Sección para importar desde URL
        frame_import = ttk.LabelFrame(frame_editor, text="📥 Importar desde URL", padding="3")
        frame_import.pack(fill='x', pady=(5, 0))
        
        frame_import_input = ttk.Frame(frame_import)
        frame_import_input.pack(fill='x', pady=2)
        
        ttk.Label(frame_import_input, text="URL:").pack(side='left')
        self.entry_import_url = ttk.Entry(frame_import_input, width=60)
        self.entry_import_url.pack(side='left', fill='x', expand=True, padx=2)
        ttk.Button(frame_import_input, text="📥 Extraer", command=self.extraer_info_url, width=10).pack(side='left', padx=2)
        
        # Botones debajo del campo URL
        frame_import_botones = ttk.Frame(frame_import)
        frame_import_botones.pack(fill='x', pady=2)
        ttk.Button(frame_import_botones, text="➕ Añadir al catálogo", command=self.nueva_serie, width=18).pack(side='left', padx=2)
        ttk.Button(frame_import_botones, text="🧹 Limpiar campos", command=self.limpiar_todos_los_campos, width=16).pack(side='left', padx=2)
        
        # Status bar
        self.label_status = ttk.Label(self.root, text="Selecciona una serie", relief='sunken', font=('Arial', 9))
        self.label_status.pack(fill='x', side='bottom')
        
        self.ficha_expandida = False
    
    def toggle_ficha(self, event=None):
        """Expandir/colapsar ficha técnica"""
        if self.ficha_expandida:
            self.frame_ficha_contenido.pack_forget()
            self.frame_ficha.config(text="Ficha Técnica ▼ (click para expandir)")
        else:
            self.frame_ficha_contenido.pack(fill='x', expand=True)
            self.frame_ficha.config(text="Ficha Técnica ▲ (click para colapsar)")
        self.ficha_expandida = not self.ficha_expandida
    
    def crear_tab_categoria(self, tab, cat_name):
        """Crear pestaña de categoría"""
        frame_lista = ttk.Frame(tab)
        frame_lista.pack(fill='both', expand=True)
        
        # Búsqueda local
        frame_busq = ttk.Frame(frame_lista)
        frame_busq.pack(fill='x', pady=2)
        ttk.Label(frame_busq, text="Filtrar:").pack(side='left')
        entry_filtro = ttk.Entry(frame_busq, width=30)
        entry_filtro.pack(side='left', padx=3)
        entry_filtro.bind('<KeyRelease>', lambda e, c=cat_name: self.filtrar(e, c))
        
        # Tree compacto
        cols = ('nombre', 'year', 'genero')
        tree = ttk.Treeview(frame_lista, columns=cols, show='headings', height=18, selectmode='extended')
        
        tree.heading('nombre', text='Nombre')
        tree.heading('year', text='Año')
        tree.heading('genero', text='Género')
        
        tree.column('nombre', width=350)
        tree.column('year', width=50)
        tree.column('genero', width=150)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        tree.bind('<<TreeviewSelect>>', lambda e, c=cat_name: self.seleccionar_serie(e, c))
        
        self.trees[cat_name] = tree
        self.cargar_series(cat_name)
    
    def cargar_series(self, cat_name):
        """Cargar series en el tree"""
        tree = self.trees[cat_name]
        series = self.categorias[cat_name]
        
        for item in tree.get_children():
            tree.delete(item)
        
        for serie in series:
            nombre = self.limpiar_nombre(serie.get('name', ''))
            if len(nombre) > 45:
                nombre = nombre[:45] + "..."
            
            year = str(serie.get('year', ''))
            genero = serie.get('genre', serie.get('specificGenre', 'N/A'))
            if len(genero) > 20:
                genero = genero[:20] + "..."
            
            tree.insert('', 'end', values=(nombre, year, genero))
    
    def filtrar(self, event, cat_name):
        """Filtrar series"""
        tree = self.trees[cat_name]
        series = self.categorias[cat_name]
        termino = event.widget.get().lower().strip()
        
        for item in tree.get_children():
            tree.delete(item)
        
        # Guardar series filtradas para selección correcta
        series_filtradas = []
        
        for serie in series:
            nombre_completo = serie.get('name', '').lower()
            nombre_limpio = self.limpiar_nombre(serie.get('name', '')).lower()
            
            if termino and termino not in nombre_completo and termino not in nombre_limpio:
                continue
            
            series_filtradas.append(serie)
            
            nombre = self.limpiar_nombre(serie.get('name', ''))
            if len(nombre) > 45:
                nombre = nombre[:45] + "..."
            
            year = str(serie.get('year', ''))
            genero = serie.get('genre', serie.get('specificGenre', 'N/A'))
            if len(genero) > 20:
                genero = genero[:20] + "..."
            
            tree.insert('', 'end', values=(nombre, year, genero))
        
        # Guardar referencia a series filtradas para esta categoría
        self.series_filtradas = {cat_name: series_filtradas}
    
    def seleccionar_serie(self, event, cat_name):
        """Seleccionar serie"""
        tree = self.trees[cat_name]
        seleccion = tree.selection()
        if not seleccion:
            return
        
        index = tree.index(seleccion[0])
        
        # Si hay filtro activo, usar series filtradas
        if hasattr(self, 'series_filtradas') and cat_name in self.series_filtradas:
            series = self.series_filtradas[cat_name]
        else:
            series = self.categorias[cat_name]
        
        # Usar índice directamente
        if index < len(series):
            self.serie_actual = series[index]
        else:
            return
        
        self.cargar_serie()
    
    def cargar_serie(self):
        """Cargar serie en formulario"""
        if not hasattr(self, 'serie_actual'):
            return
        
        s = self.serie_actual
        
        # Campos principales
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, s.get('name', ''))
        
        self.entry_year.delete(0, tk.END)
        self.entry_year.insert(0, str(s.get('year', '')))
        
        self.combo_categoria.set(s.get('_categoria', 'anime').capitalize())
        
        # Géneros
        generos = s.get('genre', s.get('specificGenre', ''))
        self.entry_generos.delete(0, tk.END)
        self.entry_generos.insert(0, generos)
        self.actualizar_primer_genero()
        
        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, s.get('imagen_url', s.get('imagen', '')))
        
        self.text_sinopsis.delete(1.0, tk.END)
        self.text_sinopsis.insert(1.0, s.get('sinopsis', '')[:1000])
        
        # URLs adicionales
        self.entry_url.delete(0, tk.END)
        self.entry_url.insert(0, s.get('url', ''))
        
        self.entry_rentry.delete(0, tk.END)
        self.entry_rentry.insert(0, s.get('rentry_url', ''))
        
        # Campos técnicos
        self.combo_tipo.set(s.get('type', 'Anime'))
        
        self.entry_href.delete(0, tk.END)
        self.entry_href.insert(0, s.get('href', ''))
        
        # Ficha técnica - Campos visibles
        ficha = s.get('ficha_tecnica', {})
        self.entry_idioma.delete(0, tk.END)
        self.entry_idioma.insert(0, ficha.get('idioma', ''))
        
        self.entry_subtitulos.delete(0, tk.END)
        self.entry_subtitulos.insert(0, ficha.get('subtitulos', ''))
        
        self.entry_calidad.delete(0, tk.END)
        self.entry_calidad.insert(0, ficha.get('calidad', ''))
        
        self.entry_resolucion.delete(0, tk.END)
        self.entry_resolucion.insert(0, ficha.get('resolucion', ''))
        
        self.entry_formato.delete(0, tk.END)
        self.entry_formato.insert(0, ficha.get('formato', ''))
        
        self.entry_peso.delete(0, tk.END)
        self.entry_peso.insert(0, ficha.get('peso', ''))
        
        # Ficha técnica colapsable (sincronizada)
        for campo, entry in self.entries_ficha.items():
            entry.delete(0, tk.END)
            entry.insert(0, ficha.get(campo, ''))
        
        self.label_status.config(text=f"Editando: {self.limpiar_nombre(s.get('name', ''))[:40]}")
    
    def actualizar_primer_genero(self, event=None):
        """Actualizar primer género"""
        generos = self.entry_generos.get().strip()
        primer = generos.split(',')[0].strip().capitalize() if generos else 'N/A'
        self.label_primer_genero.config(text=primer[:12])
    
    def aplicar_cambios(self):
        """Aplicar cambios"""
        if not hasattr(self, 'serie_actual'):
            messagebox.showwarning("Atención", "Selecciona una serie")
            return
        
        s = self.serie_actual
        
        # Guardar género anterior
        genero_anterior = s.get('genre', s.get('specificGenre', 'Sin Género'))
        if isinstance(genero_anterior, list):
            genero_anterior = ', '.join(genero_anterior) if genero_anterior else 'Sin Género'
        if isinstance(genero_anterior, str):
            genero_anterior = genero_anterior.split(',')[0].strip().capitalize()
        
        s['name'] = self.entry_nombre.get().strip()
        try:
            s['year'] = int(self.entry_year.get().strip())
        except:
            pass
        
        # Géneros con filtro de Animación y normalización
        generos = self.normalizar_genero(self.entry_generos.get().strip())
        generos = self.filtrar_animacion(generos)
        s['genre'] = generos
        s['imagen_url'] = self.entry_imagen.get().strip()
        s['sinopsis'] = self.text_sinopsis.get(1.0, tk.END).strip()
        
        # URLs adicionales
        s['url'] = self.entry_url.get().strip()
        s['rentry_url'] = self.entry_rentry.get().strip()
        
        # Campos técnicos
        s['type'] = self.combo_tipo.get()
        s['href'] = self.entry_href.get().strip()
        
        # Verificar si cambió la categoría
        categoria_nueva_key = self.combo_categoria.get()  # 'Anime', 'Dibujos', etc.
        categoria_nueva = categoria_nueva_key.lower()  # 'anime', 'dibujos', etc.
        categoria_actual = s.get('_categoria', '').lower()
        categoria_actual_key = categoria_actual.capitalize() if categoria_actual else ''
        
        if categoria_nueva != categoria_actual and categoria_nueva in ['anime', 'dibujos', 'peliculas', 'series']:
            # Mover la serie a la nueva categoría
            if categoria_actual_key in self.categorias and s in self.categorias[categoria_actual_key]:
                self.categorias[categoria_actual_key].remove(s)
            if categoria_nueva_key in self.categorias:
                self.categorias[categoria_nueva_key].append(s)
                s['_categoria'] = categoria_nueva
                self.label_status.config(text=f"✅ Serie movida a {categoria_nueva.upper()}")
                self.actualizar_contadores_pestanas()
        
        # Géneros originales (mismo valor que géneros, también filtrado)
        s['originalGenre'] = generos
        s['specificGenre'] = generos
        
        # Ficha técnica - Campos visibles y colapsables
        if 'ficha_tecnica' not in s:
            s['ficha_tecnica'] = {}
        
        # Guardar desde campos visibles
        s['ficha_tecnica']['idioma'] = self.entry_idioma.get().strip()
        s['ficha_tecnica']['subtitulos'] = self.entry_subtitulos.get().strip()
        s['ficha_tecnica']['calidad'] = self.entry_calidad.get().strip()
        s['ficha_tecnica']['resolucion'] = self.entry_resolucion.get().strip()
        s['ficha_tecnica']['formato'] = self.entry_formato.get().strip()
        s['ficha_tecnica']['peso'] = self.entry_peso.get().strip()
        
        # Sincronizar con campos colapsables
        for campo, entry in self.entries_ficha.items():
            s['ficha_tecnica'][campo] = entry.get().strip()
        
        # Detectar nuevo género
        genero_nuevo = s['genre'].split(',')[0].strip().capitalize() if s['genre'] else 'Sin Género'
        
        # Guardar automáticamente en JSON
        try:
            data_actualizada = {}
            for cat_name, items in self.categorias.items():
                items_limpios = []
                for item in items:
                    item_limpio = {k: v for k, v in item.items() if k != '_categoria'}
                    items_limpios.append(item_limpio)
                data_actualizada[cat_name.lower()] = items_limpios
            
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(data_actualizada, f, ensure_ascii=False, indent=2)
            
            self.data = data_actualizada
            
            # Restaurar _categoria
            for cat_name, items in self.categorias.items():
                for item in items:
                    item['_categoria'] = cat_name.lower()
            
            self.label_status.config(text=f"✅ Cambios aplicados y guardados")
        except Exception as e:
            self.label_status.config(text=f"⚠️ Cambios aplicados pero error al guardar: {e}")
        
        self.refrescar_todos()
        
        # Si cambió el género y estamos en modo géneros, cambiar a esa pestaña
        if genero_nuevo != genero_anterior and self.modo_actual == 'generos':
            self.cambiar_a_pestaña_genero(genero_nuevo)
    
    def cambiar_a_pestaña_genero(self, genero):
        """Cambiar a la pestaña del género especificado"""
        # Normalizar el género buscado
        genero = genero.capitalize() if genero else 'Sin Género'
        
        # Si el género cambió, recalcular géneros y recrear pestañas
        self.recalcular_generos()
        
        # Recrear tabs con los nuevos géneros
        self.cambiar_modo()
        self.cambiar_modo()  # Volver a géneros para recargar con datos actualizados
        
        # Ahora buscar la pestaña del nuevo género
        if genero in self.tabs:
            self.notebook.select(self.tabs[genero])
            self.label_status.config(text=f"✅ Cambiado a: {genero}")
        elif 'Otros' in self.tabs:
            self.notebook.select(self.tabs['Otros'])
            self.label_status.config(text=f"✅ Cambiado a: Otros ({genero})")
    
    def recalcular_generos(self):
        """Recalcular organización por géneros después de cambios"""
        # Reorganizar por género (primer género de cada serie)
        self.generos = {}
        for cat_name, items in self.categorias.items():
            for item in items:
                # Obtener género, manejando casos donde genre es lista o está vacío
                genero = item.get('genre', '')
                if isinstance(genero, list):
                    genero = ', '.join(genero) if genero else ''
                if not genero or (isinstance(genero, str) and genero.strip() == ''):
                    genero = item.get('specificGenre', 'Sin Género')
                
                genero_completo = genero if genero else 'Sin Género'
                
                if isinstance(genero_completo, str):
                    primer_genero = genero_completo.split(',')[0].strip()
                    if not primer_genero:
                        primer_genero = 'Sin Género'
                    primer_genero = primer_genero.capitalize()
                else:
                    primer_genero = 'Sin Género'
                
                if primer_genero not in self.generos:
                    self.generos[primer_genero] = []
                self.generos[primer_genero].append(item)
        
        # Reordenar géneros por cantidad
        self.generos_ordenados = sorted(self.generos.items(), key=lambda x: len(x[1]), reverse=True)
    
    def actualizar_contadores_pestanas(self):
        """Actualizar los números en los títulos de las pestañas"""
        if self.modo_actual == 'categorias':
            for i, cat_name in enumerate(['Anime', 'Dibujos', 'Peliculas', 'Series']):
                if cat_name in self.tabs:
                    self.notebook.tab(i, text=f"{cat_name} ({len(self.categorias[cat_name])})")
    
    def refrescar_todos(self):
        """Refrescar todos los trees"""
        if self.modo_actual == 'categorias':
            for cat_name in self.categorias:
                self.cargar_series(cat_name)
            self.actualizar_contadores_pestanas()
        else:
            # Modo géneros
            for genero in self.generos:
                if genero in self.trees:
                    self.cargar_series_genero(genero)
            if 'Otros' in self.trees:
                otros = [g for g, _ in self.generos_ordenados[12:]]
                self.cargar_series_otros(otros)
    
    def siguiente_serie(self):
        """Siguiente serie"""
        if not hasattr(self, 'serie_actual'):
            return
        
        cat = self.serie_actual.get('_categoria', '').capitalize()
        tree = self.trees.get(cat)
        if not tree:
            return
        
        seleccion = tree.selection()
        if seleccion:
            siguiente = tree.next(seleccion[0])
            if siguiente:
                tree.selection_set(siguiente)
                tree.see(siguiente)
    
    def buscar_global(self, event=None):
        """Buscar global"""
        termino = self.entry_buscar.get().lower().strip()
        if not termino:
            return
        
        for cat_name in self.categorias:
            series = self.categorias[cat_name]
            for i, serie in enumerate(series):
                if termino in serie.get('name', '').lower():
                    # Verificar si la pestaña existe antes de acceder
                    if cat_name in self.tabs:
                        self.notebook.select(self.tabs[cat_name])
                        tree = self.trees[cat_name]
                        # Seleccionar y ver
                        items = tree.get_children()
                        if i < len(items):
                            tree.selection_set(items[i])
                            tree.see(items[i])
                            self.serie_actual = serie
                            self.cargar_serie()
                            return
        
        self.label_status.config(text=f"No encontrado: {termino}")
    
    def eliminar_serie(self):
        """Eliminar la serie seleccionada del catálogo"""
        if not hasattr(self, 'serie_actual') or not self.serie_actual:
            messagebox.showwarning("Atención", "Selecciona una serie para eliminar")
            return
        
        s = self.serie_actual
        nombre = self.limpiar_nombre(s.get('name', 'Sin nombre'))
        categoria = s.get('_categoria', '').capitalize()
        
        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar eliminación", 
                                   f"¿Eliminar '{nombre}' de {categoria}?\n\nEsta acción no se puede deshacer."):
            return
        
        # Eliminar de la categoría
        if categoria in self.categorias and s in self.categorias[categoria]:
            self.categorias[categoria].remove(s)
            
            # Limpiar selección
            self.serie_actual = None
            self.limpiar_todos_los_campos()
            
            # Refrescar y guardar
            self.refrescar_todos()
            self.guardar_silencioso()
            
            self.label_status.config(text=f"🗑️ '{nombre[:30]}' eliminado de {categoria}", foreground='red')
        else:
            messagebox.showerror("Error", "No se pudo encontrar la serie en la categoría")
    
    def guardar_silencioso(self):
        """Guardar JSON sin mostrar mensajes"""
        try:
            data_actualizada = {}
            for cat_name, items in self.categorias.items():
                items_limpios = []
                for item in items:
                    item_limpio = {k: v for k, v in item.items() if k != '_categoria'}
                    items_limpios.append(item_limpio)
                data_actualizada[cat_name.lower()] = items_limpios
            
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(data_actualizada, f, ensure_ascii=False, indent=2)
            
            self.data = data_actualizada
            
            # Restaurar _categoria
            for cat_name, items in self.categorias.items():
                for item in items:
                    item['_categoria'] = cat_name.lower()
        except Exception as e:
            self.label_status.config(text=f"⚠️ Error al guardar: {e}", foreground='red')

    def guardar(self):
        """Guardar JSON"""
        try:
            # Aplicar cambios actuales del formulario si hay una serie seleccionada
            if hasattr(self, 'serie_actual') and self.serie_actual:
                self.aplicar_cambios()
            
            # Reconstruir data desde categorías (para reflejar cambios de categoría)
            data_actualizada = {}
            for cat_name, items in self.categorias.items():
                # Limpiar el campo _categoria antes de guardar
                items_limpios = []
                for item in items:
                    item_limpio = {k: v for k, v in item.items() if k != '_categoria'}
                    items_limpios.append(item_limpio)
                # Guardar con clave en minúsculas (anime, dibujos, peliculas, series)
                data_actualizada[cat_name.lower()] = items_limpios
            
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(data_actualizada, f, ensure_ascii=False, indent=2)
            
            # Actualizar self.data
            self.data = data_actualizada
            
            # Restaurar _categoria para uso interno
            for cat_name, items in self.categorias.items():
                for item in items:
                    item['_categoria'] = cat_name.lower()
            
            messagebox.showinfo("Éxito", "✅ Guardado")
            self.label_status.config(text="💾 JSON guardado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def regenerar_html(self):
        """Regenerar HTML"""
        import subprocess
        
        if not messagebox.askyesno("Confirmar", "¿Regenerar HTML?"):
            return
        
        try:
            self.label_status.config(text="🔄 Regenerando...")
            self.root.update()
            
            import os
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            resultado = subprocess.run(
                ['python', '-W', 'ignore', r'c:\Users\Rafael\CascadeProjects\windsurf-project\generar_html_foroactivo.py'],
                capture_output=True, text=True, timeout=60, encoding='utf-8', errors='ignore',
                env=env, shell=False
            )
            
            if resultado.returncode == 0:
                messagebox.showinfo("Éxito", "✅ HTML regenerado")
                self.label_status.config(text="✅ HTML listo")
            else:
                error_msg = resultado.stderr[:300] if resultado.stderr else "Error desconocido"
                messagebox.showerror("Error", f"Código: {resultado.returncode}\n{error_msg}")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def edicion_masiva(self):
        """Ventana para edición masiva de géneros"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Edición Masiva de Géneros")
        ventana.geometry("800x600")
        
        ttk.Label(ventana, text="📝 Edición Masiva", font=('Arial', 12, 'bold')).pack(pady=5)
        
        instrucciones = """Formato:
Nombre Serie (Año)  ← línea impar
Género1, Género2, Género3  ← línea par (géneros separados por coma)

Ejemplo:
Calle Dálmatas 101 (2019)
Comedia, Aventura, Infantil, Familiar
Pack Películas Dragon Ball (1986)
Acción, Aventura, Artes marciales, Fantasía, Shōnen"""
        
        ttk.Label(ventana, text=instrucciones, justify='left', foreground='gray').pack(pady=5)
        
        # Text area
        ttk.Label(ventana, text="Pega aquí tu lista:").pack(anchor='w', padx=10)
        text_area = scrolledtext.ScrolledText(ventana, width=90, height=20, wrap=tk.WORD)
        text_area.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Resultado - Resumen
        frame_result = ttk.Frame(ventana)
        frame_result.pack(fill='x', padx=10, pady=5)
        
        label_result = ttk.Label(frame_result, text="Listo para procesar")
        label_result.pack(side='left')
        
        # Área para mostrar no encontrados
        ttk.Label(ventana, text="❌ Series NO encontradas (para revisar):", font=('Arial', 10, 'bold'), foreground='red').pack(anchor='w', padx=10, pady=(10, 0))
        text_no_encontrados = scrolledtext.ScrolledText(ventana, width=90, height=10, wrap=tk.WORD)
        text_no_encontrados.pack(fill='both', expand=True, padx=10, pady=5)
        text_no_encontrados.insert(1.0, "Aquí aparecerán las series que no se pudieron encontrar...")
        text_no_encontrados.config(state='disabled')  # Solo lectura inicialmente
        
        def copiar_no_encontrados():
            """Copiar lista de no encontrados al portapapeles"""
            contenido = text_no_encontrados.get(1.0, tk.END).strip()
            if contenido and contenido != "Aquí aparecerán las series que no se pudieron encontrar...":
                ventana.clipboard_clear()
                ventana.clipboard_append(contenido)
                label_result.config(text="📋 Lista copiada al portapapeles")
        
        def procesar():
            contenido = text_area.get(1.0, tk.END).strip()
            if not contenido:
                label_result.config(text="⚠️ No hay contenido para procesar")
                return
            
            # Mejor parsing: filtrar líneas vacías y crear pares
            lineas_raw = contenido.split('\n')
            lineas = []
            for l in lineas_raw:
                l_strip = l.strip()
                if l_strip:
                    lineas.append(l_strip)
            
            # Debug: mostrar cuántas líneas se detectaron
            print(f"DEBUG - Líneas detectadas: {len(lineas)}")
            
            # Parsear pares nombre->género
            correcciones = {}
            i = 0
            while i < len(lineas):
                nombre = lineas[i]
                if i + 1 < len(lineas):
                    generos = lineas[i + 1]
                    correcciones[nombre] = generos
                    print(f"DEBUG - Par {len(correcciones)}: '{nombre[:50]}' -> '{generos[:50]}'")
                    i += 2
                else:
                    print(f"DEBUG - Línea sin pareja: '{nombre[:50]}'")
                    i += 1
            
            if not correcciones:
                label_result.config(text="❌ No se encontraron pares válidos\nFormato: Nombre (línea impar) + Géneros (línea par)")
                return
            
            label_result.config(text=f"🔍 Buscando {len(correcciones)} series en el catálogo...")
            ventana.update()
            
            # Aplicar correcciones con mejor coincidencia
            actualizados = 0
            no_encontrados = []
            debug_info = []
            
            # Crear índice de series para búsqueda más rápida
            series_index = {}
            for cat_name, series in self.categorias.items():
                for serie in series:
                    nombre_limpio = self.limpiar_nombre(serie.get('name', '')).lower()
                    if nombre_limpio not in series_index:
                        series_index[nombre_limpio] = []
                    series_index[nombre_limpio].append((cat_name, serie))
            
            for nombre_txt, generos_txt in correcciones.items():
                nombre_buscado = self.limpiar_nombre(nombre_txt).lower()
                encontrado = False
                
                # Primero: coincidencia exacta
                if nombre_buscado in series_index:
                    for cat_name, serie in series_index[nombre_buscado]:
                        serie['genre'] = generos_txt
                        actualizados += 1
                        encontrado = True
                        debug_info.append(f"✅ EXACTO: '{nombre_txt[:40]}'")
                        break
                
                # Segundo: coincidencia parcial (contiene)
                if not encontrado:
                    for nombre_catalogo, series_list in series_index.items():
                        if nombre_buscado in nombre_catalogo or nombre_catalogo in nombre_buscado:
                            for cat_name, serie in series_list:
                                serie['genre'] = generos_txt
                                actualizados += 1
                                encontrado = True
                                debug_info.append(f"✅ PARCIAL: '{nombre_txt[:40]}' -> '{serie.get('name', '')[:40]}'")
                                break
                        if encontrado:
                            break
                
                if not encontrado:
                    no_encontrados.append(nombre_txt)
                    debug_info.append(f"❌ NO ENCONTRADO: '{nombre_txt[:40]}' (limpio: '{nombre_buscado[:40]}')")
            
            # Mostrar resultado resumido
            resultado = f"✅ Actualizados: {actualizados} | ❌ No encontrados: {len(no_encontrados)}"
            label_result.config(text=resultado)
            
            # Mostrar no encontrados en el área de texto
            text_no_encontrados.config(state='normal')
            text_no_encontrados.delete(1.0, tk.END)
            if no_encontrados:
                # Formato: nombre + género en líneas separadas para fácil corrección
                for nombre in no_encontrados:
                    generos = correcciones.get(nombre, '')
                    text_no_encontrados.insert(tk.END, f"{nombre}\n{generos}\n\n")
            else:
                text_no_encontrados.insert(1.0, "🎉 ¡Todas las series fueron encontradas!")
            text_no_encontrados.config(state='disabled')
            
            # Guardar debug completo en archivo
            with open('debug_edicion_masiva.txt', 'w', encoding='utf-8') as f:
                f.write(f"Total: {len(correcciones)} series en input\n")
                f.write(f"Actualizadas: {actualizados}\n")
                f.write(f"No encontradas: {len(no_encontrados)}\n\n")
                f.write("Detalle completo:\n")
                for info in debug_info:
                    f.write(info + "\n")
                if no_encontrados:
                    f.write("\n\nNo encontrados (con géneros):\n")
                    for nombre in no_encontrados:
                        generos = correcciones.get(nombre, '')
                        f.write(f"{nombre}\n{generos}\n\n")
            
            print(f"\nDEBUG completo guardado en: debug_edicion_masiva.txt")
            
            if actualizados > 0:
                self.refrescar_todos()
        
        # Botones
        frame_botones = ttk.Frame(ventana)
        frame_botones.pack(pady=10)
        
        ttk.Button(frame_botones, text="✅ Procesar y Aplicar", command=procesar, width=20).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="📋 Copiar No Encontrados", command=copiar_no_encontrados, width=22).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="❌ Cerrar", command=ventana.destroy, width=12).pack(side='left', padx=5)
    
    def copiar_lista(self):
        """Copiar nombres y años de series seleccionadas al portapapeles"""
        # Obtener la pestaña actual
        pestaña_actual = self.notebook.select()
        pestaña_nombre = None
        for nombre, tab in self.tabs.items():
            if str(tab) == str(pestaña_actual):
                pestaña_nombre = nombre
                break
        
        if not pestaña_nombre:
            messagebox.showwarning("Atención", "Selecciona una pestaña")
            return
        
        tree = self.trees[pestaña_nombre]
        seleccion = tree.selection()
        
        if not seleccion:
            # Si no hay selección, copiar todas las visibles
            seleccion = tree.get_children()
        
        if not seleccion:
            messagebox.showwarning("Atención", "No hay series para copiar")
            return
        
        # Determinar fuente de datos según el modo
        if self.modo_actual == 'categorias':
            series_fuente = self.categorias.get(pestaña_nombre, [])
        else:
            # Modo géneros
            if pestaña_nombre == 'Otros':
                # Combinar todos los géneros restantes
                otros_generos = [g for g, _ in self.generos_ordenados[12:]]
                series_fuente = []
                for g in otros_generos:
                    series_fuente.extend(self.generos[g])
            else:
                series_fuente = self.generos.get(pestaña_nombre, [])
        
        # Construir lista
        lineas = []
        for item in seleccion:
            valores = tree.item(item)['values']
            if valores:
                nombre, year = valores[0], valores[1]
                # Obtener nombre completo de la serie
                index = tree.index(item)
                if index < len(series_fuente):
                    nombre_completo = series_fuente[index].get('name', '')
                    # Limpiar nombre para mostrar solo título y año
                    nombre_limpio = self.limpiar_nombre(nombre_completo)
                    lineas.append(f"{nombre_limpio} ({year})")
        
        # Copiar al portapapeles
        texto = '\n'.join(lineas)
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        
        # Mostrar mensaje
        messagebox.showinfo("Copiado", f"✅ {len(lineas)} series copiadas al portapapeles\n\nPrimeras 3 líneas:\n{texto[:150]}...")
    
    def cambiar_modo(self):
        """Cambiar entre vista por categorías y vista por géneros"""
        # Limpiar notebook actual
        for tab in list(self.tabs.values()):
            for widget in tab.winfo_children():
                widget.destroy()
            self.notebook.forget(tab)
        
        self.tabs = {}
        self.trees = {}
        
        if self.modo_actual == 'categorias':
            # Cambiar a modo géneros
            self.modo_actual = 'generos'
            self.btn_cambiar_modo.config(text="🎬 Ver por Categorías")
            self.crear_tabs_generos()
        else:
            # Cambiar a modo categorías
            self.modo_actual = 'categorias'
            self.btn_cambiar_modo.config(text="🎭 Ver por Géneros")
            self.crear_tabs_categorias()
    
    def crear_tabs_generos(self):
        """Crear pestañas por géneros (top 12 + Otros)"""
        generos_principales = self.generos_ordenados[:12]
        otros_generos = [g for g, _ in self.generos_ordenados[12:]]
        
        for genero, series in generos_principales:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"{genero} ({len(series)})")
            self.tabs[genero] = tab
            self.crear_tab_genero(tab, genero)
        
        if otros_generos:
            tab_otros = ttk.Frame(self.notebook)
            otros_series = []
            for g in otros_generos:
                otros_series.extend(self.generos[g])
            self.notebook.add(tab_otros, text=f"Otros ({len(otros_series)})")
            self.tabs['Otros'] = tab_otros
            self.crear_tab_otros(tab_otros, otros_generos)
    
    def crear_tabs_categorias(self):
        """Crear pestañas por categorías"""
        for cat_name in ['Anime', 'Dibujos', 'Peliculas', 'Series']:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"{cat_name} ({len(self.categorias[cat_name])})")
            self.tabs[cat_name] = tab
            self.crear_tab_categoria(tab, cat_name)
    
    def crear_tab_genero(self, tab, genero):
        """Crear pestaña para un género"""
        frame_lista = ttk.Frame(tab)
        frame_lista.pack(fill='both', expand=True)
        
        frame_busq = ttk.Frame(frame_lista)
        frame_busq.pack(fill='x', pady=2)
        ttk.Label(frame_busq, text="Filtrar:").pack(side='left')
        entry_filtro = ttk.Entry(frame_busq, width=30)
        entry_filtro.pack(side='left', padx=3)
        entry_filtro.bind('<KeyRelease>', lambda e, g=genero: self.filtrar_genero(e, g))
        
        cols = ('nombre', 'cat', 'year', 'genero')
        tree = ttk.Treeview(frame_lista, columns=cols, show='headings', height=18, selectmode='extended')
        
        tree.heading('nombre', text='Nombre')
        tree.heading('cat', text='Cat')
        tree.heading('year', text='Año')
        tree.heading('genero', text='Géneros')
        
        tree.column('nombre', width=350)
        tree.column('cat', width=60)
        tree.column('year', width=50)
        tree.column('genero', width=200)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        tree.bind('<<TreeviewSelect>>', lambda e, g=genero: self.seleccionar_serie_genero(e, g))
        
        self.trees[genero] = tree
        self.cargar_series_genero(genero)
    
    def crear_tab_otros(self, tab, generos_list):
        """Crear pestaña para otros géneros"""
        frame_lista = ttk.Frame(tab)
        frame_lista.pack(fill='both', expand=True)
        
        frame_busq = ttk.Frame(frame_lista)
        frame_busq.pack(fill='x', pady=2)
        ttk.Label(frame_busq, text="Filtrar:").pack(side='left')
        entry_filtro = ttk.Entry(frame_busq, width=30)
        entry_filtro.pack(side='left', padx=3)
        entry_filtro.bind('<KeyRelease>', lambda e, gl=generos_list: self.filtrar_otros(e, gl))
        
        cols = ('nombre', 'cat', 'year', 'genero')
        tree = ttk.Treeview(frame_lista, columns=cols, show='headings', height=18, selectmode='extended')
        
        tree.heading('nombre', text='Nombre')
        tree.heading('cat', text='Cat')
        tree.heading('year', text='Año')
        tree.heading('genero', text='Género')
        
        tree.column('nombre', width=320)
        tree.column('cat', width=60)
        tree.column('year', width=50)
        tree.column('genero', width=130)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        tree.bind('<<TreeviewSelect>>', lambda e, gl=generos_list: self.seleccionar_serie_otros(e, gl))
        
        self.trees['Otros'] = tree
        self.cargar_series_otros(generos_list)
    
    def cargar_series_genero(self, genero):
        """Cargar series de un género"""
        tree = self.trees[genero]
        series = self.generos[genero]
        
        for item in tree.get_children():
            tree.delete(item)
        
        for serie in series:
            nombre = self.limpiar_nombre(serie.get('name', ''))
            if len(nombre) > 45:
                nombre = nombre[:45] + "..."
            
            cat = serie.get('_categoria', '')[:4].upper()
            year = str(serie.get('year', ''))
            genero_full = serie.get('genre', serie.get('specificGenre', 'N/A'))
            if len(genero_full) > 30:
                genero_full = genero_full[:30] + "..."
            
            tree.insert('', 'end', values=(nombre, cat, year, genero_full))
    
    def cargar_series_otros(self, generos_list):
        """Cargar series de otros géneros"""
        tree = self.trees['Otros']
        
        for item in tree.get_children():
            tree.delete(item)
        
        for genero in generos_list:
            for serie in self.generos[genero]:
                nombre = self.limpiar_nombre(serie.get('name', ''))
                if len(nombre) > 40:
                    nombre = nombre[:40] + "..."
                
                cat = serie.get('_categoria', '')[:4].upper()
                year = str(serie.get('year', ''))
                
                tree.insert('', 'end', values=(nombre, cat, year, genero))
    
    def filtrar_genero(self, event, genero):
        """Filtrar series en un género"""
        tree = self.trees[genero]
        series = self.generos[genero]
        termino = event.widget.get().lower().strip()
        
        for item in tree.get_children():
            tree.delete(item)
        
        for serie in series:
            nombre_completo = serie.get('name', '').lower()
            nombre_limpio = self.limpiar_nombre(serie.get('name', '')).lower()
            
            if termino and termino not in nombre_completo and termino not in nombre_limpio:
                continue
            
            nombre = self.limpiar_nombre(serie.get('name', ''))
            if len(nombre) > 45:
                nombre = nombre[:45] + "..."
            
            cat = serie.get('_categoria', '')[:4].upper()
            year = str(serie.get('year', ''))
            genero_full = serie.get('genre', serie.get('specificGenre', 'N/A'))
            if len(genero_full) > 30:
                genero_full = genero_full[:30] + "..."
            
            tree.insert('', 'end', values=(nombre, cat, year, genero_full))
    
    def filtrar_otros(self, event, generos_list):
        """Filtrar en otros géneros"""
        tree = self.trees['Otros']
        termino = event.widget.get().lower().strip()
        
        for item in tree.get_children():
            tree.delete(item)
        
        for genero in generos_list:
            for serie in self.generos[genero]:
                nombre_completo = serie.get('name', '').lower()
                nombre_limpio = self.limpiar_nombre(serie.get('name', '')).lower()
                
                if termino and termino not in nombre_completo and termino not in nombre_limpio:
                    continue
                
                nombre = self.limpiar_nombre(serie.get('name', ''))
                if len(nombre) > 40:
                    nombre = nombre[:40] + "..."
                
                cat = serie.get('_categoria', '')[:4].upper()
                year = str(serie.get('year', ''))
                
                tree.insert('', 'end', values=(nombre, cat, year, genero))
    
    def seleccionar_serie_genero(self, event, genero):
        """Seleccionar serie de un género"""
        tree = self.trees[genero]
        seleccion = tree.selection()
        if not seleccion:
            return
        
        index = tree.index(seleccion[0])
        series = self.generos[genero]
        
        if index < len(series):
            self.serie_actual = series[index]
            self.cargar_serie()
    
    def seleccionar_serie_otros(self, event, generos_list):
        """Seleccionar serie de otros géneros"""
        tree = self.trees['Otros']
        seleccion = tree.selection()
        if not seleccion:
            return
        
        index = tree.index(seleccion[0])
        
        todas = []
        for genero in generos_list:
            todas.extend(self.generos[genero])
        
        if index < len(todas):
            self.serie_actual = todas[index]
            self.cargar_serie()
    
    def actualizar_autocompletado(self, event=None):
        """Actualizar lista de sugerencias de autocompletado"""
        texto = self.entry_buscar.get().strip().lower()
        
        if len(texto) < 2:
            self.ocultar_sugerencias()
            return
        
        # Buscar coincidencias en todas las series
        sugerencias = []
        for cat_name, series in self.categorias.items():
            for serie in series:
                nombre = serie.get('name', '')
                nombre_limpio = self.limpiar_nombre(nombre).lower()
                
                # Buscar en nombre (tanto limpio como original)
                if texto in nombre_limpio or texto in nombre.lower():
                    sugerencias.append((nombre_limpio, serie))
                    continue
                
                # Buscar en todos los géneros de la serie
                generos_completos = []
                
                # Obtener todos los géneros posibles
                genre = serie.get('genre', '')
                specificGenre = serie.get('specificGenre', '')
                
                if genre:
                    if isinstance(genre, list):
                        generos_completos.extend(genre)
                    elif isinstance(genre, str):
                        generos_completos.extend([g.strip() for g in genre.split(',')])
                
                if specificGenre:
                    if isinstance(specificGenre, list):
                        generos_completos.extend(specificGenre)
                    elif isinstance(specificGenre, str):
                        generos_completos.extend([g.strip() for g in specificGenre.split(',')])
                
                # Buscar en cada género
                for genero_item in generos_completos:
                    if genero_item and texto in genero_item.lower():
                        sugerencias.append((nombre_limpio, serie))
                        break  # Ya agregamos esta serie, no seguir buscando en sus géneros
                
                if len(sugerencias) >= 10:  # Máximo 10 sugerencias
                    break
            if len(sugerencias) >= 10:
                break
        
        # Mostrar sugerencias
        self.lista_sugerencias.delete(0, tk.END)
        for nombre, serie in sugerencias[:10]:
            self.lista_sugerencias.insert(tk.END, nombre)
        
        if sugerencias:
            self.lista_sugerencias.pack(fill='x')
            self.lista_sugerencias.lift()
        else:
            self.ocultar_sugerencias()
    
    def seleccionar_siguiente_sugerencia(self, event=None):
        """Mover selección hacia abajo en la lista"""
        if not self.lista_sugerencias.winfo_viewable():
            return
        
        seleccion = self.lista_sugerencias.curselection()
        if seleccion:
            index = seleccion[0] + 1
            if index < self.lista_sugerencias.size():
                self.lista_sugerencias.selection_clear(0, tk.END)
                self.lista_sugerencias.selection_set(index)
                self.lista_sugerencias.see(index)
        else:
            if self.lista_sugerencias.size() > 0:
                self.lista_sugerencias.selection_set(0)
        return 'break'  # Prevenir comportamiento por defecto
    
    def seleccionar_anterior_sugerencia(self, event=None):
        """Mover selección hacia arriba en la lista"""
        if not self.lista_sugerencias.winfo_viewable():
            return
        
        seleccion = self.lista_sugerencias.curselection()
        if seleccion:
            index = seleccion[0] - 1
            if index >= 0:
                self.lista_sugerencias.selection_clear(0, tk.END)
                self.lista_sugerencias.selection_set(index)
                self.lista_sugerencias.see(index)
        return 'break'
    
    def aplicar_sugerencia(self, event=None):
        """Aplicar la sugerencia seleccionada"""
        seleccion = self.lista_sugerencias.curselection()
        if not seleccion:
            return
        
        nombre_seleccionado = self.lista_sugerencias.get(seleccion[0])
        self.entry_buscar.delete(0, tk.END)
        self.entry_buscar.insert(0, nombre_seleccionado)
        self.ocultar_sugerencias()
        
        # Buscar y seleccionar la serie
        self.buscar_global()
    
    def ocultar_sugerencias(self, event=None):
        """Ocultar la lista de sugerencias"""
        self.lista_sugerencias.pack_forget()
    
    def limpiar_todos_los_campos(self):
        """Limpiar todos los campos del formulario"""
        # Campos principales
        self.entry_nombre.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_generos.delete(0, tk.END)
        self.entry_imagen.delete(0, tk.END)
        self.text_sinopsis.delete(1.0, tk.END)
        self.entry_url.delete(0, tk.END)
        self.entry_rentry.delete(0, tk.END)
        self.combo_tipo.set('Anime')
        self.entry_href.delete(0, tk.END)
        
        # Resetear labels y combos
        self.combo_categoria.set('Anime')
        self.label_primer_genero.config(text='-')
        
        # Ficha técnica
        self.entry_idioma.delete(0, tk.END)
        self.entry_subtitulos.delete(0, tk.END)
        self.entry_calidad.delete(0, tk.END)
        self.entry_resolucion.delete(0, tk.END)
        self.entry_formato.delete(0, tk.END)
        self.entry_peso.delete(0, tk.END)
        
        # Colapsable
        for entry in self.entries_ficha.values():
            entry.delete(0, tk.END)
        
        self.label_status.config(text="🧹 Campos limpiados", foreground='blue')
    
    def login_foro(self, session):
        """Hacer login en el foro animezoneesp"""
        login_url = "https://animezoneesp.foroactivo.com/login"
        
        # Datos de login proporcionados por el usuario
        login_data = {
            'username': 'Admin',
            'password': '9XsBiygA2CpqgB9',
            'autologin': 'on',
            'redirect': '',
            'login': 'Conectarse'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://animezoneesp.foroactivo.com/login'
        }
        
        # Hacer login
        response = session.post(login_url, data=login_data, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Verificar si el login fue exitoso
        if 'logout' in response.text.lower() or 'desconectarse' in response.text.lower() or 'admin' in response.text.lower():
            print("DEBUG - Login exitoso")
            return True
        else:
            print(f"DEBUG - Login posiblemente fallido. Respuesta: {response.text[:500]}")
            return False
    
    def extraer_info_url(self):
        """Extraer información desde una URL (rentry.co u otra)"""
        url = self.entry_import_url.get().strip()
        if not url:
            messagebox.showwarning("Atención", "Introduce una URL")
            return
        
        # Primero limpiar todos los campos
        self.limpiar_todos_los_campos()
        
        try:
            self.label_status.config(text="📥 Extrayendo información...", foreground='blue')
            self.root.update()
            
            import requests
            from bs4 import BeautifulSoup
            from urllib.parse import urlparse
            
            # Crear una sesión para mantener cookies
            session = requests.Session()
            
            # Si es del foro animezoneesp, hacer login primero
            if 'animezoneesp.foroactivo.com' in url:
                print("DEBUG - Detectado foro animezoneesp, haciendo login...")
                self.login_foro(session)
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer texto de la página
            texto = soup.get_text(separator='\n', strip=True)
            
            # Procesar la información extraída (pasar soup para extraer imagen)
            datos, campos_encontrados = self.procesar_texto_extraido(texto, soup)
            
            # Guardar la URL
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(0, url)
            
            # Extraer solo el path para href
            parsed = urlparse(url)
            href = parsed.path
            if parsed.query:
                href += '?' + parsed.query
            if parsed.fragment:
                href += '#' + parsed.fragment
            self.entry_href.delete(0, tk.END)
            self.entry_href.insert(0, href)
            
            # Buscar rentry.co en la página
            rentry_match = re.search(r'https?://rentry\.co/[^\s\n"<>]+', texto, re.IGNORECASE)
            if rentry_match:
                rentry_url = rentry_match.group(0)
                self.entry_rentry.delete(0, tk.END)
                self.entry_rentry.insert(0, rentry_url)
                campos_encontrados.append(f"Rentry: {rentry_url[:40]}...")
            
            # Forzar actualización
            self.root.update_idletasks()
            
            # Mostrar resumen en status bar (sin pop-ups)
            if campos_encontrados:
                resumen = " | ".join(campos_encontrados[:4])  # Mostrar menos campos en status
                total_campos = len([k for k in datos.keys() if k != 'ficha_tecnica']) + len(datos.get('ficha_tecnica', {}))
                self.label_status.config(
                    text=f"📋 {total_campos} campos: {resumen[:80]}...",
                    foreground='green'
                )
            else:
                self.label_status.config(
                    text="⚠️ No se detectaron campos",
                    foreground='orange'
                )
            
        except Exception as e:
            self.label_status.config(text=f"❌ Error: {str(e)[:50]}", foreground='red')
            print(f"DEBUG - Error al extraer: {e}")
    
    def procesar_texto_info(self):
        """Procesar texto pegado manualmente"""
        texto = self.text_import.get(1.0, tk.END).strip()
        if not texto:
            self.label_status.config(text="⚠️ Pega texto para procesar", foreground='orange')
            return
        
        self.procesar_texto_extraido(texto)
        self.label_status.config(text="✅ Información procesada", foreground='green')
    
    def procesar_texto_extraido(self, texto, soup=None):
        """Procesar texto y extraer campos técnicos y de serie"""
        import re
        
        datos = {'ficha_tecnica': {}}
        campos_encontrados = []
        
        # Debug: mostrar primeros 800 caracteres del texto
        print(f"DEBUG - Texto a procesar:\n{texto[:800]}\n...")
        
        # ===== CAMPOS PRINCIPALES DE LA SERIE =====
        
        # Buscar nombre/título - MÉTODO MEJORADO PARA FOROACTIVO
        lineas = texto.split('\n')
        
        # 1. Intentar extraer de la primera línea (título del post)
        if lineas and len(lineas) > 0:
            primera_linea = lineas[0].strip()
            # Limpiar el formato típico de foroactivo: [Activo] Nombre (Año) [...]
            nombre_match = re.search(r'\[.*?\]\s*(.+?)\s*\(\d{4}\)', primera_linea)
            if nombre_match:
                nombre = nombre_match.group(1).strip()
                datos['name'] = nombre
                campos_encontrados.append(f"Nombre: {nombre[:50]}")
                print(f"DEBUG - Nombre extraído de primera línea: {nombre}")
        
        # 2. Buscar en h1 si está disponible
        if 'name' not in datos and soup:
            h1 = soup.find('h1')
            if h1:
                titulo_pagina = h1.get_text(strip=True)
                # Limpiar prefijos comunes
                titulo_limpio = re.sub(r'^(Re:)?\s*\[.*?\]\s*', '', titulo_pagina)
                # Extraer solo el nombre (antes del año si existe)
                nombre_match = re.search(r'^(.+?)\s*\(\d{4}\)', titulo_limpio)
                if nombre_match:
                    nombre = nombre_match.group(1).strip()
                    datos['name'] = nombre
                    campos_encontrados.append(f"Nombre: {nombre[:50]}")
                    print(f"DEBUG - Nombre extraído de h1: {nombre}")
                else:
                    if titulo_limpio and len(titulo_limpio) > 3 and len(titulo_limpio) < 100:
                        datos['name'] = titulo_limpio
                        campos_encontrados.append(f"Nombre: {titulo_limpio[:50]}")
        
        # 3. Buscar línea suelta que sea solo el nombre (como "La Tierra del Arcoiris")
        if 'name' not in datos:
            for linea in lineas[100:150]:  # Buscar en el área del contenido del post
                linea_limpia = linea.strip()
                if len(linea_limpia) > 5 and len(linea_limpia) < 60:
                    # Verificar que no sea un campo técnico
                    if not any(x in linea_limpia.lower() for x in ['género:', 'año:', 'idioma:', 'subtítulos:', 'formato:', 'calidad:', 'resolución:', 'peso:', 'sinopsis:']):
                        # Verificar que no sea menú
                        palabras_menu = ['índice', 'inicio', 'foro', 'buscar', 'login', 'registro', 'conectarse', 'desconectarse', 'perfil', 'mensajes', 'notificaciones']
                        if not any(p.lower() in linea_limpia.lower() for p in palabras_menu):
                            datos['name'] = linea_limpia
                            campos_encontrados.append(f"Nombre: {linea_limpia[:50]}")
                            print(f"DEBUG - Nombre extraído del contenido: {linea_limpia}")
                            break
        
        # Buscar año
        year_match = re.search(r'A[ñn]o:\s*(\d{4})|Year:\s*(\d{4})|Estreno:\s*(\d{4})|\((\d{4})\)|\b(\d{4})\b', texto, re.IGNORECASE)
        if year_match:
            year = next((g for g in year_match.groups() if g is not None), '')
            if year and 1950 < int(year) < 2030:
                datos['year'] = int(year)
                campos_encontrados.append(f"Año: {year}")
        
        # Buscar género
        genero_match = re.search(r'G[ée]nero[s]?:\s*([^\n]+)|Genre[s]?:\s*([^\n]+)|Categor[íi]a:\s*([^\n]+)', texto, re.IGNORECASE)
        if genero_match:
            genero = next((g for g in genero_match.groups() if g is not None), '').strip()
            if genero:
                # Normalizar separadores: reemplazar ' y ' por ', '
                genero = re.sub(r'\s+y\s+', ', ', genero, flags=re.IGNORECASE)
                # Normalizar: primera letra de cada género en mayúscula
                generos_list = [g.strip().capitalize() for g in genero.split(',')]
                genero = ', '.join(generos_list)
                # Reemplazar 'Niños' por 'Infantil'
                genero = self.normalizar_genero(genero)
                # Filtrar "Animación" del género
                genero = self.filtrar_animacion(genero)
                datos['genre'] = genero
                datos['specificGenre'] = genero
                datos['originalGenre'] = genero  # Mismo valor
                campos_encontrados.append(f"Género: {genero[:40]}")
        
        # Buscar imagen URL - MÉTODO MEJORADO
        if soup:
            # Buscar imágenes en el HTML con más prioridades
            img_selectors = [
                'img.postimage',  # Foroactivo
                'img[src*="res.cloudinary.com"]',
                'img[src*="poster"]',
                'img[src*="upload"]',
                'img[src*="image"]',
                'div.postbody img',
                'div.content img',
                '.post img',
                'img[alt*="poster" i]',
                'img[alt*="portada" i]',
            ]
            
            for selector in img_selectors:
                img = soup.select_one(selector)
                if img:
                    src = img.get('src', '')
                    if src and ('jpg' in src.lower() or 'jpeg' in src.lower() or 'png' in src.lower() or 'webp' in src.lower()):
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = 'https://animezoneesp.foroactivo.com' + src
                        datos['imagen_url'] = src
                        datos['imagen'] = src
                        campos_encontrados.append(f"Imagen: {src[:50]}...")
                        print(f"DEBUG - Imagen extraída de {selector}: {src}")
                        break
        
        # Buscar imagen URL desde texto también (como fallback)
        if 'imagen_url' not in datos:
            img_match = re.search(r'https?://[^\s\n"<>]+\.(?:jpg|jpeg|png|gif|webp)', texto, re.IGNORECASE)
            if img_match:
                imagen_url = img_match.group(0)
                datos['imagen_url'] = imagen_url
                datos['imagen'] = imagen_url
                campos_encontrados.append(f"Imagen: {imagen_url[:50]}...")
        
        # Buscar URL
        url_match = re.search(r'URL:\s*(https?://[^\s\n]+)|Enlace:\s*(https?://[^\s\n]+)|Link:\s*(https?://[^\s\n]+)', texto, re.IGNORECASE)
        if url_match:
            url = next((g for g in url_match.groups() if g is not None), '')
            if url:
                datos['url'] = url
                datos['href'] = url
                campos_encontrados.append(f"URL: {url[:50]}...")
        
        # Buscar sinopsis/descripción - múltiples estrategias
        # 1. Buscar en el HTML postbody - buscar párrafos completos
        if soup:
            # Intentar múltiples selectores para foroactivo
            postbody = soup.find('div', class_='postbody')
            if not postbody:
                # Foroactivo: buscar en otros contenedores comunes
                postbody = soup.find('div', class_='content') or soup.find('div', {'id': 'post_content'}) or soup.find('div', class_='post_content')
            # Si aún no hay postbody, buscar el contenido principal
            if not postbody:
                postbody = soup.find('div', class_='post') or soup.find('article')
            if postbody:
                # Buscar todos los párrafos <p> dentro del postbody
                parrafos = postbody.find_all('p')
                mejor_parrafo = None
                mejor_longitud = 0
                
                for p in parrafos:
                    texto_p = p.get_text(strip=True)
                    # Filtrar párrafos que sean descripción válida
                    if 80 < len(texto_p) < 800:
                        p_lower = texto_p.lower()
                        # NO debe ser título de post (ej: "[Activo] Nombre...")
                        if texto_p.startswith('[') or '[activo]' in p_lower or '[finalizado]' in p_lower:
                            continue
                        # No debe ser campo técnico
                        if not any(x in p_lower[:60] for x in ['idioma:', 'subtítulos:', 'formato:', 'calidad:', 'resolución:', 'peso:', 'título:', 'género:', 'episodios:', 'capítulos:']):
                            if len(texto_p) > mejor_longitud:
                                mejor_longitud = len(texto_p)
                                mejor_parrafo = texto_p
                
                if mejor_parrafo:
                    datos['sinopsis'] = mejor_parrafo[:600]
                    campos_encontrados.append(f"Sinopsis: {mejor_parrafo[:50]}...")
                    print(f"DEBUG - Sinopsis de <p>: {mejor_parrafo[:80]}...")
        
        # 2. Si no hay párrafos <p>, buscar texto plano línea por línea
        if 'sinopsis' not in datos and lineas:
            candidatos = []
            for linea in lineas:
                linea = linea.strip()
                # Buscar líneas sustanciales (no menú, no metadata, no títulos)
                if 80 < len(linea) < 700:
                    l_lower = linea.lower()
                    # NO debe ser un título de post (ej: "[Activo] Nombre...")
                    if linea.startswith('[') or '[activo]' in l_lower or '[finalizado]' in l_lower:
                        continue
                    # NO debe ser campo técnico
                    if not any(x in l_lower[:50] for x in ['idioma:', 'subtítulos:', 'formato:', 'calidad:', 'resolución:', 'peso:', 'título:', 'género:', 'episodios:', 'capítulos:', 'http']):
                        # NO debe ser menú o navegación
                        if not any(p in l_lower[:30] for p in ['índice', 'calendario', 'foro', 'buscar', 'login', 'regist', 'conectarse', 'registrarse']):
                            candidatos.append(linea)
            
            if candidatos:
                sinopsis = max(candidatos, key=len)
                datos['sinopsis'] = sinopsis[:600]
                campos_encontrados.append(f"Sinopsis: {sinopsis[:50]}...")
                print(f"DEBUG - Sinopsis de líneas: {sinopsis[:80]}...")
        
        # ===== FICHA TÉCNICA =====
        ficha = datos.get('ficha_tecnica', {})
        
        # Buscar campos de ficha técnica en todo el texto (multiline)
        # Idioma - buscar con diferentes patrones
        idioma_match = re.search(r'Idioma[s]?:\s*([^\n]+)', texto, re.IGNORECASE)
        if idioma_match:
            ficha['idioma'] = idioma_match.group(1).strip()
            campos_encontrados.append(f"idioma: {ficha['idioma'][:20]}")
        
        # Subtítulos
        subs_match = re.search(r'Subt[ií]tulo[s]?:\s*([^\n]+)', texto, re.IGNORECASE)
        if subs_match:
            ficha['subtitulos'] = subs_match.group(1).strip()
            campos_encontrados.append(f"subtitulos: {ficha['subtitulos'][:20]}")
        
        # Calidad
        calidad_match = re.search(r'Calidad:\s*([^\n]+)', texto, re.IGNORECASE)
        if calidad_match:
            ficha['calidad'] = calidad_match.group(1).strip()
            campos_encontrados.append(f"calidad: {ficha['calidad'][:20]}")
        
        # Resolución - buscar con o sin tilde
        resol_match = re.search(r'Resoluci[óo]n:\s*([^\n]+)|Resol:\s*([^\n]+)', texto, re.IGNORECASE)
        if resol_match:
            resol_valor = next((g for g in resol_match.groups() if g is not None), '').strip()
            if resol_valor:
                ficha['resolucion'] = resol_valor
                campos_encontrados.append(f"resolucion: {ficha['resolucion'][:20]}")
        
        # Formato
        formato_match = re.search(r'^\s*Formato:\s*([^\n]+)', texto, re.MULTILINE | re.IGNORECASE)
        if formato_match:
            ficha['formato'] = formato_match.group(1).strip()
            campos_encontrados.append(f"formato: {ficha['formato'][:20]}")
        
        # Peso/Cap
        peso_match = re.search(r'^\s*Peso[/\s]?Cap:\s*([^\n]+)', texto, re.MULTILINE | re.IGNORECASE)
        if not peso_match:
            peso_match = re.search(r'^\s*Peso:\s*([^\n]+)', texto, re.MULTILINE | re.IGNORECASE)
        if peso_match:
            ficha['peso'] = peso_match.group(1).strip()
            campos_encontrados.append(f"peso: {ficha['peso'][:20]}")
        
        datos['ficha_tecnica'] = ficha
        print(f"DEBUG - Ficha técnica: {ficha}")
        
        # ===== APLICAR DATOS A LOS CAMPOS =====
        self._aplicar_datos_extraidos(datos, campos_encontrados)
        return datos, campos_encontrados
    
    def _aplicar_datos_extraidos(self, datos, campos_encontrados):
        """Aplicar los datos extraídos a los campos del formulario"""
        import tkinter as tk
        ficha = datos.get('ficha_tecnica', {})
        
        # Campos principales
        if 'name' in datos:
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, datos['name'])
        
        if 'year' in datos:
            self.entry_year.delete(0, tk.END)
            self.entry_year.insert(0, str(datos['year']))
        
        if 'genre' in datos:
            self.entry_generos.delete(0, tk.END)
            self.entry_generos.insert(0, datos['genre'])
            self.actualizar_primer_genero()
        
        if 'imagen_url' in datos or 'imagen' in datos:
            self.entry_imagen.delete(0, tk.END)
            self.entry_imagen.insert(0, datos.get('imagen_url', datos.get('imagen', '')))
        
        if 'url' in datos:
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(0, datos['url'])
        
        if 'rentry_url' in datos:
            self.entry_rentry.delete(0, tk.END)
            self.entry_rentry.insert(0, datos['rentry_url'])
        
        if 'sinopsis' in datos:
            self.text_sinopsis.delete(1.0, tk.END)
            self.text_sinopsis.insert(1.0, datos['sinopsis'][:500])
        
        if 'type' in datos:
            self.combo_tipo.set(datos['type'])
        
        # Ficha técnica
        if 'idioma' in ficha:
            self.entry_idioma.delete(0, tk.END)
            self.entry_idioma.insert(0, ficha['idioma'])
        
        if 'subtitulos' in ficha:
            self.entry_subtitulos.delete(0, tk.END)
            self.entry_subtitulos.insert(0, ficha['subtitulos'])
        
        if 'calidad' in ficha:
            self.entry_calidad.delete(0, tk.END)
            self.entry_calidad.insert(0, ficha['calidad'])
        
        if 'resolucion' in ficha:
            self.entry_resolucion.delete(0, tk.END)
            self.entry_resolucion.insert(0, ficha['resolucion'])
        
        if 'formato' in ficha:
            self.entry_formato.delete(0, tk.END)
            self.entry_formato.insert(0, ficha['formato'])
        
        if 'peso' in ficha:
            self.entry_peso.delete(0, tk.END)
            self.entry_peso.insert(0, ficha['peso'])
        
        # Sincronizar con ficha técnica colapsable
        for campo, entry in self.entries_ficha.items():
            if campo in ficha:
                entry.delete(0, tk.END)
                entry.insert(0, ficha[campo])
        
        # Forzar actualización de la interfaz
        self.root.update_idletasks()
        
        # Mostrar resumen
        if campos_encontrados:
            resumen = "\n".join(campos_encontrados[:8])  # Mostrar máximo 8
            total_campos = len([k for k in datos.keys() if k != 'ficha_tecnica']) + len(ficha)
            self.label_status.config(
                text=f"📋 Extraído: {total_campos} campos", 
                foreground='green'
            )
            messagebox.showinfo(
                "Información Extraída", 
                f"✅ Campos encontrados ({total_campos}):\n\n{resumen}"
            )
        else:
            self.label_status.config(
                text="⚠️ No se detectaron campos", 
                foreground='orange'
            )
            messagebox.showwarning(
                "Sin resultados", 
                "No se encontraron campos en el texto.\n\n"
                "Formato esperado:\n"
                "- Título: Nombre de la serie\n"
                "- Año: 2024\n"
                "- Género: Acción, Aventura\n"
                "- Sinopsis: Descripción...\n"
                "- Idioma: Español\n"
                "- Subtítulos: Español\n"
                "- Calidad: Blu-ray\n"
                "- Resolución: 1080p\n"
                "- Formato: MKV\n"
                "- Peso/Cap: 2.5 GB"
            )
    
    def nueva_serie(self):
        """Crear una nueva serie en el catálogo"""
        # Verificar si hay datos en el formulario
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            self.label_status.config(text="⚠️ Introduce al menos el nombre", foreground='orange')
            return
        
        # Determinar la categoría según el tipo
        tipo = self.combo_tipo.get().lower()
        if 'anime' in tipo:
            categoria = 'Anime'
        elif 'dibujo' in tipo or 'cartoon' in tipo:
            categoria = 'Dibujos'
        elif 'peli' in tipo or 'pelí' in tipo or 'movie' in tipo:
            categoria = 'Peliculas'
        else:
            categoria = 'Series'
        
        # Crear la nueva serie
        generos = self.filtrar_animacion(self.entry_generos.get().strip())
        nueva_serie = {
            'name': nombre,
            'year': int(self.entry_year.get().strip()) if self.entry_year.get().strip().isdigit() else 0,
            'genre': generos,
            'specificGenre': generos,
            'originalGenre': generos,
            'type': self.combo_tipo.get(),
            'imagen_url': self.entry_imagen.get().strip(),
            'imagen': self.entry_imagen.get().strip(),
            'url': self.entry_url.get().strip(),
            'href': self.entry_href.get().strip(),
            'rentry_url': self.entry_rentry.get().strip(),
            'sinopsis': self.text_sinopsis.get(1.0, tk.END).strip(),
            'confianza': 0.8,
            'ficha_tecnica': {
                'idioma': self.entry_idioma.get().strip(),
                'subtitulos': self.entry_subtitulos.get().strip(),
                'calidad': self.entry_calidad.get().strip(),
                'resolucion': self.entry_resolucion.get().strip(),
                'formato': self.entry_formato.get().strip(),
                'peso': self.entry_peso.get().strip(),
            }
        }
        
        # Añadir a la categoría
        if categoria not in self.categorias:
            categoria = 'Series'  # Default
        
        self.categorias[categoria].append(nueva_serie)
        
        # Guardar serie_actual como la nueva
        self.serie_actual = nueva_serie
        nueva_serie['_categoria'] = categoria
        
        # Refrescar la vista
        self.refrescar_todos()
        
        self.label_status.config(text=f"✅ Serie '{nombre[:30]}' añadida a {categoria}", foreground='green')
    
    def hacer_deploy(self):
        """Hacer deploy a GitHub Pages"""
        import subprocess
        import os
        
        # Confirmar
        if not messagebox.askyesno("Confirmar", "¿Subir cambios a GitHub?\n\nEsto hará:\n1. Add index.html y TOP.json\n2. Commit\n3. Push a GitHub"):
            return
        
        try:
            self.label_status.config(text="🚀 Haciendo deploy...", foreground='blue')
            self.root.update()
            
            # Cambiar al directorio del proyecto
            proyecto_dir = r'c:\Users\Rafael\CascadeProjects\windsurf-project'
            
            # Git add
            subprocess.run(['git', '-C', proyecto_dir, 'add', 'index.html', 'TOP.json'], 
                          capture_output=True, check=True)
            
            # Git commit
            subprocess.run(['git', '-C', proyecto_dir, 'commit', '-m', 'Actualizar catalogo'], 
                          capture_output=True, check=True)
            
            # Git push
            resultado = subprocess.run(['git', '-C', proyecto_dir, 'push', 'origin', 'main'], 
                                      capture_output=True, text=True, check=True)
            
            messagebox.showinfo("Éxito", "✅ Deploy completado!\n\nLos cambios se subieron a GitHub.\nEspera 2-3 minutos para que se actualice el catálogo.")
            self.label_status.config(text="✅ Deploy listo - espera 2-3 min", foreground='green')
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr[:200] if e.stderr else str(e)
            if "nothing to commit" in error_msg.lower() or "nothing added" in error_msg.lower():
                messagebox.showinfo("Info", "No hay cambios nuevos para subir.")
                self.label_status.config(text="ℹ️ Sin cambios", foreground='gray')
            else:
                messagebox.showerror("Error", f"Error en deploy:\n{error_msg}")
                self.label_status.config(text="❌ Error en deploy", foreground='red')

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorCompacto(root)
    root.mainloop()