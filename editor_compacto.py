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
    
    def crear_widgets(self):
        """Crear interfaz compacta"""
        # Frame superior compacto
        frame_top = ttk.Frame(self.root, padding="5")
        frame_top.pack(fill='x')
        
        ttk.Label(frame_top, text="🎬 Editor", font=('Arial', 11, 'bold')).pack(side='left')
        
        self.entry_buscar = ttk.Entry(frame_top, width=30)
        self.entry_buscar.pack(side='left', padx=10)
        self.entry_buscar.bind('<Return>', self.buscar_global)
        ttk.Button(frame_top, text="🔍", command=self.buscar_global, width=4).pack(side='left')
        
        ttk.Button(frame_top, text="📋 Edición Masiva", command=self.edicion_masiva).pack(side='left', padx=10)
        ttk.Button(frame_top, text="📋 Copiar Lista", command=self.copiar_lista).pack(side='left', padx=2)
        
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
        self.label_categoria = ttk.Label(frame_fila1, text="-", width=8)
        self.label_categoria.pack(side='left', padx=2)
        
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
        
        # Ficha técnica colapsable
        self.frame_ficha = ttk.LabelFrame(frame_editor, text="Ficha Técnica ▼ (click para expandir)", padding="3")
        self.frame_ficha.pack(fill='x', pady=(5, 0))
        self.frame_ficha.bind('<Button-1>', self.toggle_ficha)
        self.frame_ficha_contenido = ttk.Frame(self.frame_ficha)
        # No mostrar contenido inicialmente
        
        self.entries_ficha = {}
        campos_ficha = [
            ('idioma', 'Idioma'), ('subtitulos', 'Subs'), ('calidad', 'Calidad'),
            ('resolucion', 'Resol.'), ('formato', 'Formato'), ('episodios', 'Eps'),
            ('audio', 'Audio'), ('creador', 'Creador')
        ]
        
        for i, (campo, label) in enumerate(campos_ficha):
            row = i // 4
            col = (i % 4) * 2
            ttk.Label(self.frame_ficha_contenido, text=f"{label}:", font=('Arial', 8)).grid(row=row, column=col, sticky='e', padx=2)
            entry = ttk.Entry(self.frame_ficha_contenido, width=18, font=('Arial', 8))
            entry.grid(row=row, column=col+1, sticky='ew', padx=2, pady=1)
            self.entries_ficha[campo] = entry
        
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
        
        for serie in series:
            nombre_completo = serie.get('name', '').lower()
            nombre_limpio = self.limpiar_nombre(serie.get('name', '')).lower()
            
            if termino and termino not in nombre_completo and termino not in nombre_limpio:
                continue
            
            nombre = self.limpiar_nombre(serie.get('name', ''))
            if len(nombre) > 45:
                nombre = nombre[:45] + "..."
            
            year = str(serie.get('year', ''))
            genero = serie.get('genre', serie.get('specificGenre', 'N/A'))
            if len(genero) > 20:
                genero = genero[:20] + "..."
            
            tree.insert('', 'end', values=(nombre, year, genero))
    
    def seleccionar_serie(self, event, cat_name):
        """Seleccionar serie"""
        tree = self.trees[cat_name]
        seleccion = tree.selection()
        if not seleccion:
            return
        
        index = tree.index(seleccion[0])
        series = self.categorias[cat_name]
        
        # Encontrar serie real
        nombre_sel = tree.item(seleccion[0])['values'][0]
        for serie in series:
            if self.limpiar_nombre(serie.get('name', '')).startswith(nombre_sel[:30]):
                self.serie_actual = serie
                break
        else:
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
        
        # Ficha técnica
        ficha = s.get('ficha_tecnica', {})
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
        
        s['genre'] = self.entry_generos.get().strip()
        s['imagen_url'] = self.entry_imagen.get().strip()
        s['sinopsis'] = self.text_sinopsis.get(1.0, tk.END).strip()
        
        # Detectar nuevo género
        genero_nuevo = s['genre'].split(',')[0].strip().capitalize() if s['genre'] else 'Sin Género'
        
        self.label_status.config(text=f"✅ Cambios aplicados")
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
    
    def refrescar_todos(self):
        """Refrescar todos los trees"""
        if self.modo_actual == 'categorias':
            for cat_name in self.categorias:
                self.cargar_series(cat_name)
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
    
    def guardar(self):
        """Guardar JSON"""
        try:
            for cat_items in self.categorias.values():
                for item in cat_items:
                    if '_categoria' in item:
                        del item['_categoria']
            
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
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
        
        # Resultado
        frame_result = ttk.Frame(ventana)
        frame_result.pack(fill='x', padx=10, pady=5)
        
        label_result = ttk.Label(frame_result, text="Listo para procesar")
        label_result.pack(side='left')
        
        def procesar():
            contenido = text_area.get(1.0, tk.END).strip()
            if not contenido:
                messagebox.showwarning("Atención", "No hay contenido para procesar")
                return
            
            lineas = [l.strip() for l in contenido.split('\n') if l.strip()]
            
            # Parsear pares nombre->género
            correcciones = {}
            i = 0
            while i < len(lineas):
                nombre = lineas[i]
                if i + 1 < len(lineas):
                    generos = lineas[i + 1]
                    correcciones[nombre] = generos
                    i += 2
                else:
                    i += 1
            
            if not correcciones:
                messagebox.showwarning("Atención", "No se encontraron pares válidos nombre->género")
                return
            
            # Aplicar correcciones
            actualizados = 0
            no_encontrados = []
            
            for nombre_txt, generos_txt in correcciones.items():
                nombre_buscado = self.limpiar_nombre(nombre_txt).lower()
                encontrado = False
                
                for cat_name, series in self.categorias.items():
                    for serie in series:
                        nombre_serie = self.limpiar_nombre(serie.get('name', '')).lower()
                        
                        # Coincidencia flexible
                        if nombre_buscado == nombre_serie or nombre_buscado in nombre_serie or nombre_serie in nombre_buscado:
                            serie['genre'] = generos_txt
                            actualizados += 1
                            encontrado = True
                            break
                    if encontrado:
                        break
                
                if not encontrado:
                    no_encontrados.append(nombre_txt)
            
            # Reportar resultado
            resultado = f"✅ Actualizados: {actualizados}/{len(correcciones)}\n"
            if no_encontrados:
                resultado += f"❌ No encontrados: {len(no_encontrados)}\n"
                for nombre in no_encontrados[:5]:
                    resultado += f"  - {nombre[:40]}...\n"
            
            label_result.config(text=resultado)
            
            if actualizados > 0:
                self.refrescar_todos()
                messagebox.showinfo("Éxito", f"✅ {actualizados} series actualizadas\n\nRecuerda guardar el JSON (💾)")
                ventana.destroy()
        
        # Botones
        frame_botones = ttk.Frame(ventana)
        frame_botones.pack(pady=10)
        
        ttk.Button(frame_botones, text="✅ Procesar y Aplicar", command=procesar, width=20).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="❌ Cancelar", command=ventana.destroy, width=15).pack(side='left', padx=5)
    
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

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorCompacto(root)
    root.mainloop()
