"""
Editor completo para TOP.json
Permite editar TODOS los campos de cualquier serie
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import re

class EditorCompleto:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor Completo de Series - AnimeZoneESP")
        self.root.geometry("1200x800")
        
        self.ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
        
        self.cargar_datos()
        self.crear_widgets()
        
    def cargar_datos(self):
        """Cargar datos del JSON"""
        with open(self.ruta_json, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.todas_series = []
        for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
            if categoria in self.data:
                for item in self.data[categoria]:
                    item['_categoria'] = categoria
                    self.todas_series.append(item)
        
        print(f"📊 Total series cargadas: {len(self.todas_series)}")
    
    def crear_widgets(self):
        """Crear interfaz completa"""
        # Frame superior - Búsqueda y filtros
        frame_superior = ttk.Frame(self.root, padding="10")
        frame_superior.pack(fill='x')
        
        ttk.Label(frame_superior, text="🔍 Buscar:").pack(side='left')
        self.entry_buscar = ttk.Entry(frame_superior, width=40)
        self.entry_buscar.pack(side='left', padx=5)
        self.entry_buscar.bind('<KeyRelease>', self.buscar)
        
        # Filtro por categoría
        ttk.Label(frame_superior, text="Categoría:").pack(side='left', padx=(20, 5))
        self.combo_categoria = ttk.Combobox(frame_superior, values=['Todas', 'Anime', 'Dibujos', 'Peliculas', 'Series'], width=12, state='readonly')
        self.combo_categoria.set('Todas')
        self.combo_categoria.pack(side='left')
        self.combo_categoria.bind('<<ComboboxSelected>>', self.buscar)
        
        ttk.Button(frame_superior, text="Mostrar Todas", command=self.mostrar_todas).pack(side='left', padx=10)
        ttk.Button(frame_superior, text="💾 Guardar JSON", command=self.guardar).pack(side='left', padx=5)
        ttk.Button(frame_superior, text="🔄 Regenerar HTML", command=self.regenerar_html).pack(side='left', padx=5)
        
        # Frame principal dividido
        paned = ttk.PanedWindow(self.root, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Panel izquierdo - Lista de series
        frame_izquierdo = ttk.LabelFrame(paned, text="Todas las Series", padding="5")
        paned.add(frame_izquierdo, weight=1)
        
        # Treeview con scrollbar
        cols = ('nombre', 'categoria', 'genero', 'year')
        self.tree = ttk.Treeview(frame_izquierdo, columns=cols, show='headings', height=30)
        
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('categoria', text='Cat.')
        self.tree.heading('genero', text='Género')
        self.tree.heading('year', text='Año')
        
        self.tree.column('nombre', width=250)
        self.tree.column('categoria', width=50)
        self.tree.column('genero', width=120)
        self.tree.column('year', width=50)
        
        scrollbar_y = ttk.Scrollbar(frame_izquierdo, orient='vertical', command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(frame_izquierdo, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        
        self.tree.bind('<<TreeviewSelect>>', self.cargar_serie)
        
        # Panel derecho - Edición
        frame_derecho = ttk.LabelFrame(paned, text="Editar Serie", padding="10")
        paned.add(frame_derecho, weight=2)
        
        # Canvas + Scrollbar para el formulario
        canvas = tk.Canvas(frame_derecho)
        scrollbar = ttk.Scrollbar(frame_derecho, orient='vertical', command=canvas.yview)
        self.frame_form = ttk.Frame(canvas)
        
        self.frame_form.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.frame_form, anchor='nw', width=650)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Campos del formulario
        row = 0
        
        # Nombre
        ttk.Label(self.frame_form, text="Nombre:").grid(row=row, column=0, sticky='w', pady=5)
        self.entry_nombre = ttk.Entry(self.frame_form, width=70)
        self.entry_nombre.grid(row=row, column=1, sticky='ew', pady=5, columnspan=2)
        row += 1
        
        # Categoría (no editable directamente)
        ttk.Label(self.frame_form, text="Categoría:").grid(row=row, column=0, sticky='w', pady=5)
        self.label_categoria = ttk.Label(self.frame_form, text="-")
        self.label_categoria.grid(row=row, column=1, sticky='w', pady=5)
        row += 1
        
        # Año
        ttk.Label(self.frame_form, text="Año:").grid(row=row, column=0, sticky='w', pady=5)
        self.entry_year = ttk.Entry(self.frame_form, width=10)
        self.entry_year.grid(row=row, column=1, sticky='w', pady=5)
        row += 1
        
        # Género (lista completa)
        ttk.Label(self.frame_form, text="Géneros (separados por coma):").grid(row=row, column=0, sticky='w', pady=5)
        self.entry_generos = ttk.Entry(self.frame_form, width=70)
        self.entry_generos.grid(row=row, column=1, sticky='ew', pady=5, columnspan=2)
        row += 1
        
        # Primer género (calculado)
        ttk.Label(self.frame_form, text="Primer género (clasificación):").grid(row=row, column=0, sticky='w', pady=5)
        self.label_primer_genero = ttk.Label(self.frame_form, text="-", foreground='blue', font=('Arial', 10, 'bold'))
        self.label_primer_genero.grid(row=row, column=1, sticky='w', pady=5)
        ttk.Button(self.frame_form, text="Actualizar", command=self.actualizar_primer_genero).grid(row=row, column=2, sticky='e', pady=5)
        row += 1
        
        # URL Imagen
        ttk.Label(self.frame_form, text="URL Imagen:").grid(row=row, column=0, sticky='w', pady=5)
        self.entry_imagen = ttk.Entry(self.frame_form, width=70)
        self.entry_imagen.grid(row=row, column=1, sticky='ew', pady=5, columnspan=2)
        row += 1
        
        # Sinopsis
        ttk.Label(self.frame_form, text="Sinopsis:").grid(row=row, column=0, sticky='nw', pady=5)
        self.text_sinopsis = scrolledtext.ScrolledText(self.frame_form, width=60, height=8, wrap=tk.WORD)
        self.text_sinopsis.grid(row=row, column=1, sticky='ew', pady=5, columnspan=2)
        row += 1
        
        # Ficha Técnica
        ttk.Separator(self.frame_form, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky='ew', pady=15)
        row += 1
        
        ttk.Label(self.frame_form, text="FICHA TÉCNICA", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1
        
        # Campos de ficha técnica
        campos_ficha = ['audio', 'calidad', 'creador', 'duracion_episodio', 'elenco', 
                       'episodios', 'formato', 'idioma', 'peso_episodio', 'productora',
                       'reparto', 'resolucion', 'subtitulos', 'tamaño', 'temporadas']
        
        self.entries_ficha = {}
        for campo in campos_ficha:
            ttk.Label(self.frame_form, text=f"{campo.replace('_', ' ').title()}:").grid(row=row, column=0, sticky='w', pady=2)
            entry = ttk.Entry(self.frame_form, width=70)
            entry.grid(row=row, column=1, sticky='ew', pady=2, columnspan=2)
            self.entries_ficha[campo] = entry
            row += 1
        
        # Botones de acción
        ttk.Separator(self.frame_form, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky='ew', pady=15)
        row += 1
        
        frame_botones = ttk.Frame(self.frame_form)
        frame_botones.grid(row=row, column=0, columnspan=3, pady=10)
        
        ttk.Button(frame_botones, text="✅ Aplicar Cambios", command=self.aplicar_cambios, width=20).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="🗑️ Restaurar Valores", command=self.restaurar_valores, width=20).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="➡️ Siguiente Serie", command=self.siguiente_serie, width=20).pack(side='left', padx=5)
        
        # Info inferior
        self.label_info = ttk.Label(self.root, text=f"Total: {len(self.todas_series)} series | Usa el buscador o selecciona una serie para editar")
        self.label_info.pack(side='bottom', fill='x', padx=10, pady=5)
        
        # Cargar todas las series inicialmente
        self.cargar_todas_series()
    
    def cargar_todas_series(self):
        """Cargar todas las series en el treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for serie in self.todas_series:
            nombre = serie.get('name', 'Sin nombre')
            if len(nombre) > 40:
                nombre = nombre[:40] + "..."
            
            categoria = serie.get('_categoria', 'N/A')[:3].upper()
            genero = serie.get('genre', serie.get('specificGenre', 'N/A'))
            if len(genero) > 15:
                genero = genero[:15] + "..."
            year = str(serie.get('year', ''))
            
            self.tree.insert('', 'end', values=(nombre, categoria, genero, year))
        
        self.series_tree = self.todas_series.copy()
    
    def buscar(self, event=None):
        """Buscar series"""
        termino = self.entry_buscar.get().lower().strip()
        categoria = self.combo_categoria.get()
        
        # Limpiar tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.series_tree = []
        
        for serie in self.todas_series:
            nombre = serie.get('name', '').lower()
            cat = serie.get('_categoria', '').lower()
            
            # Filtro por categoría
            if categoria != 'Todas' and cat != categoria.lower():
                continue
            
            # Filtro por término
            if termino and termino not in nombre:
                continue
            
            self.series_tree.append(serie)
            
            nombre_display = serie.get('name', 'Sin nombre')
            if len(nombre_display) > 40:
                nombre_display = nombre_display[:40] + "..."
            
            categoria_display = serie.get('_categoria', 'N/A')[:3].upper()
            genero = serie.get('genre', serie.get('specificGenre', 'N/A'))
            if len(genero) > 15:
                genero = genero[:15] + "..."
            year = str(serie.get('year', ''))
            
            self.tree.insert('', 'end', values=(nombre_display, categoria_display, genero, year))
        
        self.label_info.config(text=f"Mostrando: {len(self.series_tree)} series")
    
    def mostrar_todas(self):
        """Mostrar todas las series"""
        self.entry_buscar.delete(0, tk.END)
        self.combo_categoria.set('Todas')
        self.cargar_todas_series()
        self.label_info.config(text=f"Total: {len(self.todas_series)} series")
    
    def cargar_serie(self, event=None):
        """Cargar datos de la serie seleccionada en el formulario"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        index = self.tree.index(seleccion[0])
        if index >= len(self.series_tree):
            return
        
        self.serie_actual = self.series_tree[index]
        self.restaurar_valores()
    
    def restaurar_valores(self):
        """Restaurar valores de la serie actual en el formulario"""
        if not hasattr(self, 'serie_actual'):
            return
        
        serie = self.serie_actual
        
        # Campos básicos
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, serie.get('name', ''))
        
        self.label_categoria.config(text=serie.get('_categoria', 'N/A').upper())
        
        self.entry_year.delete(0, tk.END)
        self.entry_year.insert(0, str(serie.get('year', '')))
        
        # Género
        genero = serie.get('genre', serie.get('specificGenre', ''))
        self.entry_generos.delete(0, tk.END)
        self.entry_generos.insert(0, genero)
        
        # Primer género
        primer = genero.split(',')[0].strip() if genero else 'N/A'
        self.label_primer_genero.config(text=primer)
        
        # Imagen
        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, serie.get('imagen_url', serie.get('imagen', '')))
        
        # Sinopsis
        self.text_sinopsis.delete(1.0, tk.END)
        self.text_sinopsis.insert(1.0, serie.get('sinopsis', ''))
        
        # Ficha técnica
        ficha = serie.get('ficha_tecnica', {})
        for campo, entry in self.entries_ficha.items():
            entry.delete(0, tk.END)
            entry.insert(0, ficha.get(campo, ''))
        
        self.label_info.config(text=f"Editando: {serie.get('name', 'N/A')[:50]}...")
    
    def actualizar_primer_genero(self):
        """Actualizar visualización del primer género"""
        generos = self.entry_generos.get().strip()
        primer = generos.split(',')[0].strip() if generos else 'N/A'
        self.label_primer_genero.config(text=primer)
    
    def aplicar_cambios(self):
        """Aplicar cambios a la serie actual"""
        if not hasattr(self, 'serie_actual'):
            messagebox.showwarning("Atención", "Selecciona una serie primero")
            return
        
        serie = self.serie_actual
        
        # Aplicar cambios básicos
        serie['name'] = self.entry_nombre.get().strip()
        
        try:
            serie['year'] = int(self.entry_year.get().strip())
        except:
            pass
        
        serie['genre'] = self.entry_generos.get().strip()
        serie['imagen_url'] = self.entry_imagen.get().strip()
        serie['sinopsis'] = self.text_sinopsis.get(1.0, tk.END).strip()
        
        # Aplicar ficha técnica
        if 'ficha_tecnica' not in serie:
            serie['ficha_tecnica'] = {}
        
        for campo, entry in self.entries_ficha.items():
            valor = entry.get().strip()
            if valor:
                serie['ficha_tecnica'][campo] = valor
        
        self.label_info.config(text=f"✅ Cambios aplicados a: {serie.get('name', 'N/A')[:40]}...")
        messagebox.showinfo("Éxito", "Cambios aplicados. Recuerda guardar el JSON (Ctrl+S)")
        
        # Actualizar visual en el tree
        self.buscar()
    
    def siguiente_serie(self):
        """Ir a la siguiente serie en la lista"""
        seleccion = self.tree.selection()
        if not seleccion:
            # Seleccionar primera
            if self.tree.get_children():
                self.tree.selection_set(self.tree.get_children()[0])
            return
        
        actual = seleccion[0]
        siguiente = self.tree.next(actual)
        
        if siguiente:
            self.tree.selection_set(siguiente)
            self.tree.see(siguiente)
    
    def guardar(self):
        """Guardar JSON"""
        try:
            # Limpiar campos auxiliares
            for serie in self.todas_series:
                if '_categoria' in serie:
                    del serie['_categoria']
            
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            # Restaurar campos auxiliares
            for serie in self.todas_series:
                for cat in ['anime', 'dibujos', 'peliculas', 'series']:
                    if serie in self.data.get(cat, []):
                        serie['_categoria'] = cat
                        break
            
            messagebox.showinfo("Éxito", "✅ Cambios guardados en TOP.json")
            self.label_info.config(text="💾 JSON guardado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")
    
    def regenerar_html(self):
        """Regenerar HTML"""
        import subprocess
        
        respuesta = messagebox.askyesno("Confirmar", "¿Regenerar index.html?")
        if not respuesta:
            return
        
        try:
            self.label_info.config(text="🔄 Regenerando HTML...")
            self.root.update()
            
            resultado = subprocess.run(
                ['python', r'c:\Users\Rafael\CascadeProjects\windsurf-project\generar_html_foroactivo.py'],
                capture_output=True, text=True, timeout=60
            )
            
            if resultado.returncode == 0:
                messagebox.showinfo("Éxito", "✅ HTML regenerado. Recarga la página.")
                self.label_info.config(text="✅ HTML regenerado correctamente")
            else:
                messagebox.showerror("Error", f"Error:\n{resultado.stderr[:300]}")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo regenerar:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorCompleto(root)
    root.mainloop()
