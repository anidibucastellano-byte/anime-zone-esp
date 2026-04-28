"""
Editor Compacto por Géneros para TOP.json
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import re

class EditorGeneroCompacto:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor por Géneros - AnimeZoneESP")
        self.root.geometry("1100x700")
        
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
        
        print(f"📊 Total: {len(self.todas_series)} series en {len(self.generos)} géneros")
    
    def limpiar_nombre(self, nombre):
        """Limpiar nombre de formato técnico"""
        if not nombre:
            return 'Sin nombre'
        nombre = re.sub(r'\[.*?\]', '', nombre)
        nombre = nombre.replace('(Activo)', '').replace('(Finalizado)', '')
        nombre = re.sub(r'\(.*?\)', '', nombre)
        nombre = re.sub(r'\s+', ' ', nombre)
        return nombre.strip()
    
    def crear_widgets(self):
        """Crear interfaz compacta"""
        # Frame superior
        frame_top = ttk.Frame(self.root, padding="5")
        frame_top.pack(fill='x')
        
        ttk.Label(frame_top, text="🎭 Editor por Géneros", font=('Arial', 11, 'bold')).pack(side='left')
        
        self.entry_buscar = ttk.Entry(frame_top, width=30)
        self.entry_buscar.pack(side='left', padx=10)
        self.entry_buscar.bind('<Return>', self.buscar_global)
        ttk.Button(frame_top, text="🔍", command=self.buscar_global, width=4).pack(side='left')
        
        ttk.Button(frame_top, text="💾 Guardar", command=self.guardar).pack(side='right', padx=2)
        ttk.Button(frame_top, text="🔄 HTML", command=self.regenerar_html).pack(side='right', padx=2)
        
        # Notebook con pestañas de géneros (top 10 + Otros)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=2)
        
        self.tabs = {}
        self.trees = {}
        
        # Crear pestañas para los géneros principales (top 10) + "Otros"
        generos_principales = self.generos_ordenados[:10]
        otros_generos = [g for g, _ in self.generos_ordenados[10:]]
        
        for genero, series in generos_principales:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"{genero} ({len(series)})")
            self.tabs[genero] = tab
            self.crear_tab_genero(tab, genero)
        
        # Pestaña "Otros" con el resto de géneros
        if otros_generos:
            tab_otros = ttk.Frame(self.notebook)
            otros_series = []
            for g in otros_generos:
                otros_series.extend(self.generos[g])
            self.notebook.add(tab_otros, text=f"Otros ({len(otros_series)})")
            self.tabs['Otros'] = tab_otros
            self.crear_tab_otros(tab_otros, otros_generos)
        
        # Panel inferior - Editor compacto
        frame_editor = ttk.LabelFrame(self.root, text="✏️ Editar Serie", padding="5")
        frame_editor.pack(fill='x', side='bottom', padx=5, pady=2)
        
        # Frame izquierdo
        frame_izq = ttk.Frame(frame_editor)
        frame_izq.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        ttk.Label(frame_izq, text="Nombre:").pack(anchor='w')
        self.entry_nombre = ttk.Entry(frame_izq, width=60)
        self.entry_nombre.pack(fill='x', pady=(0, 5))
        
        frame_fila1 = ttk.Frame(frame_izq)
        frame_fila1.pack(fill='x', pady=2)
        
        ttk.Label(frame_fila1, text="Año:").pack(side='left')
        self.entry_year = ttk.Entry(frame_fila1, width=8)
        self.entry_year.pack(side='left', padx=(2, 10))
        
        ttk.Label(frame_fila1, text="Cat:").pack(side='left')
        self.label_categoria = ttk.Label(frame_fila1, text="-", width=8)
        self.label_categoria.pack(side='left', padx=2)
        
        ttk.Label(frame_fila1, text="Clasif:").pack(side='left')
        self.label_primer_genero = ttk.Label(frame_fila1, text="-", foreground='blue', width=12)
        self.label_primer_genero.pack(side='left', padx=2)
        
        ttk.Label(frame_izq, text="Géneros:").pack(anchor='w', pady=(5, 0))
        self.entry_generos = ttk.Entry(frame_izq, width=60)
        self.entry_generos.pack(fill='x')
        self.entry_generos.bind('<KeyRelease>', self.actualizar_primer_genero)
        
        frame_urls = ttk.Frame(frame_izq)
        frame_urls.pack(fill='x', pady=5)
        
        ttk.Label(frame_urls, text="Imagen:").pack(side='left')
        self.entry_imagen = ttk.Entry(frame_urls, width=50)
        self.entry_imagen.pack(side='left', fill='x', expand=True, padx=2)
        
        # Frame derecho
        frame_der = ttk.Frame(frame_editor)
        frame_der.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        ttk.Label(frame_der, text="Sinopsis:").pack(anchor='w')
        self.text_sinopsis = tk.Text(frame_der, width=50, height=4, wrap=tk.WORD)
        self.text_sinopsis.pack(fill='both', expand=True)
        
        frame_botones = ttk.Frame(frame_der)
        frame_botones.pack(fill='x', pady=(5, 0))
        
        ttk.Button(frame_botones, text="✅ Aplicar", command=self.aplicar_cambios, width=12).pack(side='left', padx=2)
        ttk.Button(frame_botones, text="🔄 Restaurar", command=self.cargar_serie, width=12).pack(side='left', padx=2)
        ttk.Button(frame_botones, text="➡️ Siguiente", command=self.siguiente_serie, width=12).pack(side='left', padx=2)
        
        # Status bar
        self.label_status = ttk.Label(self.root, text="Selecciona una serie", relief='sunken', font=('Arial', 9))
        self.label_status.pack(fill='x', side='bottom')
    
    def crear_tab_genero(self, tab, genero):
        """Crear pestaña para un género"""
        frame_lista = ttk.Frame(tab)
        frame_lista.pack(fill='both', expand=True)
        
        # Búsqueda local
        frame_busq = ttk.Frame(frame_lista)
        frame_busq.pack(fill='x', pady=2)
        ttk.Label(frame_busq, text="Filtrar:").pack(side='left')
        entry_filtro = ttk.Entry(frame_busq, width=30)
        entry_filtro.pack(side='left', padx=3)
        entry_filtro.bind('<KeyRelease>', lambda e, g=genero: self.filtrar_genero(e, g))
        
        # Tree
        cols = ('nombre', 'cat', 'year', 'genero')
        tree = ttk.Treeview(frame_lista, columns=cols, show='headings', height=18)
        
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
        
        # Filtro
        frame_busq = ttk.Frame(frame_lista)
        frame_busq.pack(fill='x', pady=2)
        ttk.Label(frame_busq, text="Filtrar:").pack(side='left')
        entry_filtro = ttk.Entry(frame_busq, width=30)
        entry_filtro.pack(side='left', padx=3)
        entry_filtro.bind('<KeyRelease>', lambda e, gl=generos_list: self.filtrar_otros(e, gl))
        
        # Tree con columna de género
        cols = ('nombre', 'cat', 'year', 'genero')
        tree = ttk.Treeview(frame_lista, columns=cols, show='headings', height=18)
        
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
        
        # Encontrar la serie en la lista combinada
        todas = []
        for genero in generos_list:
            todas.extend(self.generos[genero])
        
        if index < len(todas):
            self.serie_actual = todas[index]
            self.cargar_serie()
    
    def cargar_serie(self):
        """Cargar serie en formulario"""
        if not hasattr(self, 'serie_actual'):
            return
        
        s = self.serie_actual
        
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, s.get('name', ''))
        
        self.entry_year.delete(0, tk.END)
        self.entry_year.insert(0, str(s.get('year', '')))
        
        self.label_categoria.config(text=s.get('_categoria', 'N/A').upper())
        
        generos = s.get('genre', s.get('specificGenre', ''))
        self.entry_generos.delete(0, tk.END)
        self.entry_generos.insert(0, generos)
        self.actualizar_primer_genero()
        
        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, s.get('imagen_url', s.get('imagen', '')))
        
        self.text_sinopsis.delete(1.0, tk.END)
        self.text_sinopsis.insert(1.0, s.get('sinopsis', '')[:300])
        
        self.label_status.config(text=f"Editando: {self.limpiar_nombre(s.get('name', ''))[:40]}")
    
    def actualizar_primer_genero(self, event=None):
        """Actualizar primer género"""
        generos = self.entry_generos.get().strip()
        primer = generos.split(',')[0].strip() if generos else 'N/A'
        self.label_primer_genero.config(text=primer[:12])
    
    def aplicar_cambios(self):
        """Aplicar cambios"""
        if not hasattr(self, 'serie_actual'):
            messagebox.showwarning("Atención", "Selecciona una serie")
            return
        
        s = self.serie_actual
        
        s['name'] = self.entry_nombre.get().strip()
        try:
            s['year'] = int(self.entry_year.get().strip())
        except:
            pass
        
        s['genre'] = self.entry_generos.get().strip()
        s['imagen_url'] = self.entry_imagen.get().strip()
        s['sinopsis'] = self.text_sinopsis.get(1.0, tk.END).strip()
        
        self.label_status.config(text=f"✅ Cambios aplicados")
        self.refrescar_todos()
    
    def refrescar_todos(self):
        """Refrescar todos los trees"""
        for genero in self.generos:
            if genero in self.trees:
                self.cargar_series_genero(genero)
        if 'Otros' in self.trees:
            otros = [g for g, _ in self.generos_ordenados[10:]]
            self.cargar_series_otros(otros)
    
    def siguiente_serie(self):
        """Siguiente serie"""
        if not hasattr(self, 'serie_actual'):
            return
        
        # Encontrar en qué género está
        genero_actual = None
        for genero, series in self.generos.items():
            if self.serie_actual in series:
                genero_actual = genero
                break
        
        if genero_actual and genero_actual in self.trees:
            tree = self.trees[genero_actual]
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
        
        # Buscar en todos los géneros
        for genero, series in self.generos.items():
            for i, serie in enumerate(series):
                if termino in serie.get('name', '').lower() or \
                   termino in self.limpiar_nombre(serie.get('name', '')).lower():
                    # Cambiar a esa pestaña
                    if genero in self.tabs:
                        self.notebook.select(self.tabs[genero])
                    elif 'Otros' in self.tabs:
                        self.notebook.select(self.tabs['Otros'])
                    
                    tree = self.trees.get(genero) or self.trees.get('Otros')
                    if tree:
                        items = tree.get_children()
                        if i < len(items):
                            tree.selection_set(items[i])
                            tree.see(items[i])
                            self.serie_actual = serie
                            self.cargar_serie()
                            return
        
        self.label_status.config(text=f"No encontrado: {termino}")
    
    def guardar(self):
        """Guardar JSON"""
        try:
            # Limpiar campos temporales
            for serie in self.todas_series:
                if '_categoria' in serie:
                    del serie['_categoria']
            
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            # Restaurar campos temporales
            for serie in self.todas_series:
                for cat in ['anime', 'dibujos', 'peliculas', 'series']:
                    if serie in self.data.get(cat, []):
                        serie['_categoria'] = cat
                        break
            
            messagebox.showinfo("Éxito", "✅ Guardado")
            self.label_status.config(text="💾 JSON guardado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def regenerar_html(self):
        """Regenerar HTML"""
        import subprocess
        import os
        
        if not messagebox.askyesno("Confirmar", "¿Regenerar HTML?"):
            return
        
        try:
            self.label_status.config(text="🔄 Regenerando...")
            self.root.update()
            
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

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorGeneroCompacto(root)
    root.mainloop()
