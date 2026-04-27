# 🎬 Web Anime Zone ESP - Estilo Netflix

Sistema para generar una web tipo Netflix con miniaturas de anime/series extraídas automáticamente del foro.

## 📁 Archivos Importantes

- **`actualizar_web_con_imagenes.py`** - Script maestro (ejecutar este)
- **`extraer_imagenes_foro.py`** - Extrae imágenes del foro (requiere login)
- **`generar_html_foroactivo.py`** - Genera el HTML con diseño Netflix
- **`TOP.json`** - Base de datos con todas las series

## 🚀 Uso Rápido

1. **Abre el panel de control** (si no está abierto):
   ```
   python panel_server.py
   ```

2. **Ejecuta el actualizador**:
   ```
   python actualizar_web_con_imagenes.py
   ```

3. **Sigue las instrucciones**:
   - El script extraerá automáticamente las imágenes del foro
   - Generará `index.html` con diseño tipo Netflix
   - Creará la carpeta `images/` con las miniaturas

4. **Sube a GitHub**:
   - Sube `index.html` a tu repositorio
   - Activa GitHub Pages en Settings > Pages
   - Selecciona "Deploy from a branch" → main → / (root)

## 🎨 Características del Diseño

- **Grid tipo Netflix**: Tarjetas con aspect ratio 2:3
- **Miniaturas automáticas**: Se extraen de los temas del foro
- **Placeholder inteligente**: Emoji según tipo (🍜 anime, 🎨 dibujos, 🎬 películas, 📺 series)
- **Hover effects**: Zoom, sombra, gradiente
- **Responsive**: Se adapta a móvil, tablet y desktop
- **Filtros**: Por década, género, tipo y búsqueda

## 🔧 Credenciales del Foro

Las credenciales están configuradas en `extraer_imagenes_foro.py`:
- Usuario: `Admin`
- Password: `9XsBiygA2CpqgB9`

## 🐛 Solución de Problemas

### No se extraen las imágenes
- Verifica que puedes acceder al foro con las credenciales
- Algunos temas pueden no tener imágenes (usarán placeholder)

### Las imágenes no se ven en la web
- Asegúrate de subir también la carpeta `images/` a GitHub
- Las imágenes se referencian con ruta relativa: `images/nombre.jpg`

### Error al generar HTML
- Verifica que `TOP.json` existe y tiene datos
- Ejecuta primero el script de extracción de URLs del foro

## 📂 Estructura del Proyecto

```
windsurf-project/
├── index.html              ← Web generada (subir a GitHub)
├── images/                 ← Miniaturas extraídas (subir a GitHub)
│   ├── anime_1_Nombre.jpg
│   ├── serie_5_Otro.jpg
│   └── ...
├── TOP.json                ← Base de datos
├── actualizar_web_con_imagenes.py
├── extraer_imagenes_foro.py
└── generar_html_foroactivo.py
```

## 🌐 URL Final

Una vez subido a GitHub Pages:
```
https://anidibucastellano-byte.github.io/anime-zone-esp/
```

## 📝 Notas

- Las imágenes se descargan una sola vez y se guardan localmente
- Si una serie no tiene imagen, se muestra un placeholder con emoji
- El diseño es responsive y funciona en móviles
- Las tarjetas tienen animaciones al pasar el mouse (hover)
