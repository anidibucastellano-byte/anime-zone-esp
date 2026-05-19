import tkinter as tk
from tkinter import ttk, messagebox
import base64

# Configuración de colores para estética Cyberpunk/Anime Premium
COLOR_BG = "#0c0c0f"          # Negro profundo
COLOR_CARD = "#14141a"        # Gris tarjeta oscuro
COLOR_BORDER = "#252530"      # Gris borde
COLOR_TEXT_MAIN = "#ffffff"   # Blanco
COLOR_TEXT_MUTED = "#8c8c9e"  # Gris apagado
COLOR_RED = "#ff3c3c"         # Rojo neón
COLOR_GOLD = "#f5b041"        # Oro brillante
COLOR_GREEN = "#2ecc71"       # Verde éxito

class EncriptadorMegaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AZ-MegaCrypt • Encriptador de Enlaces")
        self.root.geometry("620x420")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG)
        
        # Configurar estilos de ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Estilo de botones
        self.style.configure('Custom.TButton', 
                             background=COLOR_RED, 
                             foreground=COLOR_TEXT_MAIN, 
                             font=('Arial', 10, 'bold'), 
                             borderwidth=0, 
                             focusthickness=0)
        self.style.map('Custom.TButton', 
                       background=[('active', '#e03232'), ('pressed', '#c02828')])
        
        self.style.configure('Clear.TButton', 
                             background='#2c2c38', 
                             foreground=COLOR_TEXT_MAIN, 
                             font=('Arial', 9), 
                             borderwidth=0)
        self.style.map('Clear.TButton', 
                       background=[('active', '#3d3d4e'), ('pressed', '#1a1a24')])

        # Centrar la ventana en la pantalla
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self.crear_interfaz()

    def crear_interfaz(self):
        # Contenedor principal con margen
        main_frame = tk.Frame(self.root, bg=COLOR_BG, padx=25, pady=20)
        main_frame.pack(fill='both', expand=True)

        # CABECERA
        header_frame = tk.Frame(main_frame, bg=COLOR_BG)
        header_frame.pack(fill='x', pady=(0, 15))
        
        # Título principal brillante
        title_label = tk.Label(header_frame, 
                               text="⚡ ANIMEZONEESP", 
                               font=('Arial', 16, 'bold'), 
                               fg=COLOR_GOLD, 
                               bg=COLOR_BG)
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(header_frame, 
                                  text="Protector y Encriptador de Enlaces de MEGA para Foroactivo", 
                                  font=('Arial', 9), 
                                  fg=COLOR_TEXT_MUTED, 
                                  bg=COLOR_BG)
        subtitle_label.pack(anchor='w')

        # SECCIÓN DE ENTRADA (PEGAR ENLACE)
        input_frame = tk.LabelFrame(main_frame, 
                                    text="🔗 Pegar Enlace de MEGA (mega.nz o mega.co.nz)", 
                                    font=('Arial', 9, 'bold'),
                                    fg=COLOR_TEXT_MAIN, 
                                    bg=COLOR_CARD, 
                                    padx=15, 
                                    pady=12,
                                    bd=1,
                                    relief='solid',
                                    highlightbackground=COLOR_BORDER)
        input_frame.pack(fill='x', pady=5)
        
        self.entry_input = tk.Entry(input_frame, 
                                    font=('Consolas', 10), 
                                    bg="#0e0e12", 
                                    fg=COLOR_TEXT_MAIN, 
                                    insertbackground=COLOR_TEXT_MAIN,
                                    bd=1, 
                                    relief='solid',
                                    highlightthickness=1,
                                    highlightbackground=COLOR_BORDER,
                                    highlightcolor=COLOR_RED)
        self.entry_input.pack(fill='x', ipady=6, pady=(5, 5))
        self.entry_input.focus_set()
        
        # Vincular la tecla Enter para encriptar de inmediato
        self.entry_input.bind('<Return>', lambda e: self.encriptar_enlace())

        # BOTONES DE ACCIÓN
        buttons_frame = tk.Frame(main_frame, bg=COLOR_BG)
        buttons_frame.pack(fill='x', pady=10)
        
        btn_encrypt = ttk.Button(buttons_frame, 
                                 text="🔐 Encriptar y Copiar", 
                                 style='Custom.TButton',
                                 command=self.encriptar_enlace,
                                 width=22)
        btn_encrypt.pack(side='left', padx=(0, 10))
        
        btn_clear = ttk.Button(buttons_frame, 
                               text="🧹 Limpiar Campos", 
                               style='Clear.TButton',
                               command=self.limpiar_campos,
                               width=15)
        btn_clear.pack(side='left')

        # SECCIÓN DE SALIDA (RESULTADO)
        output_frame = tk.LabelFrame(main_frame, 
                                     text="🛡️ Enlace Protegido Generado", 
                                     font=('Arial', 9, 'bold'),
                                     fg=COLOR_GOLD, 
                                     bg=COLOR_CARD, 
                                     padx=15, 
                                     pady=12,
                                     bd=1,
                                     relief='solid',
                                     highlightbackground=COLOR_BORDER)
        output_frame.pack(fill='x', pady=5)

        self.entry_output = tk.Entry(output_frame, 
                                     font=('Consolas', 10), 
                                     bg="#0e0e12", 
                                     fg=COLOR_GREEN, 
                                     bd=1, 
                                     relief='solid',
                                     highlightthickness=1,
                                     highlightbackground=COLOR_BORDER,
                                     state='readonly')
        self.entry_output.pack(fill='x', ipady=6, pady=(5, 5))

        # ETIQUETA DE ESTADO / ALERTA
        self.status_label = tk.Label(main_frame, 
                                     text="Listo para proteger tus enlaces.", 
                                     font=('Arial', 9, 'italic'), 
                                     fg=COLOR_TEXT_MUTED, 
                                     bg=COLOR_BG)
        self.status_label.pack(fill='x', pady=(10, 0))

    def encriptar_enlace(self):
        url = self.entry_input.get().strip()
        
        if not url:
            self.mostrar_estado("Error: Por favor, pega un enlace primero.", COLOR_RED)
            messagebox.showwarning("Campo Vacío", "Debes pegar un enlace de MEGA para poder encriptarlo.")
            return

        # Validar si es un enlace de MEGA
        if not ("mega.nz" in url or "mega.co.nz" in url):
            self.mostrar_estado("Error: El enlace no parece ser de MEGA.", COLOR_RED)
            confirmar = messagebox.askyesno("Enlace No Reconocido", 
                                             "El enlace proporcionado no parece ser de mega.nz o mega.co.nz.\n"
                                             "¿Deseas encriptarlo de todas formas?")
            if not confirmar:
                return

        try:
            # Algoritmo exclusivo AnimeZoneESP (Base64 + Reversión + Prefijo/Sufijo)
            # 1. Pasar a Base64
            url_bytes = url.encode('utf-8')
            b64_bytes = base64.b64encode(url_bytes)
            b64_str = b64_bytes.decode('utf-8')
            
            # 2. Invertir la cadena
            reversed_b64 = b64_str[::-1]
            
            # 3. Empaquetar con firma AnimeZone
            codigo_cifrado = f"AZ_{reversed_b64}_EP"
            
            # 4. Construir la URL final del redirector en GitHub Pages
            url_publica = f"https://anidibucastellano-byte.github.io/anime-zone-esp/decode.html#{codigo_cifrado}"
            
            # Mostrar resultado en el campo de salida
            self.entry_output.config(state='normal')
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, url_publica)
            self.entry_output.config(state='readonly')
            
            # Copiar automáticamente al portapapeles de forma nativa
            self.root.clipboard_clear()
            self.root.clipboard_append(url_publica)
            self.root.update() # Asegura que el portapapeles se actualice
            
            self.mostrar_estado("¡Enlace protegido y copiado al portapapeles automáticamente! 📋", COLOR_GREEN)
            
        except Exception as e:
            self.mostrar_estado(f"Error al encriptar: {str(e)}", COLOR_RED)
            messagebox.showerror("Error", f"Ocurrió un error inesperado al procesar el enlace:\n{str(e)}")

    def limpiar_campos(self):
        self.entry_input.delete(0, tk.END)
        self.entry_output.config(state='normal')
        self.entry_output.delete(0, tk.END)
        self.entry_output.config(state='readonly')
        self.mostrar_estado("Campos limpiados. Listo para un nuevo enlace.", COLOR_TEXT_MUTED)
        self.entry_input.focus_set()

    def mostrar_estado(self, texto, color):
        self.status_label.config(text=texto, fg=color)

if __name__ == "__main__":
    root = tk.Tk()
    app = EncriptadorMegaApp(root)
    root.mainloop()
