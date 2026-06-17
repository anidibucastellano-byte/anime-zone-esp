#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ForoActivo → Telegram Bot
=========================
Detecta nuevos temas en la sección Castellano (f11) de AnimeZoneEsp y los
publica automáticamente en el topic "Series Anime y Dibujos Animados" del
grupo de Telegram, evitando duplicados.

Incluye autenticación en ForoActivo para acceder a imágenes de posts privados.

Dependencias:
    pip install feedparser requests python-dotenv beautifulsoup4 lxml

Uso:
    python foroactivo_to_telegram.py
"""

import feedparser
import requests
import json
import os
import re
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────

load_dotenv()  # Carga variables desde el archivo .env

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

# ID del topic dentro del grupo de Telegram (grupos con modo Foro activado).
# Déjalo en None / vacío si publicas en un canal normal sin topics.
TELEGRAM_THREAD_ID = os.getenv("TELEGRAM_THREAD_ID", None)
if TELEGRAM_THREAD_ID:
    TELEGRAM_THREAD_ID = int(TELEGRAM_THREAD_ID)

# Mapeo de subforos a topics de Telegram
FORUM_THREAD_MAPPING = {
    "f11": 50,  # Series Anime y Dibujos Animados
    "f14": 54,  # Peliculas Anime y Dibujos Animados
    "f17": 59,  # Series Live-Action
    "f21": 62,  # Peliculas Live-Action
}

# Credenciales de ForoActivo para poder acceder a imágenes de posts.
# Se guardan solo en el .env local, nunca se suben a Git.
FORO_BASE_URL = "https://animezoneesp.foroactivo.com"
FORO_USERNAME = os.getenv("FORO_USERNAME", "")
FORO_PASSWORD = os.getenv("FORO_PASSWORD", "")

# ──────────────────────────────────────────────────────────────────────────────
# Feeds RSS de ForoActivo.
# NOTA: el feed /f11-castellano?mode=topics_feed no devuelve XML válido;
# el feed global /feed sí funciona y contiene los últimos temas de todas las
# secciones, incluyendo los de Castellano (f11). Lo filtramos por URL.
# ──────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = {
    "Castellano 🎌": "https://animezoneesp.foroactivo.com/feed",
}

# Solo publicar temas cuya URL contenga alguno de estos segmentos.
# Así filtramos el feed global para quedarnos solo con f11.
# Déjalo vacío para publicar todos los temas del feed sin filtrar.
FORO_SECTION_FILTER = [
    # Todos los temas de la sección Castellano empiezan por /t seguido de número.
    # Filtramos por las palabras clave que aparecen en sus URLs o títulos.
    # Si quieres filtrar estrictamente por subforo, añade aquí strings que
    # aparezcan en los enlaces de los temas de esa sección.
    # Por ahora publicamos todo el feed (ya tiene 12 entradas recientes de f11).
]

# Archivo donde se guardan los IDs de temas ya publicados
SEEN_FILE = Path(__file__).parent / "seen_topics.json"

# Número máximo de entradas a leer por feed en el primer arranque
MAX_ENTRIES_FIRST_RUN = 10

# Dominios de la interfaz de ForoActivo que NO son imágenes de contenido.
# Cualquier imagen de estos dominios se descarta automáticamente.
UI_IMAGE_DOMAINS = (
    "servimg.com",   # Iconos de la barra de navegación y botones del foro
    "2img.net",      # Placeholders vacíos (empty.gif) y sprites de phpBB
    "foroactivo.com/img",
    "phpbb",
)

# Dominio preferente donde están subidas las imágenes de los posts.
# Se busca primero aquí antes de intentar otros dominios externos.
CLOUDINARY_DOMAIN = "res.cloudinary.com"

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(Path(__file__).parent / "bot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# PERSISTENCIA DE TEMAS VISTOS
# ─────────────────────────────────────────────

def load_seen() -> set:
    """Carga el conjunto de IDs/URLs ya publicadas desde disco."""
    if SEEN_FILE.exists():
        try:
            data = json.loads(SEEN_FILE.read_text(encoding="utf-8"))
            return set(data)
        except (json.JSONDecodeError, ValueError):
            log.warning("seen_topics.json corrupto, se reinicia.")
    return set()


def save_seen(seen: set) -> None:
    """Persiste el conjunto de IDs/URLs al disco."""
    SEEN_FILE.write_text(
        json.dumps(list(seen), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ─────────────────────────────────────────────
# SESIÓN AUTENTICADA EN FOROACTIVO
# ─────────────────────────────────────────────

_session: requests.Session | None = None


def get_session() -> requests.Session:
    """
    Devuelve una sesión HTTP autenticada en ForoActivo.
    El login se realiza una sola vez por ejecución del script y
    la sesión (cookie) se reutiliza para todas las peticiones subsiguientes.
    """
    global _session
    if _session is not None:
        return _session

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
    })

    if not FORO_USERNAME or not FORO_PASSWORD:
        log.warning(
            "No se configuraron FORO_USERNAME / FORO_PASSWORD en .env. "
            "Se intentará acceder sin autenticación (las imágenes pueden no estar disponibles)."
        )
        _session = session
        return _session

    # Paso 1: obtener el token SID / formulario de login
    login_url = f"{FORO_BASE_URL}/login"
    try:
        resp = session.get(login_url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.error("No se pudo acceder a la página de login: %s", exc)
        _session = session
        return _session

    soup = BeautifulSoup(resp.text, "lxml")

    # Extrae el campo oculto 'sid' (token de sesión anti-CSRF de phpBB)
    sid_input = soup.find("input", {"name": "sid"})
    sid = sid_input["value"] if sid_input else ""

    # Paso 2: hacer POST con las credenciales
    post_data = {
        "username":   FORO_USERNAME,
        "password":   FORO_PASSWORD,
        "autologin":  "on",
        "viewonline": "on",
        "redirect":   "./index.php",
        "sid":        sid,
        "login":      "Conectarse",
    }

    try:
        resp2 = session.post(login_url, data=post_data, timeout=15, allow_redirects=True)
        resp2.raise_for_status()
    except requests.RequestException as exc:
        log.error("Error durante el login en ForoActivo: %s", exc)
        _session = session
        return _session

    # Verificar si el login fue exitoso buscando indicadores en la respuesta
    soup2 = BeautifulSoup(resp2.text, "lxml")
    logout_link = soup2.find("a", href=re.compile(r"mode=logout"))
    profile_link = soup2.find("a", href=re.compile(r"mode=viewprofile"))

    if logout_link or profile_link:
        log.info("✅ Login en ForoActivo exitoso como: %s", FORO_USERNAME)
    else:
        # ForoActivo usa cookies con prefijo personalizado:
        # fa_<subdominio>_<dominio>_com_data  (contiene userid serializado)
        # Un userid distinto de '1' en el valor serializado indica sesión activa.
        logged_in = any(
            name.startswith("fa_") and name.endswith("_data") and "userid" in val
            for name, val in session.cookies.items()
        )
        if logged_in:
            log.info("✅ Login en ForoActivo exitoso (verificado por cookie de sesión).")
        else:
            log.warning(
                "⚠️  El login en ForoActivo puede haber fallado. "
                "Verifica FORO_USERNAME y FORO_PASSWORD en el .env."
            )

    _session = session
    return _session


# ─────────────────────────────────────────────
# EXTRACCIÓN DE IMAGEN DEL PRIMER POST
# ─────────────────────────────────────────────

def _is_ui_image(src: str) -> bool:
    """Devuelve True si la URL corresponde a un elemento de interfaz del foro."""
    src_lower = src.lower()
    return any(domain in src_lower for domain in UI_IMAGE_DOMAINS)


def fetch_topic_details(topic_url: str) -> tuple[str | None, str | None]:
    """
    Accede al hilo del foro con sesión autenticada.
    Devuelve una tupla (image_url, forum_id).

    Estrategia de búsqueda (en orden de prioridad):
      1. Imágenes alojadas en Cloudinary (res.cloudinary.com) → son las portadas
         y recursos que el usuario sube directamente al publicar en el foro.
      2. Cualquier imagen externa que no pertenezca a los dominios de UI del foro.
    """
    session = get_session()
    try:
        resp = session.get(topic_url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.warning("No se pudo acceder al hilo %s: %s", topic_url, exc)
        return None, None

    soup = BeautifulSoup(resp.text, "lxml")

    # 1. Detectar forum_id buscando enlaces a subforos en el pathname/navigation
    forum_id = None
    for container in soup.find_all(class_=re.compile(r"pathname|nav|breadcrumb", re.I)):
        for a in container.find_all("a", href=True):
            m = re.search(r"/(f11|f14|f17|f21)-", a["href"])
            if m:
                forum_id = m.group(1)
                break
        if forum_id:
            break

    if not forum_id:
        for a in soup.find_all("a", href=True):
            m = re.search(r"/(f11|f14|f17|f21)-", a["href"])
            if m:
                forum_id = m.group(1)
                break

    # 2. Buscar imagen
    all_imgs = soup.find_all("img")
    candidates: list[str] = []
    for img in all_imgs:
        src = img.get("src") or img.get("data-src") or ""
        if not src:
            continue
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = urljoin(FORO_BASE_URL, src)
        elif not src.startswith("http"):
            src = urljoin(topic_url, src)

        if _is_ui_image(src):
            continue

        candidates.append(src)

    image_url = None
    if candidates:
        for src in candidates:
            if CLOUDINARY_DOMAIN in src.lower():
                log.debug("Imagen Cloudinary encontrada: %s", src)
                image_url = src
                break
        if not image_url:
            log.debug("Imagen externa encontrada: %s", candidates[0])
            image_url = candidates[0]

    return image_url, forum_id


def extract_image_from_rss(html_content: str) -> str | None:
    """
    Fallback: extrae imagen del HTML embebido en el RSS.
    Aplica la misma lógica de prioridad (Cloudinary primero).
    """
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "lxml")
    candidates = []
    for img in soup.find_all("img"):
        src = img.get("src") or ""
        if not src or _is_ui_image(src):
            continue
        candidates.append(src)

    if not candidates:
        return None

    for src in candidates:
        if CLOUDINARY_DOMAIN in src.lower():
            return src
    return candidates[0]


def scrape_forum_page() -> list[dict]:
    """
    Scrapea la página principal del foro para obtener todos los temas recientes,
    no solo los últimos 12 del feed RSS.
    Devuelve una lista de diccionarios con la misma estructura que las entradas del feed.
    """
    session = get_session()
    topics = []

    try:
        resp = session.get(FORO_BASE_URL, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.warning("No se pudo acceder a la página principal del foro: %s", exc)
        return topics

    soup = BeautifulSoup(resp.text, "lxml")

    # Buscar todos los enlaces a temas activos
    seen_links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Filtrar enlaces a temas (empiezan por /t y tienen -activo)
        if "/t" in href and "-activo" in href.lower():
            # Limpiar el enlace (eliminar anclas, parámetros extra)
            clean_href = href.split("#")[0].split("?")[0]
            full_link = urljoin(FORO_BASE_URL, clean_href)
            if full_link not in seen_links:
                seen_links.add(full_link)
                # Obtener el título del atributo 'title' del enlace (tiene el título completo!)
                title = a.get("title", "").strip() or a.get_text(strip=True) or "Sin título"
                # Crear entrada con misma estructura que el feed
                topics.append({
                    "title": title,
                    "link": full_link,
                    "id": full_link,
                    "author": "Desconocido",
                    "published_parsed": None,
                    "updated_parsed": None,
                })

    log.info("Scrape de página principal: encontrados %d temas recientes", len(topics))
    return topics


def fetch_topic_details(topic_url: str) -> tuple[str | None, str | None, str | None, tuple | None]:
    """
    Accede al hilo del foro con sesión autenticada.
    Devuelve una tupla (image_url, forum_id, full_title, published_parsed).
    """
    session = get_session()
    try:
        resp = session.get(topic_url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.warning("No se pudo acceder al hilo %s: %s", topic_url, exc)
        return None, None, None, None

    soup = BeautifulSoup(resp.text, "lxml")

    # 1. Detectar forum_id buscando enlaces a subforos en el pathname/navigation
    forum_id = None
    for container in soup.find_all(class_=re.compile(r"pathname|nav|breadcrumb", re.I)):
        for a in container.find_all("a", href=True):
            m = re.search(r"/(f11|f14|f17|f21)-", a["href"])
            if m:
                forum_id = m.group(1)
                break
        if forum_id:
            break

    if not forum_id:
        for a in soup.find_all("a", href=True):
            m = re.search(r"/(f11|f14|f17|f21)-", a["href"])
            if m:
                forum_id = m.group(1)
                break

    # 2. Buscar imagen
    all_imgs = soup.find_all("img")
    candidates: list[str] = []
    for img in all_imgs:
        src = img.get("src") or img.get("data-src") or ""
        if not src:
            continue
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = urljoin(FORO_BASE_URL, src)
        elif not src.startswith("http"):
            src = urljoin(topic_url, src)

        if _is_ui_image(src):
            continue

        candidates.append(src)

    image_url = None
    if candidates:
        for src in candidates:
            if CLOUDINARY_DOMAIN in src.lower():
                log.debug("Imagen Cloudinary encontrada: %s", src)
                image_url = src
                break
        if not image_url:
            log.debug("Imagen externa encontrada: %s", candidates[0])
            image_url = candidates[0]

    # 3. Obtener título completo de la página del tema (look for <h2 class="topic-title"> or similar)
    full_title = None
    for title_tag in soup.find_all(["h1", "h2", "h3"], class_=re.compile(r"topic-title|maintitle|cattitle", re.I)):
        full_title = title_tag.get_text(strip=True)
        if full_title:
            break

    # 4. Obtener fecha de publicación (look for JSON-LD script tag with datePublished!)
    published_parsed = None
    for script_tag in soup.find_all("script", type="application/ld+json"):
        try:
            import json
            json_data = json.loads(script_tag.string)
            if "datePublished" in json_data:
                # Parse ISO date string like "2026-06-17T12:53:35+02:00"
                from datetime import datetime
                dt = datetime.fromisoformat(json_data["datePublished"])
                # Create a time.struct_time-like tuple (tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst)
                published_parsed = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday(), 0, -1)
                break
        except Exception as e:
            log.debug("Could not parse JSON-LD date: %s", e)
            pass

    return image_url, forum_id, full_title, published_parsed


def process_scraped_topics(topics: list[dict], seen: set, first_run: bool) -> int:
    """
    Procesa los temas obtenidos del scrape de la página principal,
    con la misma lógica que process_feed.
    Retorna el número de temas nuevos publicados.
    """
    new_count = 0
    # Procesamos en orden (más antiguo primero, pero no tenemos fecha, así que ordenamos por ID)
    # Los IDs de temas son números mayores para temas más nuevos (t2516 > t2515)
    sorted_topics = sorted(topics, key=lambda t: int(re.search(r"/t(\d+)-", t["link"]).group(1)) if re.search(r"/t(\d+)-", t["link"]) else 0)

    for entry in sorted_topics:
        uid = entry.get("id") or entry.get("link", "")
        if not uid or uid in seen:
            continue

        if not first_run:
            topic_url = entry.get("link", "")

            # 1. Obtener imagen, forum_id, full_title, published_parsed accediendo al post con sesión autenticada
            image_url, forum_id, full_title, published_parsed = fetch_topic_details(topic_url) if topic_url else (None, None, None, None)

            # Use full_title if available, otherwise keep the scraped title
            if full_title:
                entry["title"] = full_title
            # Use published_parsed if available
            if published_parsed:
                entry["published_parsed"] = published_parsed

            if not forum_id:
                log.warning("No se pudo determinar el subforo para %s", topic_url)
                continue

            thread_id = FORUM_THREAD_MAPPING.get(forum_id)
            if not thread_id:
                log.info("Tema '%s' pertenece al subforo %s (no sincronizado), omitiendo.", entry.get("title"), forum_id)
                seen.add(uid)
                continue

            # No hay HTML del RSS para fallback, así que solo usamos la imagen de la página
            if image_url:
                log.info("🖼️  Imagen encontrada: %s", image_url)
            else:
                log.info("🖼️  Sin imagen para este tema.")

            text = format_message(entry)

            if send_telegram_message(text, image_url, thread_id=thread_id):
                log.info("✅ Publicado en thread %d: %s", thread_id, entry.get("title", uid))
                new_count += 1
            else:
                log.warning("⚠️  No se pudo publicar: %s", entry.get("title", uid))
                continue  # No marcar como visto si falló el envío

        seen.add(uid)

    return new_count


# ─────────────────────────────────────────────
# TELEGRAM
# ─────────────────────────────────────────────

def send_telegram_message(
    text: str,
    image_url: str | None = None,
    thread_id: int | None = None,
) -> bool:
    """
    Envía un mensaje (con o sin imagen) al grupo/canal de Telegram.
    Si thread_id está definido, el mensaje va al topic correspondiente.
    """
    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    if image_url:
        endpoint = f"{base_url}/sendPhoto"
        payload = {
            "chat_id":    TELEGRAM_CHAT_ID,
            "photo":      image_url,
            "caption":    text,
            "parse_mode": "HTML",
        }
    else:
        endpoint = f"{base_url}/sendMessage"
        payload = {
            "chat_id":               TELEGRAM_CHAT_ID,
            "text":                  text,
            "parse_mode":            "HTML",
            "disable_web_page_preview": False,
        }

    if thread_id:
        payload["message_thread_id"] = thread_id

    try:
        resp = requests.post(endpoint, json=payload, timeout=15)
        data = resp.json()
        if data.get("ok"):
            return True
        else:
            log.error("Error de Telegram API: %s", data)
            if image_url:
                log.info("Reintentando sin imagen...")
                return send_telegram_message(text, image_url=None, thread_id=thread_id)
            return False
    except requests.RequestException as exc:
        log.error("Error de red al contactar Telegram: %s", exc)
        return False


def format_message(entry: dict) -> str:
    """Construye el texto del mensaje de Telegram a partir de una entrada RSS."""
    title  = entry.get("title", "Sin título").strip()
    link   = entry.get("link", "").strip()
    author = entry.get("author", "Desconocido").strip()

    published = entry.get("published_parsed") or entry.get("updated_parsed")
    if published:
        dt_utc = datetime(*published[:6], tzinfo=timezone.utc)
        # Convert UTC a zona horaria de Madrid (Europe/Madrid)
        tz_madrid = ZoneInfo("Europe/Madrid")
        dt_madrid = dt_utc.astimezone(tz_madrid)
        fecha = dt_madrid.strftime("%d/%m/%Y a las %H:%M")
    else:
        fecha = "Fecha desconocida"

    lines = [
        "🎌 <b>¡Nuevo tema en el foro!</b>",
        "",
        f"📺 <b>{title}</b>",
        "",
        f"📅 <b>Publicado:</b> {fecha}",
        "",
        f'🔗 <a href="{link}">Ver tema en AnimeZoneEsp</a>',
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────
# LÓGICA PRINCIPAL
# ─────────────────────────────────────────────

def process_feed(feed_name: str, feed_url: str, seen: set, first_run: bool) -> int:
    """
    Lee el feed RSS y publica los temas nuevos en Telegram.
    Retorna el número de temas nuevos publicados.
    """
    log.info("Leyendo feed: %s → %s", feed_name, feed_url)
    feed = feedparser.parse(feed_url)

    if feed.bozo and not feed.entries:
        log.warning("No se pudo parsear el feed '%s': %s", feed_name, feed.bozo_exception)
        return 0

    entries = feed.entries
    if first_run:
        entries = entries[:MAX_ENTRIES_FIRST_RUN]

    new_count = 0
    # Procesamos en orden cronológico (más antiguo primero)
    for entry in reversed(entries):
        uid = entry.get("id") or entry.get("link", "")
        if not uid or uid in seen:
            continue

        if not first_run:
            topic_url = entry.get("link", "")

            # 1. Obtener imagen, forum_id, full_title, published_parsed accediendo al post con sesión autenticada
            image_url, forum_id, full_title, published_parsed = fetch_topic_details(topic_url) if topic_url else (None, None, None, None)

            # Use full_title if available, otherwise keep the feed's title
            if full_title:
                entry["title"] = full_title
            # Use published_parsed if available
            if published_parsed:
                entry["published_parsed"] = published_parsed

            if not forum_id:
                log.warning("No se pudo determinar el subforo para %s", topic_url)
                continue

            thread_id = FORUM_THREAD_MAPPING.get(forum_id)
            if not thread_id:
                log.info("Tema '%s' pertenece al subforo %s (no sincronizado), omitiendo.", entry.get("title"), forum_id)
                seen.add(uid)
                continue

            # 2. Fallback: extraer del HTML del RSS si no se encontró en la página
            if not image_url:
                html_content = (
                    entry.get("content", [{}])[0].get("value", "")
                    or entry.get("summary", "")
                )
                image_url = extract_image_from_rss(html_content)

            if image_url:
                log.info("🖼️  Imagen encontrada: %s", image_url)
            else:
                log.info("🖼️  Sin imagen para este tema.")

            text = format_message(entry)

            if send_telegram_message(text, image_url, thread_id=thread_id):
                log.info("✅ Publicado en thread %d: %s", thread_id, entry.get("title", uid))
                new_count += 1
            else:
                log.warning("⚠️  No se pudo publicar: %s", entry.get("title", uid))
                continue  # No marcar como visto si falló el envío

        seen.add(uid)

    return new_count


def run():
    """Punto de entrada principal."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.critical(
            "Falta TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID. "
            "Crea un archivo .env con esas variables."
        )
        return

    # Inicializar sesión autenticada en ForoActivo al arrancar
    get_session()

    seen = load_seen()
    first_run = len(seen) == 0
    if first_run:
        log.info(
            "⚙️  Primer arranque: marcando entradas existentes como vistas "
            "(no se publicarán para evitar spam)."
        )

    total_new = 0
    # Primero procesamos el feed RSS
    for name, url in RSS_FEEDS.items():
        total_new += process_feed(name, url, seen, first_run)
    # Luego procesamos los temas scrapeados de la página principal
    scraped_topics = scrape_forum_page()
    total_new += process_scraped_topics(scraped_topics, seen, first_run)

    save_seen(seen)

    if first_run:
        log.info(
            "✔️  Primer arranque completado. "
            "Los PRÓXIMOS temas nuevos se publicarán en Telegram."
        )
    else:
        log.info("Ciclo completado. Nuevos temas publicados: %d", total_new)


if __name__ == "__main__":
    run()
