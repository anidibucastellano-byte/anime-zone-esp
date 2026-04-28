"""
Editor por Géneros para TOP.json
Navegación organizada por Géneros principales
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path

class EditorPorGenero:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor por Géneros - AnimeZoneESP")
        self.root.geometry("1400x900")
        
        self.ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
        
        self.cargar_datos()
        self.crear_widgets()
        
    def cargar_datos(self):
        """Cargar y organizar datos por género"""
        with open(self.ruta_json, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # Lista plana de todas las series
        self.todas_series = []
        for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
            if categoria in self.data:
                for item in self.data[categoria]:
                    item['_categoria'] = categoria
                    self.todas_series.append(item)
        
        # Organizar por género (primer género de cada serie)
        self.generos = {}
        for serie in self.todas_series:
            genero_completo = serie.get('genre', serie.get('specificGenre', 'Sin Género'))
            if isinstance(genero_completo, str):
                primer_genero = genero_completo.split(',')[0].strip()
            else:
                primer_genero = 'Sin Género'
            
            if primer_genero not in self.generos:
                self.generos[primer_genero] = []
            self.generos[primer_genero].append(serie)
        
        # Ordenar géneros por cantidad de series
        self.generos_ordenados = sorted(self.generos.items(), key=lambda x: len(x[1]), reverse=True)
        
        print(f"📊 Total series: {len(self.todas_series)}")
        print(f"📊 Total géneros: {len(self.generos)}")
        for genero, series in self.generos_ordenados[:10]:
            print(f"   {genero}: {len(series)} series")
    
    def crear_widgets(self):
        """Crear interfaz con pestañas por género"""
        # Frame superior
        frame_top = ttk.Frame(self.root, padding="10")
        frame_top.pack(fill='x')
        
        ttk.Label(frame_top, text="🎭 Editor por Géneros", font=('Arial', 14, 'bold')).pack(side='left')
        
        # Selector de vista
        ttk.Label(frame_top, text="Ver por:").pack(side='left', padx=(30, 5))
        self.combo_vista = ttk.Combobox(frame_top, values=['Género', 'Categoría'], width=12, state='readonly')
        self.combo_vista.set('Género')
        self.combo_vista.pack(side='left')
        self.combo_vista.bind('<<ComboboxSelected>>', self.cambiar_vista)
        
        # Búsqueda
        ttk.Label(frame_top, text="🔍 Buscar:").pack(side='left', padx=(20, 5))
        self.entry_buscar = ttk.Entry(frame_top, width=35)
        self.entry_buscar.pack(side='left')
        self.entry_buscar.bind('<Return>', self.buscar_global)
        ttk.Button(frame_top, text="Buscar", command=self.buscar_global).pack(side='left', padx=5)
        
        ttk.Button(frame_top, text="💾 Guardar JSON", command=self.guardar).pack(side='right', padx=5)
        ttk.Button(frame_top, text="🔄 Regenerar HTML", command=self.regenerar_html).pack(side='right', padx=5)
        
        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Crear pestañas para cada género
        self.tabs = {}
        self.trees = {}
        
        # Mostrar solo los géneros con más series (top 15) + "Otros"
        generos_a_mostrar = self.generos_ordenados[:15]
        
        for genero, series in generos_a_mostrar:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"{genero[:20]} ({len(series)})")
            self.tabs[genero] = tab
            self.crear_tab_genero(tab, genero, series)
        
        # Pestaña "Otros" para géneros menores
        if len(self.generos_ordenados) > 15:
            tab_otros = ttk.Frame(self.notebook)
            otros_series = []
            for genero, series in self.generos_ordenados[15:]:
                otros_series.extend(series)
            self.notebook.add(tab_otros, text=f"Otros ({len(otros_series)})")
            self.tabs['Otros'] = tab_otros
            self.crear_tab_genero(tab_otros, 'Otros', otros_series)
        
        # Editor inferior
        frame_editor = ttk.LabelFrame(self.root, text="✏️ Editor de Serie", padding="10")
        frame_editor.pack(fill='x', side='bottom', padx=10, pady=5)
        self.crear_formulario_editor(frame_editor)
        
        # Status
        self.label_status = ttk.Label(self.root, text="Selecciona un género y luego una serie para editar", relief='sunken')
        self.label_status.pack(fill='x', side='bottom')
    
    def crear_tab_genero(self, tab, genero, series):
        """Crear contenido de una pestaña de género"""
        # Frame izquierdo - Lista
        frame_lista = ttk.Frame(tab)
        frame_lista.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Info del género
        frame_info = ttk.Frame(frame_lista)
        frame_info.pack(fill='x', pady=(0, 5))
        ttk.Label(frame_info, text=f"🎭 {genero}", font=('Arial', 12, 'bold')).pack(side='left')
        ttk.Label(frame_info, text=f"- {len(series)} series").pack(side='left', padx=5)
        
        # Búsqueda
        frame_busqueda = ttk.Frame(frame_lista)
        frame_busqueda.pack(fill='x', pady=(0, 5))
        ttk.Label(frame_busqueda, text="🔍 Filtrar:").pack(side='left')
        entry_buscar = ttk.Entry(frame_busqueda, width=30)
        entry_buscar.pack(side='left', padx=5)
        entry_buscar.bind('<KeyRelease>', lambda e, g=genero: self.filtrar_genero(e, g))
        
        # Treeview
        cols = ('nombre', 'categoria', 'year', 'genero_completo')
        tree = ttk.Treeview(frame_lista, columns=cols, show='headings', height=25)
        
        tree.heading('nombre', text='Nombre')
        tree.heading('categoria', text='Cat.')
        tree.heading('year', text='Año')
        tree.heading('genero_completo', text='Géneros Completos')
        
        tree.column('nombre', width=350)
        tree.column('categoria', width=50)
        tree.column('year', width=50)
        tree.column('genero_completo', width=250)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        tree.bind('<<TreeviewSelect>>', lambda e, g=genero: self.seleccionar_serie(e, g))
        
        self.trees[genero] = {'tree': tree, 'series': series}
        
        # Cargar series
        self.cargar_series_en_tree(genero)
    
    def cargar_series_en_tree(self, genero):
        """Cargar series de un género en su tree"""
        info = self.trees[genero]
        tree = info['tree']
        series = info['series']
        
        for item in tree.get_children():
            tree.delete(item)
        
        for serie in series:
            nombre = serie.get('name', 'Sin nombre')
            if len(nombre) > 50:
                nombre = nombre[:50] + "..."
            
            cat = serie.get('_categoria', 'N/A')[:3].upper()
            year = str(serie.get('year', ''))
            genero_full = serie.get('genre', serie.get('specificGenre', 'N/A'))
            if len(genero_full) > 35:
                genero_full = genero_full[:35] + "..."
            
            tree.insert('', 'end', values=(nombre, cat, year, genero_full))
    
    def filtrar_genero(self, event, genero):
        """Filtrar series dentro de un género"""
        info = self.trees[genero]
        tree = info['tree']
        series = info['series']
        termino = event.widget.get().lower().strip()
        
        for item in tree.get_children():
            tree.delete(item)
        
        for serie in series:
            nombre = serie.get('name', '').lower()
            if termino and termino not in nombre:
                continue
            
            nombre_display = serie.get('name', 'Sin nombre')
            if len(nombre_display) > 50:
                nombre_display = nombre_display[:50] + "..."
            
            cat = serie.get('_categoria', 'N/A')[:3].upper()
            year = str(serie.get('year', ''))
            genero_full = serie.get('genre', serie.get('specificGenre', 'N/A'))
            if len(genero_full) > 35:
                genero_full = genero_full[:35] + "..."
            
            tree.insert('', 'end', values=(nombre_display, cat, year, genero_full))
    
    def seleccionar_serie(self, event, genero):
        """Seleccionar serie del tree"""
        info = self.trees[genero]
        tree = info['tree']
        series = info['series']
        
        seleccion = tree.selection()
        if not seleccion:
            return
        
        index = tree.index(seleccion[0])
        items = tree.get_children()
        if index >= len(items):
            return
        
        # Encontrar la serie real
        nombre_seleccionado = tree.item(seleccion[0])['values'][0]
        for serie in series:
            if serie.get('name', '').startswith(nombre_seleccionado[:30]):
                self.serie_actual = serie
                break
        else:
            return
        
        self.cargar_serie_en_formulario()
    
    def crear_formulario_editor(self, parent):
        """Crear formulario de edición"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        self.frame_form = ttk.Frame(canvas)
        
        self.frame_form.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.frame_form, anchor='nw', width=1350)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        row = 0
        
        # Título
        ttk.Label(self.frame_form, text="INFORMACIÓN BÁSICA", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=4, sticky='w', pady=(0, 10))
        row += 1
        
        # Campos básicos
        campos = [
            ('nombre', 'Nombre:', 80),
            ('categoria', 'Categoría:', None),
            ('year', 'Año:', 10),
            ('generos', 'Géneros (separados por coma):', 80),
            ('primer_genero', '→ Clasificación:', None),
            ('imagen', 'URL Imagen:', 80),
        ]
        
        self.entries = {}
        for campo, label, ancho in campos:
            ttk.Label(self.frame_form, text=label).grid(row=row, column=0, sticky='w', pady=3)
            if ancho:
                entry = ttk.Entry(self.frame_form, width=ancho)
                entry.grid(row=row, column=1, sticky='ew', pady=3, columnspan=3)
                self.entries[campo] = entry
            else:
                lbl = ttk.Label(self.frame_form, text="-", font=('Arial', 10, 'bold'))
                lbl.grid(row=row, column=1, sticky='w', pady=3)
                self.entries[campo] = lbl
            row += 1
        
        # Sinopsis
        ttk.Label(self.frame_form, text="Sinopsis:").grid(row=row, column=0, sticky='nw', pady=3)
        self.text_sinopsis = scrolledtext.ScrolledText(self.frame_form, width=100, height=5, wrap=tk.WORD)
        self.text_sinopsis.grid(row=row, column=1, sticky='ew', pady=3, columnspan=3)
        row += 1
        
        # Botones
        frame_botones = ttk.Frame(self.frame_form)
        frame_botones.grid(row=row, column=0, columnspan=4, pady=10)
        
        ttk.Button(frame_botones, text="💾 Aplicar Cambios", command=self.aplicar_cambios, width=25).pack(side='left', padx=10)
        ttk.Button(frame_botones, text="🔄 Restaurar", command=self.cargar_serie_en_formulario, width=25).pack(side='left', padx=10)
        ttk.Button(frame_botones, text="➡️ Siguiente", command=self.siguiente_serie, width=25).pack(side='left', padx=10)
    
    def cargar_serie_en_formulario(self):
        """Cargar datos de la serie"""
        if not hasattr(self, 'serie_actual'):
            return
        
        s = self.serie_actual
        
        self.entries['nombre'].delete(0, tk.END)
        self.entries['nombre'].insert(0, s.get('name', ''))
        
        self.entries['categoria'].config(text=s.get('_categoria', 'N/A').upper())
        
        self.entries['year'].delete(0, tk.END)
        self.entries['year'].insert(0, str(s.get('year', '')))
        
        generos = s.get('genre', s.get('specificGenre', ''))
        self.entries['generos'].delete(0, tk.END)
        self.entries['generos'].insert(0, generos)
        
        primer = generos.split(',')[0].strip() if generos else 'N/A'
        self.entries['primer_genero'].config(text=primer, foreground='blue')
        
        self.entries['imagen'].delete(0, tk.END)
        self.entries['imagen'].insert(0, s.get('imagen_url', s.get('imagen', '')))
        
        self.text_sinopsis.delete(1.0, tk.END)
        self.text_sinopsis.insert(1.0, s.get('sinopsis', ''))
        
        self.label_status.config(text=f"✏️ Editando: {s.get('name', 'N/A')[:50]}...")
    
    def aplicar_cambios(self):
        """Aplicar cambios"""
        if not hasattr(self, 'serie_actual'):
            messagebox.showwarning("Atención", "Selecciona una serie primero")
            return
        
        s = self.serie_actual
        
        s['name'] = self.entries['nombre'].get().strip()
        try:
            s['year'] = int(self.entries['year'].get().strip())
        except:
            pass
        
        nuevo_genero = self.entries['generos'].get().strip()
        genero_anterior = s.get('genre', s.get('specificGenre', ''))
        
        s['genre'] = nuevo_genero
        s['imagen_url'] = self.entries['imagen'].get().strip()
        s['sinopsis'] = self.text_sinopsis.get(1.0, tk.END).strip()
        
        # Actualizar primer género en pantalla
        primer = nuevo_genero.split(',')[0].strip() if nuevo_genero else 'N/A'
        self.entries['primer_genero'].config(text=primer)
        
        # Si cambió el género principal, mover a otra pestaña
        primer_anterior = genero_anterior.split(',')[0].strip() if genero_anterior else 'N/A'
        if primer != primer_anterior:
            self.label_status.config(text=f"🔄 Género cambiado de '{primer_anterior}' a '{primer}'. Guarda y recarga.")
        else:
            self.label_status.config(text=f"✅ Cambios aplicados a: {s['name'][:40]}...")
        
        messagebox.showinfo("Éxito", "Cambios aplicados. ¡Recuerda guardar el JSON!")
        self.refrescar_trees()
    
    def refrescar_trees(self):
        """Refrescar todos los trees"""
        for genero in self.trees:
            self.cargar_series_en_tree(genero)
    
    def siguiente_serie(self):
        """Ir a siguiente serie"""
        if not hasattr(self, 'serie_actual'):
            return
        
        genero_actual = self.serie_actual.get('genre', '').split(',')[0].strip()
        if genero_actual not in self.trees:
            genero_actual = 'Otros'
        
        tree = self.trees[genero_actual]['tree']
        seleccion = tree.selection()
        
        if seleccion:
            siguiente = tree.next(seleccion[0])
            if siguiente:
                tree.selection_set(siguiente)
                tree.see(siguiente)
    
    def buscar_global(self, event=None):
        """Buscar en todos los géneros"""
        termino = self.entry_buscar.get().lower().strip()
        if not termino:
            return
        
        for genero, info in self.trees.items():
            tree = info['tree']
            series = info['series']
            
            for item in tree.get_children():
                tree.delete(item)
            
            for serie in series:
                nombre = serie.get('name', '').lower()
                if termino in nombre:
                    nombre_display = serie.get('name', 'Sin nombre')[:50]
                    cat = serie.get('_categoria', 'N/A')[:3].upper()
                    year = str(serie.get('year', ''))
                    genero_full = serie.get('genre', serie.get('specificGenre', 'N/A'))[:35]
                    tree.insert('', 'end', values=(nombre_display, cat, year, genero_full))
    
    def cambiar_vista(self, event=None):
        """Cambiar entre vista por género o categoría"""
        # Implementar si se necesita
        pass
    
    def guardar(self):
        """Guardar JSON"""
        try:
            for serie in self.todas_series:
                if '_categoria' in serie:
                    del serie['_categoria']
            
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            for serie in self.todas_series:
                for cat in ['anime', 'dibujos', 'peliculas', 'series']:
                    if serie in self.data.get(cat, []):
                        serie['_categoria'] = cat
                        break
            
            messagebox.showinfo("Éxito", "✅ JSON guardado")
            self.label_status.config(text="💾 Guardado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
    
    def regenerar_html(self):
        """Regenerar HTML"""
        import subprocess
        
        if not messagebox.askyesno("Confirmar", "¿Regenerar index.html?"):
            return
        
        try:
            self.label_status.config(text="🔄 Regenerando...")
            self.root.update()
            
            resultado = subprocess.run(
                ['python', r'c:\Users\Rafael\CascadeProjects\windsurf-project\generar_html_foroactivo.py'],
                capture_output=True, text=True, timeout=60
            )
            
            if resultado.returncode == 0:
                messagebox.showinfo("Éxito", "✅ HTML regenerado!")
                self.label_status.config(text="✅ HTML regenerado. Recarga la página.")
            else:
                messagebox.showerror("Error", f"Error:\n{resultado.stderr[:300]}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorPorGenero(root)
    root.mainloop()
