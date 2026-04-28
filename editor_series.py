"""
Editor GUI para TOP.json
Permite editar géneros e imágenes manualmente
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import re

class EditorSeries:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Series - AnimeZoneESP")
        self.root.geometry("900x700")
        
        # Ruta al JSON
        self.ruta_json = Path(r'c:\Users\Rafael\CascadeProjects\windsurf-project\TOP.json')
        
        # Cargar datos
        self.cargar_datos()
        
        # Crear interfaz
        self.crear_widgets()
        
    def cargar_datos(self):
        """Cargar datos del JSON"""
        with open(self.ruta_json, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # Crear lista plana de todas las series
        self.todas_series = []
        for categoria in ['anime', 'dibujos', 'peliculas', 'series']:
            if categoria in self.data:
                for item in self.data[categoria]:
                    item['_categoria'] = categoria
                    self.todas_series.append(item)
        
        print(f"📊 Total series cargadas: {len(self.todas_series)}")
    
    def crear_widgets(self):
        """Crear widgets de la interfaz"""
        # Frame superior - Búsqueda
        frame_busqueda = ttk.Frame(self.root, padding="10")
        frame_busqueda.pack(fill='x')
        
        ttk.Label(frame_busqueda, text="Buscar:").pack(side='left')
        self.entry_buscar = ttk.Entry(frame_busqueda, width=50)
        self.entry_buscar.pack(side='left', padx=5)
        self.entry_buscar.bind('<KeyRelease>', self.buscar)
        
        ttk.Button(frame_busqueda, text="🔍 Buscar", command=self.buscar).pack(side='left', padx=5)
        ttk.Button(frame_busqueda, text="💾 Guardar Cambios", command=self.guardar).pack(side='left', padx=5)
        ttk.Button(frame_busqueda, text="🔄 Regenerar HTML", command=self.regenerar_html).pack(side='left', padx=5)
        
        # Frame central - Lista y Detalles
        frame_central = ttk.Frame(self.root, padding="10")
        frame_central.pack(fill='both', expand=True)
        
        # Lista de series (izquierda)
        frame_lista = ttk.LabelFrame(frame_central, text="Series Encontradas", padding="5")
        frame_lista.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Scrollbar + Listbox
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')
        
        self.listbox = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, width=60, height=20)
        self.listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        self.listbox.bind('<<ListboxSelect>>', self.mostrar_detalles)
        
        # Detalles de la serie (derecha)
        frame_detalles = ttk.LabelFrame(frame_central, text="Detalles de la Serie", padding="10")
        frame_detalles.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Campos editables
        ttk.Label(frame_detalles, text="Nombre:").pack(anchor='w')
        self.label_nombre = ttk.Label(frame_detalles, text="-", wraplength=300)
        self.label_nombre.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(frame_detalles, text="Categoría:").pack(anchor='w')
        self.label_categoria = ttk.Label(frame_detalles, text="-")
        self.label_categoria.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(frame_detalles, text="Género (lista completa):").pack(anchor='w')
        self.entry_genero = ttk.Entry(frame_detalles, width=50)
        self.entry_genero.pack(fill='x', pady=(0, 5))
        
        ttk.Label(frame_detalles, text="Primer género (para clasificación):").pack(anchor='w')
        self.label_primer_genero = ttk.Label(frame_detalles, text="-", foreground='blue')
        self.label_primer_genero.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(frame_detalles, text="URL Imagen:").pack(anchor='w')
        self.entry_imagen = ttk.Entry(frame_detalles, width=50)
        self.entry_imagen.pack(fill='x', pady=(0, 5))
        
        # Botón para aplicar cambios a la serie seleccionada
        ttk.Button(frame_detalles, text="✅ Aplicar Cambios", command=self.aplicar_cambios).pack(fill='x', pady=(10, 0))
        
        # Sinopsis (solo lectura)
        ttk.Label(frame_detalles, text="Sinopsis:").pack(anchor='w', pady=(10, 0))
        self.text_sinopsis = scrolledtext.ScrolledText(frame_detalles, width=40, height=6, wrap=tk.WORD)
        self.text_sinopsis.pack(fill='both', expand=True)
        self.text_sinopsis.config(state='disabled')
        
        # Frame inferior - Info
        frame_info = ttk.Frame(self.root, padding="10")
        frame_info.pack(fill='x', side='bottom')
        
        self.label_info = ttk.Label(frame_info, text="Usa el buscador para encontrar series. Selecciona una para editar.")
        self.label_info.pack()
        
        # Cargar todas las series inicialmente
        self.actualizar_lista(self.todas_series[:100])  # Mostrar primeras 100
    
    def buscar(self, event=None):
        """Buscar series por nombre"""
        termino = self.entry_buscar.get().lower().strip()
        
        if not termino:
            # Mostrar primeras 100
            resultados = self.todas_series[:100]
        else:
            # Buscar coincidencias
            resultados = []
            for item in self.todas_series:
                nombre = item.get('name', '').lower()
                if termino in nombre:
                    resultados.append(item)
        
        self.actualizar_lista(resultados)
        self.label_info.config(text=f"Encontradas: {len(resultados)} series")
    
    def actualizar_lista(self, series):
        """Actualizar la lista mostrada"""
        self.listbox.delete(0, tk.END)
        self.series_mostradas = series
        
        for item in series:
            nombre = item.get('name', 'Sin nombre')
            # Truncar si es muy largo
            if len(nombre) > 55:
                nombre = nombre[:55] + "..."
            self.listbox.insert(tk.END, nombre)
    
    def mostrar_detalles(self, event=None):
        """Mostrar detalles de la serie seleccionada"""
        seleccion = self.listbox.curselection()
        if not seleccion:
            return
        
        index = seleccion[0]
        if index >= len(self.series_mostradas):
            return
        
        self.serie_actual = self.series_mostradas[index]
        
        # Actualizar campos
        self.label_nombre.config(text=self.serie_actual.get('name', 'N/A'))
        self.label_categoria.config(text=self.serie_actual.get('_categoria', 'N/A').upper())
        
        # Género
        genero_actual = self.serie_actual.get('genre', self.serie_actual.get('specificGenre', ''))
        self.entry_genero.delete(0, tk.END)
        self.entry_genero.insert(0, genero_actual)
        
        # Primer género
        primer_genero = genero_actual.split(',')[0].strip() if genero_actual else 'N/A'
        self.label_primer_genero.config(text=primer_genero)
        
        # Imagen
        imagen_actual = self.serie_actual.get('imagen_url', self.serie_actual.get('imagen', ''))
        self.entry_imagen.delete(0, tk.END)
        self.entry_imagen.insert(0, imagen_actual)
        
        # Sinopsis
        self.text_sinopsis.config(state='normal')
        self.text_sinopsis.delete(1.0, tk.END)
        self.text_sinopsis.insert(1.0, self.serie_actual.get('sinopsis', 'Sin sinopsis')[:300])
        self.text_sinopsis.config(state='disabled')
        
        self.label_info.config(text=f"Editando: {self.serie_actual.get('name', 'N/A')[:50]}...")
    
    def aplicar_cambios(self):
        """Aplicar cambios a la serie seleccionada"""
        if not hasattr(self, 'serie_actual'):
            messagebox.showwarning("Atención", "Selecciona una serie primero")
            return
        
        # Actualizar género
        nuevo_genero = self.entry_genero.get().strip()
        if nuevo_genero:
            self.serie_actual['genre'] = nuevo_genero
            # Actualizar label de primer género
            primer_genero = nuevo_genero.split(',')[0].strip()
            self.label_primer_genero.config(text=primer_genero)
        
        # Actualizar imagen
        nueva_imagen = self.entry_imagen.get().strip()
        if nueva_imagen:
            self.serie_actual['imagen_url'] = nueva_imagen
        
        self.label_info.config(text=f"✅ Cambios aplicados a: {self.serie_actual.get('name', 'N/A')[:40]}...")
        messagebox.showinfo("Éxito", "Cambios aplicados. Recuerda guardar (Ctrl+S o botón Guardar)")
    
    def guardar(self):
        """Guardar cambios en el JSON"""
        try:
            # Eliminar el campo auxiliar _categoria antes de guardar
            for item in self.todas_series:
                if '_categoria' in item:
                    del item['_categoria']
            
            # Guardar
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            # Recargar datos (para restaurar _categoria)
            self.cargar_datos()
            
            messagebox.showinfo("Éxito", "✅ Cambios guardados en TOP.json")
            self.label_info.config(text="💾 Cambios guardados correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")
    
    def regenerar_html(self):
        """Ejecutar script para regenerar HTML"""
        import subprocess
        
        respuesta = messagebox.askyesno("Confirmar", "¿Regenerar index.html con los cambios actuales?")
        if not respuesta:
            return
        
        try:
            self.label_info.config(text="🔄 Regenerando HTML...")
            self.root.update()
            
            resultado = subprocess.run(
                ['python', r'c:\Users\Rafael\CascadeProjects\windsurf-project\generar_html_foroactivo.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if resultado.returncode == 0:
                messagebox.showinfo("Éxito", "✅ HTML regenerado correctamente\n\nRecarga la página en el navegador para ver los cambios")
                self.label_info.config(text="✅ HTML regenerado. Recarga la página.")
            else:
                messagebox.showerror("Error", f"Error al regenerar HTML:\n{resultado.stderr[:500]}")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo regenerar HTML:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorSeries(root)
    root.mainloop()
