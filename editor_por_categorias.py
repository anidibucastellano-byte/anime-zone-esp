"""
Editor por Categorías para TOP.json
Navegación organizada: Anime | Dibujos | Películas | Series
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path

class EditorPorCategorias:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor por Categorías - AnimeZoneESP")
        self.root.geometry("1400x900")
        
        self.ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
        
        self.cargar_datos()
        self.crear_widgets()
        
    def cargar_datos(self):
        """Cargar datos del JSON"""
        with open(self.ruta_json, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # Organizar por categoría
        self.categorias = {
            'Anime': self.data.get('anime', []),
            'Dibujos': self.data.get('dibujos', []),
            'Peliculas': self.data.get('peliculas', []),
            'Series': self.data.get('series', [])
        }
        
        # Crear lista plana de todas las series
        self.todas_series = []
        for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
            if categoria in self.data:
                for item in self.data[categoria]:
                    item['_categoria'] = categoria
                    self.todas_series.append(item)
        
        # Agregar campo auxiliar
        for cat_name, items in self.categorias.items():
            for item in items:
                item['_categoria'] = cat_name.lower()
        
        total = sum(len(items) for items in self.categorias.values())
        print(f"📊 Total series cargadas: {total}")
        print(f"   Anime: {len(self.categorias['Anime'])}")
        print(f"   Dibujos: {len(self.categorias['Dibujos'])}")
        print(f"   Peliculas: {len(self.categorias['Peliculas'])}")
        print(f"   Series: {len(self.categorias['Series'])}")
    
    def limpiar_nombre(self, nombre):
        """Limpiar nombre - quitar corchetes y formato técnico"""
        if not nombre:
            return 'Sin nombre'
        import re
        # Quitar corchetes y su contenido
        nombre = re.sub(r'\[.*?\]', '', nombre)
        # Quitar (Activo), (Finalizado)
        nombre = nombre.replace('(Activo)', '').replace('(Finalizado)', '')
        # Quitar formatos técnicos entre paréntesis
        nombre = re.sub(r'\(.*?\)', '', nombre)
        # Quitar múltiples espacios
        nombre = re.sub(r'\s+', ' ', nombre)
        return nombre.strip()
    
    def crear_widgets(self):
        """Crear interfaz con pestañas por categoría"""
        # Frame superior - Título y controles globales
        frame_top = ttk.Frame(self.root, padding="10")
        frame_top.pack(fill='x')
        
        ttk.Label(frame_top, text="📁 Editor por Categorías", font=('Arial', 14, 'bold')).pack(side='left')
        
        # Búsqueda global
        ttk.Label(frame_top, text="🔍 Buscar:").pack(side='left', padx=(30, 5))
        self.entry_buscar = ttk.Entry(frame_top, width=40)
        self.entry_buscar.pack(side='left')
        self.entry_buscar.bind('<Return>', self.buscar_global)
        ttk.Button(frame_top, text="Buscar en todas", command=self.buscar_global).pack(side='left', padx=5)
        
        ttk.Button(frame_top, text="💾 Guardar JSON", command=self.guardar).pack(side='right', padx=5)
        ttk.Button(frame_top, text="🔄 Regenerar HTML", command=self.regenerar_html).pack(side='right', padx=5)
        
        # Notebook (pestañas) por categoría
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Crear pestaña para cada categoría
        self.tabs = {}
        self.trees = {}
        
        for cat_name in ['Anime', 'Dibujos', 'Peliculas', 'Series']:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"{cat_name} ({len(self.categorias[cat_name])})")
            self.tabs[cat_name] = tab
            
            self.crear_tab_categoria(tab, cat_name)
        
        # Panel inferior - Editor
        frame_editor = ttk.LabelFrame(self.root, text="✏️ Editor de Serie Seleccionada", padding="10")
        frame_editor.pack(fill='x', side='bottom', padx=10, pady=5)
        
        self.crear_formulario_editor(frame_editor)
        
        # Status bar
        self.label_status = ttk.Label(self.root, text="Selecciona una categoría y luego una serie para editar", relief='sunken')
        self.label_status.pack(fill='x', side='bottom')
    
    def crear_tab_categoria(self, tab, cat_name):
        """Crear contenido de una pestaña de categoría"""
        # Frame izquierdo - Lista
        frame_lista = ttk.Frame(tab)
        frame_lista.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Búsqueda en categoría
        frame_busqueda = ttk.Frame(frame_lista)
        frame_busqueda.pack(fill='x', pady=(0, 5))
        
        ttk.Label(frame_busqueda, text="🔍 Buscar en esta categoría:").pack(side='left')
        entry_buscar_cat = ttk.Entry(frame_busqueda, width=30)
        entry_buscar_cat.pack(side='left', padx=5)
        entry_buscar_cat.bind('<KeyRelease>', lambda e, c=cat_name: self.buscar_en_categoria(e, c))
        ttk.Button(frame_busqueda, text="Mostrar todas", 
                  command=lambda c=cat_name: self.cargar_series_en_tree(c)).pack(side='left', padx=5)
        
        # Treeview
        cols = ('nombre', 'year', 'genero')
        tree = ttk.Treeview(frame_lista, columns=cols, show='headings', height=25)
        
        tree.heading('nombre', text='Nombre de la Serie')
        tree.heading('year', text='Año')
        tree.heading('genero', text='Género')
        
        tree.column('nombre', width=400)
        tree.column('year', width=60)
        tree.column('genero', width=200)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        tree.bind('<<TreeviewSelect>>', lambda e, c=cat_name: self.seleccionar_serie(e, c))
        
        self.trees[cat_name] = tree
        
        # Cargar series iniciales
        self.cargar_series_en_tree(cat_name)
    
    def cargar_series_en_tree(self, cat_name):
        """Cargar todas las series de una categoría en su tree"""
        tree = self.trees[cat_name]
        
        # Limpiar
        for item in tree.get_children():
            tree.delete(item)
        
        # Cargar series con nombres limpios
        series = self.categorias[cat_name]
        for serie in series:
            # Usar nombre limpio (sin corchetes ni formato técnico)
            nombre_completo = serie.get('name', 'Sin nombre')
            nombre_limpio = self.limpiar_nombre(nombre_completo)
            if len(nombre_limpio) > 50:
                nombre_limpio = nombre_limpio[:50] + "..."
            
            year = str(serie.get('year', ''))
            genero = serie.get('genre', serie.get('specificGenre', 'N/A'))
            if len(genero) > 30:
                genero = genero[:30] + "..."
            
            tree.insert('', 'end', values=(nombre_limpio, year, genero))
    
    def buscar_en_categoria(self, event, cat_name):
        """Buscar en una categoría específica"""
        tree = self.trees[cat_name]
        termino = event.widget.get().lower().strip()
        
        # Limpiar
        for item in tree.get_children():
            tree.delete(item)
        
        # Filtrar y cargar
        series = self.categorias[cat_name]
        for serie in series:
            nombre_completo = serie.get('name', '')
            nombre_limpio = self.limpiar_nombre(nombre_completo)
            
            if termino and termino not in nombre_completo.lower() and termino not in nombre_limpio.lower():
                continue
            
            nombre_display = nombre_limpio
            if len(nombre_display) > 50:
                nombre_display = nombre_display[:50] + "..."
            
            year = str(serie.get('year', ''))
            genero = serie.get('genre', serie.get('specificGenre', 'N/A'))
            if len(genero) > 30:
                genero = genero[:30] + "..."
            
            tree.insert('', 'end', values=(nombre_display, year, genero))
    
    def buscar_global(self, event=None):
        """Buscar en todas las categorías y mostrar resultados"""
        termino = self.entry_buscar.get().lower().strip()
        if not termino:
            return
        
        # Ir a la primera categoría con resultados
        for cat_name in ['Anime', 'Dibujos', 'Peliculas', 'Series']:
            tree = self.trees[cat_name]
            series = self.categorias[cat_name]
            
            # Limpiar
            for item in tree.get_children():
                tree.delete(item)
            
            # Cargar coincidencias
            encontradas = 0
            for serie in series:
                nombre_completo = serie.get('name', '')
                nombre_limpio = self.limpiar_nombre(nombre_completo)
                
                if termino in nombre_completo.lower() or termino in nombre_limpio.lower():
                    nombre_display = nombre_limpio
                    if len(nombre_display) > 50:
                        nombre_display = nombre_display[:50] + "..."
                    
                    year = str(serie.get('year', ''))
                    genero = serie.get('genre', serie.get('specificGenre', 'N/A'))
                    if len(genero) > 30:
                        genero = genero[:30] + "..."
                    
                    tree.insert('', 'end', values=(nombre_display, year, genero))
                    encontradas += 1
            
            if encontradas > 0:
                self.notebook.select(self.tabs[cat_name])
                self.label_status.config(text=f"🔍 {encontradas} resultados para '{termino}' en {cat_name}")
                return
        
        self.label_status.config(text=f"❌ No se encontró '{termino}' en ninguna categoría")
    
    def seleccionar_serie(self, event, cat_name):
        """Cuando se selecciona una serie en el tree"""
        tree = self.trees[cat_name]
        seleccion = tree.selection()
        if not seleccion:
            return
        
        index = tree.index(seleccion[0])
        series = self.categorias[cat_name]
        
        # Encontrar la serie correspondiente (considerando búsquedas previas)
        nombre_seleccionado = tree.item(seleccion[0])['values'][0]
        
        # Buscar serie real
        for serie in series:
            if serie.get('name', '').startswith(nombre_seleccionado[:30]):
                self.serie_actual = serie
                break
        else:
            if index < len(series):
                self.serie_actual = series[index]
            else:
                return
        
        self.cargar_serie_en_formulario()
    
    def crear_formulario_editor(self, parent):
        """Crear el formulario de edición"""
        # Canvas con scrollbar para muchos campos
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        self.frame_form = ttk.Frame(canvas)
        
        self.frame_form.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.frame_form, anchor='nw', width=1350)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Campos del formulario
        row = 0
        
        # Título
        ttk.Label(self.frame_form, text="INFORMACIÓN BÁSICA", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=4, sticky='w', pady=(0, 10))
        row += 1
        
        # Nombre
        ttk.Label(self.frame_form, text="Nombre:").grid(row=row, column=0, sticky='w', pady=3)
        self.entry_nombre = ttk.Entry(self.frame_form, width=80)
        self.entry_nombre.grid(row=row, column=1, sticky='ew', pady=3, columnspan=3)
        row += 1
        
        # Categoría (solo lectura)
        ttk.Label(self.frame_form, text="Categoría:").grid(row=row, column=0, sticky='w', pady=3)
        self.label_categoria = ttk.Label(self.frame_form, text="-", font=('Arial', 10, 'bold'))
        self.label_categoria.grid(row=row, column=1, sticky='w', pady=3)
        row += 1
        
        # Año
        ttk.Label(self.frame_form, text="Año:").grid(row=row, column=0, sticky='w', pady=3)
        self.entry_year = ttk.Entry(self.frame_form, width=10)
        self.entry_year.grid(row=row, column=1, sticky='w', pady=3)
        row += 1
        
        # Géneros
        ttk.Label(self.frame_form, text="Géneros (separados por coma):").grid(row=row, column=0, sticky='w', pady=3)
        self.entry_generos = ttk.Entry(self.frame_form, width=80)
        self.entry_generos.grid(row=row, column=1, sticky='ew', pady=3, columnspan=3)
        row += 1
        
        # Primer género (clasificación)
        ttk.Label(self.frame_form, text="→ Clasificación (primer género):").grid(row=row, column=0, sticky='w', pady=3)
        self.label_primer_genero = ttk.Label(self.frame_form, text="-", foreground='blue', font=('Arial', 11, 'bold'))
        self.label_primer_genero.grid(row=row, column=1, sticky='w', pady=3)
        ttk.Button(self.frame_form, text="🔄 Calcular", command=self.calcular_primer_genero).grid(row=row, column=2, sticky='w', pady=3)
        row += 1
        
        # URLs
        ttk.Label(self.frame_form, text="URL del Foro:").grid(row=row, column=0, sticky='w', pady=3)
        self.entry_url = ttk.Entry(self.frame_form, width=80)
        self.entry_url.grid(row=row, column=1, sticky='ew', pady=3, columnspan=3)
        row += 1
        
        ttk.Label(self.frame_form, text="URL Imagen:").grid(row=row, column=0, sticky='w', pady=3)
        self.entry_imagen = ttk.Entry(self.frame_form, width=80)
        self.entry_imagen.grid(row=row, column=1, sticky='ew', pady=3, columnspan=3)
        row += 1
        
        ttk.Label(self.frame_form, text="URL Rentry (Ver Online):").grid(row=row, column=0, sticky='w', pady=3)
        self.entry_rentry = ttk.Entry(self.frame_form, width=80)
        self.entry_rentry.grid(row=row, column=1, sticky='ew', pady=3, columnspan=3)
        row += 1
        
        # Sinopsis
        ttk.Label(self.frame_form, text="Sinopsis:").grid(row=row, column=0, sticky='nw', pady=3)
        self.text_sinopsis = scrolledtext.ScrolledText(self.frame_form, width=100, height=6, wrap=tk.WORD)
        self.text_sinopsis.grid(row=row, column=1, sticky='ew', pady=3, columnspan=3)
        row += 1
        
        # Ficha Técnica
        ttk.Separator(self.frame_form, orient='horizontal').grid(row=row, column=0, columnspan=4, sticky='ew', pady=15)
        row += 1
        
        ttk.Label(self.frame_form, text="FICHA TÉCNICA", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=4, sticky='w', pady=(0, 10))
        row += 1
        
        campos_ficha = [
            ('idioma', 'Idioma'),
            ('subtitulos', 'Subtítulos'),
            ('calidad', 'Calidad'),
            ('resolucion', 'Resolución'),
            ('formato', 'Formato'),
            ('episodios', 'Episodios'),
            ('temporadas', 'Temporadas'),
            ('duracion_episodio', 'Duración Ep.'),
            ('peso_episodio', 'Peso Ep.'),
            ('tamaño', 'Tamaño Total'),
            ('audio', 'Audio'),
            ('creador', 'Creador/Director'),
            ('reparto', 'Reparto/Elenco'),
            ('productora', 'Productora'),
            ('ano', 'Año (ficha)'),
        ]
        
        self.entries_ficha = {}
        for campo, label in campos_ficha:
            ttk.Label(self.frame_form, text=f"{label}:").grid(row=row, column=0, sticky='w', pady=2)
            entry = ttk.Entry(self.frame_form, width=80)
            entry.grid(row=row, column=1, sticky='ew', pady=2, columnspan=3)
            self.entries_ficha[campo] = entry
            row += 1
        
        # Botones de acción
        ttk.Separator(self.frame_form, orient='horizontal').grid(row=row, column=0, columnspan=4, sticky='ew', pady=15)
        row += 1
        
        frame_botones = ttk.Frame(self.frame_form)
        frame_botones.grid(row=row, column=0, columnspan=4, pady=10)
        
        ttk.Button(frame_botones, text="💾 Aplicar Cambios", command=self.aplicar_cambios, width=25).pack(side='left', padx=10)
        ttk.Button(frame_botones, text="🔄 Restaurar Valores", command=self.cargar_serie_en_formulario, width=25).pack(side='left', padx=10)
        ttk.Button(frame_botones, text="➡️ Siguiente Serie", command=self.siguiente_serie, width=25).pack(side='left', padx=10)
    
    def cargar_serie_en_formulario(self):
        """Cargar datos de la serie seleccionada"""
        if not hasattr(self, 'serie_actual'):
            return
        
        s = self.serie_actual
        
        # Básicos
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, s.get('name', ''))
        
        self.label_categoria.config(text=s.get('_categoria', 'N/A').upper())
        
        self.entry_year.delete(0, tk.END)
        self.entry_year.insert(0, str(s.get('year', '')))
        
        # Géneros
        generos = s.get('genre', s.get('specificGenre', ''))
        self.entry_generos.delete(0, tk.END)
        self.entry_generos.insert(0, generos)
        self.calcular_primer_genero()
        
        # URLs
        self.entry_url.delete(0, tk.END)
        self.entry_url.insert(0, s.get('url', ''))
        
        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, s.get('imagen_url', s.get('imagen', '')))
        
        self.entry_rentry.delete(0, tk.END)
        self.entry_rentry.insert(0, s.get('rentry_url', ''))
        
        # Sinopsis
        self.text_sinopsis.delete(1.0, tk.END)
        self.text_sinopsis.insert(1.0, s.get('sinopsis', ''))
        
        # Ficha técnica
        ficha = s.get('ficha_tecnica', {})
        for campo, entry in self.entries_ficha.items():
            entry.delete(0, tk.END)
            entry.insert(0, ficha.get(campo, ''))
        
        self.label_status.config(text=f"✏️ Editando: {s.get('name', 'N/A')[:50]}...")
    
    def calcular_primer_genero(self):
        """Calcular primer género de la lista"""
        generos = self.entry_generos.get().strip()
        if generos:
            primer = generos.split(',')[0].strip()
            self.label_primer_genero.config(text=primer)
        else:
            self.label_primer_genero.config(text="N/A")
    
    def aplicar_cambios(self):
        """Guardar cambios en la serie actual"""
        if not hasattr(self, 'serie_actual'):
            messagebox.showwarning("Atención", "Selecciona una serie primero")
            return
        
        s = self.serie_actual
        
        # Aplicar cambios
        s['name'] = self.entry_nombre.get().strip()
        
        try:
            s['year'] = int(self.entry_year.get().strip())
        except:
            pass
        
        s['genre'] = self.entry_generos.get().strip()
        s['url'] = self.entry_url.get().strip()
        s['imagen_url'] = self.entry_imagen.get().strip()
        s['rentry_url'] = self.entry_rentry.get().strip()
        s['sinopsis'] = self.text_sinopsis.get(1.0, tk.END).strip()
        
        # Ficha técnica
        if 'ficha_tecnica' not in s:
            s['ficha_tecnica'] = {}
        
        for campo, entry in self.entries_ficha.items():
            valor = entry.get().strip()
            if valor:
                s['ficha_tecnica'][campo] = valor
        
        self.label_status.config(text=f"✅ Cambios aplicados a: {s['name'][:40]}...")
        messagebox.showinfo("Éxito", "Cambios aplicados. ¡Recuerda guardar el JSON!")
        
        # Refrescar tree actual
        cat = s.get('_categoria', '').capitalize()
        if cat in self.trees:
            self.cargar_series_en_tree(cat)
    
    def siguiente_serie(self):
        """Ir a la siguiente serie"""
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
    
    def guardar(self):
        """Guardar JSON"""
        try:
            # Limpiar campos auxiliares
            for cat_items in self.categorias.values():
                for item in cat_items:
                    if '_categoria' in item:
                        del item['_categoria']
            
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            # Restaurar campos auxiliares
            for cat_name, items in self.categorias.items():
                for item in items:
                    item['_categoria'] = cat_name.lower()
            
            messagebox.showinfo("Éxito", "✅ Cambios guardados en TOP.json")
            self.label_status.config(text="💾 JSON guardado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")
    
    def regenerar_html(self):
        """Regenerar HTML"""
        import subprocess
        
        respuesta = messagebox.askyesno("Confirmar", "¿Regenerar index.html?\n\nEsto actualizará la página web.")
        if not respuesta:
            return
        
        try:
            self.label_status.config(text="🔄 Regenerando HTML...")
            self.root.update()
            
            resultado = subprocess.run(
                ['python', r'c:\Users\Rafael\CascadeProjects\windsurf-project\generar_html_foroactivo.py'],
                capture_output=True, text=True, timeout=60
            )
            
            if resultado.returncode == 0:
                messagebox.showinfo("Éxito", "✅ HTML regenerado correctamente!\n\nRecarga la página en el navegador.")
                self.label_status.config(text="✅ HTML regenerado. Recarga la página web.")
            else:
                messagebox.showerror("Error", f"Error al regenerar:\n{resultado.stderr[:300]}")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo regenerar:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorPorCategorias(root)
    root.mainloop()
