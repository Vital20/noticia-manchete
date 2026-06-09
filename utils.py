import re
import unicodedata
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

CORES = {
    "positivo": "#00E676",
    "negativo": "#FF5252",
    "neutro": "#FFD740",
    "fundo": "#0A1628",
    "card": "rgba(26, 42, 74, 0.6)",
    "card_solid": "#1A2A4A",
    "texto": "#F0F4FF",
    "texto_muted": "#8899BB",
    "accent": "#00D4FF",
    "accent2": "#0088FF",
    "borda": "rgba(255, 255, 255, 0.06)",
    "navbar": "rgba(10, 22, 40, 0.85)",
    "tema_b": "#FF6D00",
}

STOPWORDS_PT = {
    "a", "agora", "ainda", "alguem", "algum", "alguma", "algumas", "alguns",
    "ante", "antes", "ao", "aos", "apos", "aquela", "aquelas", "aquele",
    "aqueles", "aquilo", "as", "ate", "atraves", "cada", "coisa", "com",
    "como", "contra", "da", "das", "de", "dela", "delas", "dele", "deles",
    "depois", "dessa", "dessas", "desse", "desses", "desta", "destas",
    "deste", "destes", "disso", "disto", "do", "dos", "durante", "e", "ela",
    "elas", "ele", "eles", "em", "enquanto", "entre", "era", "eram", "essa",
    "essas", "esse", "esses", "esta", "estamos", "estas", "estava", "estavam",
    "este", "estes", "estou", "eu", "foi", "foram", "ha", "isso", "isto",
    "ja", "lhe", "lhes", "mais", "mas", "me", "mesmo", "meu", "meus",
    "muito", "muitos", "na", "nao", "nas", "nem", "no", "nos", "nossa",
    "nossas", "nosso", "nossos", "num", "numa", "nunca", "o", "os", "ou",
    "para", "pela", "pelas", "pelo", "pelos", "perante", "pode", "podem",
    "por", "porem", "quando", "quantos", "que", "quem", "sao", "se", "seja",
    "sem", "sempre", "sendo", "ser", "seu", "seus", "si", "sido", "so",
    "sob", "sobre", "sua", "suas", "tambem", "tanto", "te", "tem", "temos",
    "ter", "teu", "teus", "tive", "todo", "todos", "tu", "tua", "tuas",
    "um", "uma", "umas", "uns", "vai", "vao", "voce", "voces", "vos",
    "a", "as", "e", "estao", "esta", "entre", "por", "sem", "como", "no",
    "na", "nos", "nas", "do", "da", "dos", "das", "ao", "aos", "num",
    "numa", "muito", "sao", "qual", "quais", "existe", "existem", "serao",
    "sera", "foram", "era", "toda", "todas", "grande", "grandes", "novo",
    "nova", "novos", "novas", "ter", "tem", "temos", "pelo", "pela", "pelos",
    "pelas", "se", "sua", "suas", "seu", "seus", "diz", "disse", "segundo",
    "sobre", "ainda", "apos", "vez", "anos", "dois", "tres", "fez", "faz",
    "dizem", "cerca", "pode", "parte", "depois", "primeiro", "primeira",
}


def limpar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def extrair_palavras(texto):
    texto_limpo = limpar_texto(texto)
    palavras = texto_limpo.split()
    return [p for p in palavras if p not in STOPWORDS_PT and len(p) > 2]


def formatar_data(data_str):
    if not data_str:
        return datetime.now().strftime("%d/%m/%Y")
    return str(data_str)


def log(mensagem):
    logger.info(mensagem)


def validar_link(link):
    if not link or not isinstance(link, str):
        return False
    return link.startswith("http://") or link.startswith("https://")
