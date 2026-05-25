import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote, urlparse, parse_qs
from utils import HEADERS, logger

PORTALS_MAP = {
    "g1.globo.com": "G1",
    "cnnbrasil.com.br": "CNN Brasil",
    "uol.com.br": "UOL",
    "folha.uol.com.br": "Folha de S.Paulo",
    "estadao.com.br": "Estadão",
}


def _identificar_portal(source_url, source_text):
    source_url = (source_url or "").lower()
    source_text = (source_text or "").lower()
    for dominio, nome in PORTALS_MAP.items():
        if dominio in source_url or dominio in source_text:
            return nome
    for nome in PORTALS_MAP.values():
        if nome.lower() in source_text:
            return nome
    return None


def _buscar_rss_google(tema):
    manchetes = []
    try:
        url = f"https://news.google.com/rss/search?q={tema}&hl=pt-BR&gl=BR"
        logger.info(f"Buscando RSS: {url}")
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            logger.warning(f"RSS: HTTP {resp.status_code}")
            return manchetes

        soup = BeautifulSoup(resp.text, "xml")
        items = soup.select("item")

        for item in items:
            source_tag = item.select_one("source")
            source_url = source_tag.get("url", "") if source_tag else ""
            source_text = source_tag.get_text(strip=True) if source_tag else ""

            portal = _identificar_portal(source_url, source_text)
            if not portal:
                continue

            title_tag = item.select_one("title")
            link_tag = item.select_one("link")
            pubDate_tag = item.select_one("pubDate")

            titulo = title_tag.get_text(strip=True) if title_tag else ""
            if not titulo or len(titulo) < 10:
                continue

            link = link_tag.get_text(strip=True) if link_tag else ""

            data_str = ""
            if pubDate_tag:
                try:
                    pub_parsed = datetime.strptime(
                        pubDate_tag.get_text(strip=True), "%a, %d %b %Y %H:%M:%S %Z"
                    )
                    data_str = pub_parsed.strftime("%d/%m/%Y")
                except Exception:
                    data_str = datetime.now().strftime("%d/%m/%Y")

            manchetes.append({
                "portal": portal,
                "manchete": titulo,
                "link": link,
                "data": data_str if data_str else datetime.now().strftime("%d/%m/%Y"),
                "horario_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

        logger.info(f"RSS: {len(manchetes)} manchetes dos portais alvo")
    except requests.Timeout:
        logger.warning("RSS: timeout na requisicao")
    except requests.ConnectionError:
        logger.warning("RSS: erro de conexao")
    except Exception as e:
        logger.warning(f"RSS: erro inesperado - {e}")

    return manchetes


def _buscar_google_news_html(tema, site, portal_nome):
    manchetes = []
    try:
        url = f"https://www.google.com/search?q={tema}+site:{site}&tbm=nws&hl=pt-BR&num=10"
        logger.info(f"HTML fallback para {portal_nome}")
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return manchetes

        soup = BeautifulSoup(resp.text, "html.parser")
        titles = soup.select("h3")
        links = soup.select("a")

        for i, title_tag in enumerate(titles):
            titulo = title_tag.get_text(strip=True)
            if not titulo or len(titulo) < 10:
                continue

            link = ""
            if i < len(links):
                link = links[i].get("href", "")
                if link.startswith("/url?"):
                    parsed = urlparse(link)
                    qs_params = parse_qs(parsed.query)
                    link = qs_params.get("q", [link])[0]

            manchetes.append({
                "portal": portal_nome,
                "manchete": titulo,
                "link": link if link.startswith("http") else "",
                "data": datetime.now().strftime("%d/%m/%Y"),
                "horario_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
    except Exception as e:
        logger.warning(f"{portal_nome} HTML: {e}")

    return manchetes


def coletar_manchetes(tema):
    if not tema or not tema.strip():
        return []

    tema_encoded = quote(tema.strip())
    todas = _buscar_rss_google(tema_encoded)

    if not todas:
        logger.info("RSS sem resultados. Tentando scraping HTML...")
        for dominio, nome in PORTALS_MAP.items():
            manchetes = _buscar_google_news_html(tema_encoded, dominio, nome)
            todas.extend(manchetes)

    logger.info(f"Total coletado: {len(todas)} manchetes para '{tema}'")
    return todas
