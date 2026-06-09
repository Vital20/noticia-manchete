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
    # artigos, pronomes, preposicoes basicas
    "a", "as", "o", "os", "um", "uma", "umas", "uns",
    "ao", "aos", "da", "das", "do", "dos", "na", "nas", "no", "nos", "num", "numa",
    "de", "dela", "delas", "dele", "deles", "dessa", "dessas", "desse", "desses",
    "desta", "destas", "deste", "destes", "disso", "disto",
    "em", "entre", "para", "por", "perante", "sob", "sobre", "com", "sem", "contra",
    "ate", "ate", "ante", "apos", "desde", "mediante", "conforme", "segundo",
    "durante", "exceto", "salvo", "tirante",
    "e", "mas", "ou", "que", "se", "nem", "tambem", "porem", "contudo",
    "todavia", "entretanto", "portanto", "logo", "pois",
    "eu", "tu", "ele", "ela", "nos", "vos", "eles", "elas",
    "me", "te", "lhe", "lhes", "seu", "seus", "sua", "suas",
    "meu", "meus", "minha", "minhas", "teu", "teus", "tua", "tuas",
    "nosso", "nossos", "nossa", "nossas", "vosso", "vossos", "vossa", "vossas",
    "aquele", "aquela", "aqueles", "aquilo", "aquilo",
    "esse", "essa", "esses", "essas", "este", "esta", "estes", "estas",
    "isso", "isto", "aquele", "aquela",
    "alguem", "ninguem", "algo", "nada", "tudo", "cada", "qual", "quais",
    "quem", "cujo", "cuja", "cujos", "cujas", "quanto", "quanta", "quantas",
    "algum", "alguma", "alguns", "algumas", "nenhum", "nenhuma", "nenhuns", "nenhumas",
    "outro", "outra", "outros", "outras", "varios", "variadas", "diversos", "diversas",
    
    # verbos auxiliares / relato
    "sera", "serao", "seria", "seriam", "sendo", "sido",
    "estao", "esta", "estava", "estavam", "estaremos", "estiver",
    "era", "eram", "foi", "foram", "for", "forem",
    "tem", "temos", "ter", "teve", "tiver", "tinha", "tinham",
    "terao", "teria", "teriam",
    "ha", "havia", "houve", "houver",
    "pode", "podem", "podera", "poderiam", "poderia", "podia", "poder",
    "deve", "devem", "deveria", "deveriam",
    "vai", "vao", "vamos", "ira", "irao",
    "fazer", "fez", "faz", "fazem", "fara", "facao",
    "diz", "disse", "dizem", "dizer", "dizia", "diziam",
    "afirma", "afirmam", "afirmou", "afirmar",
    "informa", "informam", "informou", "informar",
    "revela", "revelam", "revelou",
    "aponta", "apontam", "apontou",
    "mostra", "mostram", "mostrou",
    "destaca", "destacam", "destacou",
    "ressalta", "ressaltam",
    "sinaliza", "sinalizam",
    "indica", "indicam", "indicou",
    "avalia", "avaliam", "avaliou",
    "considera", "consideram", "considerou",
    "sugere", "sugerem", "sugeriu",
    "defende", "defendem", "defendeu",
    "declara", "declaram", "declarou",
    "adianta", "adiantou",
    "cita", "citam", "citou",
    "explica", "explicam", "explicou",
    "acrescenta", "acrescentou",
    "classifica", "classificou",
    "garante", "garantem", "garantiu",
    "negocia", "negociam", "negociou",
    "preve", "preveem", "previu",
    "noticia", "noticiam", "noticiou",
    
    # tempo
    "hoje", "ontem", "amanha", "depois", "antes", "agora", "ja", "ainda",
    "sempre", "nunca", "jamais", "asvezes", "raro",
    "ano", "anos", "mes", "meses", "dia", "dias", "hora", "horas",
    "semana", "semanas", "minuto", "minutos", "segundo", "segundos",
    "tarde", "manha", "noite", "madrugada",
    "tempo", "vezes", "vez", "momento",
    
    # numeros e quantidades
    "mil", "milhao", "milhoes", "milhao", "bilhao", "bilhoes",
    "milhares", "centenas", "dezenas", "centena", "dezena",
    "dois", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez",
    "cento", "cem", "duzentos", "trezentos", "quatrocentos", "quinhentos",
    "seiscentos", "setecentos", "oitocentos", "novecentos",
    "primeiro", "primeira", "primeiros", "primeiras",
    "ultimo", "ultima", "ultimos", "ultimas",
    "proximo", "proxima", "proximos", "proximas",
    
    # adjetivos/advérbios genericos
    "mais", "menos", "muito", "muitos", "muita", "muitas", "pouco", "poucos",
    "pouca", "poucas", "tanto", "tanta", "todos", "todas", "todo", "toda",
    "grande", "grandes", "maior", "maiores", "menor", "menores",
    "novo", "nova", "novos", "novas", "velho", "velha", "velhos", "velhas",
    "mesmo", "mesma", "mesmos", "mesmas", "proprio", "propria", "proprios",
    "melhor", "melhores", "pior", "piores",
    "possivel", "possiveis", "impossivel", "impossivel",
    "principal", "principais", "bom", "boa", "ruim",
    "so", "apenas", "somente", "cerca", "quase", "aproximadamente",
    "ex", "vice", "pre", "pos", "anti", "pro",
    
    # palavras genericas de noticia
    "noticia", "noticias", "jornal", "jornalismo",
    "portal", "site", "blog", "coluna", "editorial", "reportagem",
    "materia", "artigo", "entrevista", "galeria", "video", "audio",
    "ultimas", "ultima", "momento", "minuto", "minutoamomento",
    "leia", "veja", "assista", "ouca", "saiba",
    "entenda", "entender",
    "informacao", "informacoes", "conteudo", "programa",
    "edicao", "edicoes", "edicao",
    
    # verbos de acao muito comuns
    "virou", "vira", "torna", "tornou", "tornar",
    "ficou", "fica", "ficar",
    "acontece", "aconteceu", "acontecer",
    "pode", "podem", "poderia", "poderia",
    "deixou", "deixa", "deixar",
    "passou", "passa", "passar",
    "segue", "segue", "seguiu", "seguir",
    "entrou", "entra", "entrar",
    "saiu", "sai", "sair",
    "chegou", "chega", "chegar",
    "acabou", "acaba", "acabar",
    "comecou", "comeca", "comecar",
    
    # portais, sites, veiculos
    "uol", "g1", "globo", "globoocom", "oglobo",
    "cnn", "cnnbrasil", "folha", "folhadespaulo", "folhaonline",
    "estadao", "oestadao", "estadaoonline",
    "r7", "record", "band", "sbt",
    "bbc", "bbcbrasil", "bbcnews",
    "terra", "ig", "igultimo", "abril", "istoedinheiro",
    "veja", "vejaonline", "epoca", "cartacapital", "brasileconomico",
    "correio", "correiobraziliense", "jb", "jblog",
    "em", "emcimadanoticia", "emtemporeal",
    "yahoo", "google", "bing", "msn",
    "metropoles", "metropolesonline",
    "poder360", "poder",
    
    # locais/regioes comuns
    "brasil", "brasileiro", "brasileira", "brasileiros", "brasileiras",
    "sao", "paulo", "riodejaneiro", "rio", "janeiro",
    "belo", "horizonte", "curitiba", "salvador", "fortaleza",
    "brasilia", "distritofederal", "portoalegre",
    "nacional", "federal", "estadual", "municipal",
    "capital", "interior", "regiao",
    
    # misc
    "segundo", "terceiro", "quarto", "quinto",
    "cada", "coisa", "coisas", "gente", "pessoas", "pessoa",
    "casa", "casas", "vez", "vezes", "parte", "partes", "lado", "lados",
    "fim", "final", "inicio", "comeco", "meio",
    "tipo", "tipos", "forma", "formas", "modo", "maneira",
    "fato", "fatos", "dado", "dados", "caso", "casos",
    "numero", "numeros", "valor", "valores", "total",
    "maioria", "minoria", "media",
    "exemplo", "exemplos", "base", "bases",
    
    # verbos neutros frequentes em manchetes
    "anuncia", "anunciou", "anunciar", "anunciado",
    "avanca", "avancou", "avancar",
    "supera", "superou", "superar", "superado",
    "bate", "bateu", "bater",
    "cresce", "cresceu", "crescer", "crescimento",
    "aumenta", "aumentou", "aumentar", "aumento",
    "cai", "caiu", "cair", "caindo",
    "reduz", "reduziu", "reduzir", "reducao",
    "sobe", "subiu", "subir",
    "dispara", "disparou", "disparar",
    "recorde", "recordes",
    "atinge", "atingiu", "atingir",
    "preve", "previu", "prever",
    "registra", "registrou", "registrar",
    "manteve", "mantem", "manter",
    "lanca", "lancou", "lancar",
    "implementa", "implementou", "implementar",
    "expande", "expandiu", "expandir",
    "retoma", "retomou", "retomar", "retomada",
    "libera", "liberou", "liberar",
    "aprova", "aprovou", "aprovar",
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
