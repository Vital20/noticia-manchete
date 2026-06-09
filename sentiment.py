import re
import subprocess
import sys
from utils import limpar_texto

# ── CARGA DE MODELOS (com fallback progressivo) ──

_NLP = None
_STEMMER = None
_DISPONIVEL = "puro"


def _carregar_nlp():
    global _NLP, _DISPONIVEL
    try:
        import spacy
        try:
            _NLP = spacy.load("pt_core_news_sm")
            _DISPONIVEL = "spacy"
        except OSError:
            try:
                subprocess.run(
                    [sys.executable, "-m", "spacy", "download", "pt_core_news_sm"],
                    check=True, capture_output=True
                )
                _NLP = spacy.load("pt_core_news_sm")
                _DISPONIVEL = "spacy"
            except Exception:
                pass
    except Exception:
        pass


def _carregar_stemmer():
    global _STEMMER, _DISPONIVEL
    try:
        import nltk
        try:
            from nltk.stem import RSLPStemmer
            _STEMMER = RSLPStemmer()
        except LookupError:
            try:
                nltk.download("rslp")
                from nltk.stem import RSLPStemmer
                _STEMMER = RSLPStemmer()
            except Exception:
                pass
        if _STEMMER and _DISPONIVEL == "puro":
            _DISPONIVEL = "nltk"
    except Exception:
        pass


try:
    _carregar_nlp()
    _carregar_stemmer()
except Exception:
    pass


def _obter_lemas(texto):
    if not _NLP:
        return {}
    doc = _NLP(texto)
    lemas = {}
    for tok in doc:
        palavra = limpar_texto(tok.text)
        lemma = limpar_texto(tok.lemma_)
        if not palavra or len(palavra) <= 1:
            continue
        partes = palavra.split()
        stem = lemma.split()[0] if lemma else palavra
        for p in partes:
            if len(p) > 1:
                lemas[p] = stem if len(stem) > 1 else p
    return lemas


def _obter_stems(tokens):
    if not _STEMMER:
        return {}
    return {t: _STEMMER.stem(t) for t in tokens if len(t) > 1}


def _em_lexico(token, lexico, lemas=None, stems=None):
    if token in lexico:
        return True
    if lemas and token in lemas and lemas[token] in lexico:
        return True
    if stems and token in stems and stems[token] in lexico:
        return True
    return False


def _peso_no_lexico(token, pesos, lemas=None, stems=None):
    if token in pesos:
        return pesos[token]
    if lemas and token in lemas and lemas[token] in pesos:
        return pesos[lemas[token]]
    if stems and token in stems and stems[token] in pesos:
        return pesos[stems[token]]
    return None


def _obter_palavra_base(token, lemas=None, stems=None):
    if lemas and token in lemas:
        return lemas[token]
    if stems and token in stems:
        return stems[token]
    return token


# ── LÉXICO ──

_POSITIVAS = {
    "sucesso", "vitoria", "vitorioso", "vitoriosa", "triunfo",
    "conquista", "conquistas", "conquistou", "conquistar",
    "realizacao", "realizacoes", "realizar", "realizado",
    "atingiu", "atingir", "alcancou", "alcancar", "alcance",
    "concluiu", "concluir", "concluido", "entregue", "entregou",
    "implementado", "implementacao", "implantado", "implantacao",
    "lancado", "lancamento", "inaugurado", "inauguracao",
    "premiado", "premiada", "premiados", "premiadas", "premiacao",
    "homenageado", "homenageada", "homenagem", "homenagens",
    "reconhecido", "reconhecida", "reconhecimento",
    "destaque", "destacou", "destacar", "campeao", "campea",
    "campeoes", "vencedor", "vencedora", "venceu", "vence",
    "superou", "superar", "superado", "supera",
    "expandindo", "expansao", "expansiva",
    "prosperidade", "prospero", "prospera", "florescente",
    "florescendo", "fortaleceu", "fortalecer", "fortalecimento",
    "fortalece", "multiplicou", "multiplicar", "alavancou",
    "superavit", "excedente", "rentavel", "rentabilidade",
    "lucro", "lucros", "lucrativo", "lucrativa", "lucrou",
    "ganho", "ganhos", "bonificacao", "dividendos",
    "melhora", "melhor", "melhorou", "melhorando", "melhorias",
    "melhorar", "avanco", "avancos", "avancou", "avancar", "avanca",
    "progresso", "progressivo", "progressos",
    "evolucao", "evoluiu", "evoluir", "evolui",
    "aprimoramento", "aprimorar", "aprimorou",
    "aperfeicoamento", "aperfeicoar", "aperfeicoou",
    "modernizacao", "modernizar", "modernizou",
    "otimizacao", "otimizar", "otimizou", "incremento",
    "excelente", "excelencia", "otimo", "otima", "otimos", "otimas",
    "maravilhoso", "maravilhosa", "extraordinario", "extraordinaria",
    "formidavel", "admirável", "notavel", "brilhante",
    "fantastico", "fantastica", "espetacular", "magnifico",
    "sensacional", "incrivel", "impressionante",
    "surpreendente", "fenomenal", "excepcional",
    "satisfatorio", "satisfatoria", "satisfez", "satisfacao",
    "digno", "digna", "louvavel", "honroso", "honrosa",
    "eficiente", "eficiencia", "eficaz", "eficazes",
    "produtivo", "produtiva", "produtividade",
    "competente", "competencia", "competencias",
    "confiavel", "confianca", "solido", "solida", "solidas",
    "robusto", "robusta", "qualidade", "qualidades",
    "altissimo", "altissima", "altos",
    "inovacao", "inovacoes", "inovador", "inovadora",
    "pioneiro", "pioneira", "vanguardista", "vanguarda",
    "transformacao", "transformador", "transformadora",
    "revolucionario", "revolucionou",
    "digital", "tecnologia", "tecnologico", "tecnologica",
    "positivo", "positiva", "positivos", "positivas",
    "otimismo", "otimista", "otimistas",
    "esperanca", "esperancoso", "esperancosa",
    "promissor", "promissora", "promissores",
    "alentador", "alentadora", "encorajador", "encorajadora",
    "animador", "animadora", "favoravel", "favoraveis",
    "benefico", "benefica", "beneficios", "beneficio",
    "frutifero", "vantajoso", "vantajosa", "vantagem", "vantagens",
    "oportunidade", "oportunidades", "potencial", "potenciais",
    "ajuda", "ajudar", "ajudou", "apoio", "apoiar", "apoiou",
    "parceria", "parcerias", "cooperacao", "colaboracao",
    "solidariedade", "uniao", "paz", "dialogo", "entendimento",
    "acordo", "acordos", "conciliacao", "harmonia", "harmonioso",
    "harmoniosa", "tratativa", "tratativas", "negociacao",
    "negociacoes", "pacto", "alianca", "coalizao",
    "alegria", "feliz", "felicidade", "orgulho", "orgulhoso",
    "orgulhosa", "gratidao", "gratificado", "gratificante",
    "contentamento", "entusiasmo", "empolgado", "empolgada",
    "animado", "animada", "motivado", "motivada",
    "inspirador", "inspiradora", "inspiracao",
    "seguranca", "seguro", "segura", "estavel", "estaveis",
    "estabilidade", "tranquilidade", "pacifico", "pacifica",
    "protecao", "protegido", "protegida", "garantia", "garantias",
    "garantido", "garantida", "transparencia", "transparente",
    "saude", "saudavel", "bem-estar", "vacinacao", "vacinado",
    "vacinada", "curado", "curada", "cura", "recuperacao",
    "recuperado", "recuperada", "recupera", "recuperou",
    "tratamento", "tratamentos",
    "descoberta", "descobertas", "pesquisa", "pesquisas",
    "cientistas", "desenvolvimento", "desenvolver", "desenvolveu",
    "solucao", "solucoes", "resolver", "resolvido", "resolvida",
    "comemorar", "comemora", "comemorou", "comemoracao",
    "celebrar", "celebra", "celebrou", "festejar", "festeja",
    "inaugurar", "inaugura", "lancar", "lanca", "investir",
    "investe", "investiu", "investimento", "investimentos",
    "contratar", "contrata", "contratou", "contratacao",
    "empregar", "emprega", "empregou",
    "promover", "promove", "promoveu", "promocao",
    "criar", "cria", "criou", "criacao", "gerar", "gera",
    "gerou", "geracao", "acima", "expansivo", "expansiva",
    "anima", "animar", "animou", "investidores",
    "vendas", "natal", "ferias", "turismo",
    "cumprir", "cumpriu", "cumprira", "cumprimento",
    "descobrem", "descobriu", "descobrir", "descoberto",
    "atinge", "atingiu", "atingir", "maxima", "maximo",
    "vitorias", "vitoriosa", "vitoriosas",
    "bateu", "bater", "exportacao", "exportacoes",
    "implementa", "implementou", "expande", "expandiu",
    "retomada", "sobra", "bonanca",
}

_NEGATIVAS = {
    "morte", "mortes", "morto", "mortos", "morta", "morrer",
    "morreu", "morrendo", "matar", "matou", "mata",
    "assassinato", "assassinatos", "assassinar", "assassinado",
    "assassinada", "homicidio", "homicidios", "homicida",
    "latrocinio", "genocidio", "tragedia", "tragedias",
    "tragico", "tragica", "catastrofe", "catastrofico",
    "catastrofica", "desastre", "desastres", "desastroso",
    "desastrosa", "devastador", "devastadora", "devastacao",
    "arrasador", "arrasou", "destruicao", "destruir", "destruiu",
    "destrutivo", "calamidade", "calamitoso",
    "violencia", "violentas", "violento", "violenta",
    "agressao", "agressivo", "agredir", "agredido",
    "atentado", "atentados", "ataque", "ataques", "atacar",
    "atacou", "ameaca", "ameacas", "ameacador", "ameacadora",
    "ameacar", "ameacou", "perigo", "perigos", "perigoso",
    "perigosa", "sequestro", "sequestrado", "sequestrada",
    "terrorismo", "terrorista", "terroristas",
    "bala", "balas", "tiro", "tiros", "tiroteio", "tiroteios",
    "facada", "facadas", "esfaqueado", "esfaqueada",
    "ferido", "feridos", "ferida", "ferimento", "ferimentos",
    "socorro", "crime", "crimes", "criminoso", "criminosos",
    "criminalidade", "criminoso",
    "ilegal", "ilegais", "ilegalidade",
    "fraude", "fraudes", "fraudulento", "fraudulenta",
    "corrupcao", "corrupto", "corruptos", "corrupta",
    "propina", "propinas", "desvio", "desvios", "desviou",
    "lavagem", "sonegação", "sonegacao", "sonegou",
    "superfaturamento", "cartel", "conluio",
    "improbidade", "nepotismo", "caixa-dois",
    "prisao", "prisoes", "prender", "prendeu", "preso", "presos",
    "presa", "capturado", "capturada", "detido", "detida",
    "detencao", "reclusao", "encarceramento", "cadeia",
    "penitenciaria", "condenacao", "condenado", "condenada",
    "condenados", "sentenca", "julgado", "julgada",
    "problema", "problemas", "dificuldade", "dificuldades",
    "dificil", "dificeis", "complicado", "complicada",
    "complicacao", "complexo", "complexa",
    "tenso", "tensa", "tensao", "grave", "graves", "gravidade",
    "critico", "critica", "criticas", "preocupante", "preocupantes",
    "preocupacao", "alarmante", "alarmantes",
    "drastico", "drastica", "drasticamente",
    "crise", "crises", "recessao", "estagnacao",
    "inflacao", "reajuste", "carestia", "escassez",
    "endividamento", "divida", "dividas", "inadimplencia",
    "calote", "default", "falencia", "falir", "faliu",
    "bancarrota", "colapso", "quebrou", "quebra",
    "prejuizo", "prejuizos", "perda", "perdas", "rombo", "rombos",
    "deficit", "deficits", "crise",
    "pior", "piora", "piorou",
    "piorando",
    "suspensao", "suspender", "suspendeu",
    "cancelamento", "cancelar", "cancelou",
    "bloqueio", "bloquear", "bloqueou",
    "paralisacao", "paralisar", "paralisou",
    "parado", "parada", "estagnado", "estagnada",
    "desemprego", "desempregado", "desempregados",
    "miseravel", "miseraveis", "miseria",
    "pobreza", "fome", "desnutricao",
    "doenca", "doencas", "doente", "doentes",
    "epidemia", "pandemias", "pandemia", "virus",
    "contaminacao", "contaminado", "contaminada",
    "guerra", "guerras", "conflito", "conflitos",
    "combate", "batalha", "batalhas", "confronto", "confrontos",
    "embate", "embates", "disputa", "disputas",
    "briga", "brigas", "rixa", "desavença", "desavenças",
    "divergencia", "divergencias", "discordia",
    "hostilidade", "hostil", "hostis",
    "belico", "belica", "tumulto", "tumultos", "confusao",
    "depredacao", "vandalismo", "saque", "saques",
    "investigacao", "investigacoes", "investigar", "investigado",
    "investigada", "suspeito", "suspeita", "suspeitas",
    "denuncia", "denuncias", "denunciar", "denunciado",
    "denunciada", "acusacao", "acusacoes", "acusar", "acusado",
    "acusada", "revelacao", "revelacoes", "revela", "revelou",
    "escandalo", "escandalos", "escandaloso",
    "polêmica", "polemica", "polemico", "controversia",
    "controverso", "controversa", "dubio", "dubia",
    "questionado", "questionada", "questionavel",
    "multa", "multas", "multado", "multada",
    "sanção", "sanções", "sancao", "sancoes", "sancionado",
    "processo", "processos", "processado", "processada",
    "intimacao", "intimado", "intimada",
    "notificacao", "notificado", "notificada",
    "embargo", "embargos", "embargado",
    "interdicao", "interditado", "interditada",
    "confisco", "confiscado",
    "pessimo", "pessima", "pessimos", "pessimas",
    "ruim", "ruins", "terrivel", "terriveis",
    "horrivel", "horroroso", "horror",
    "medo", "medos", "temor", "temer", "receio", "apreensao",
    "negativo", "negativa", "negativos",
    "fracasso", "fracassar", "fracassou",
    "derrota", "derrotas", "derrotado",
    "falhou", "falhar", "falha", "falhas", "fracassou",
    "deficiente", "deficiencia", "deficiencias",
    "insuficiente", "inadequado", "inadequada",
    "incompetente", "incompetencia",
    "ineficaz", "ineficientes", "ineficiente",
    "ineficiencia", "instabilidade", "inseguranca",
    "inseguro", "insegura", "incerteza", "incertezas",
    "vulneravel", "vulnerabilidade",
    "precario", "precaria", "precarios", "precarias",
    "abandono", "abandonado", "abandonada",
    "negligenciar", "negligencia", "negligente",
    "omissao", "omitir", "omisso", "omissa",
    "censura", "censurar", "censurado",
    "autoritario", "autoritaria", "ditadura", "ditatorial",
    "golpe", "golpista", "golpistas",
    "manipulacao", "manipular", "manipulado",
    "desinformacao", "boato", "boatos", "falso", "falsa",
    "falsos", "falsas", "enganoso", "enganosa", "engano",
    "mentira", "mentiras", "mentiroso", "farsa",
    "intolerancia", "preconceito", "discriminacao",
    "racismo", "racista", "racistas",
    "xenofobia", "machismo", "misoginia", "homofobia",
    "exploracao", "explorador", "opressao", "opressor",
    "abusivo", "abusiva", "abuso", "abusos", "abusou",
    "injustica", "injusto", "injusta",
    "arbitrario", "arbitraria", "arbitrariedade",
    "impunidade", "violacao", "violacoes", "violador",
    "imoral", "imoralidade", "antietico", "antietica",
    "danoso", "danosa", "prejudicial", "prejudiciais",
    "nocivo", "nociva", "tóxico", "toxica", "toxicos",
    "caotico", "caotica", "anarquia", "anarquico",
    "conturbado", "turbulento", "convulsionado",
    "especulativo", "especulacao", "predatorio", "predatoria",
    "terror", "arrastao", "arrastoes",
    "desmatamento", "desmatar", "desmatou",
    "vitima", "vitimas",
    "alvo", "prejudica", "prejudicam", "prejudicou", "prejudicar",
    "perdeu", "perder", "perde", "perdendo",
    "admite", "admitiu", "admitir", "admitindo",
    "preocupa", "preocupar", "preocupou", "preocupam",
    "alerta", "alertar", "alertou", "alertas",
    "critica", "criticar", "criticou", "criticam",
    "condena", "condenar", "condenou",
    "repudia", "repudiar", "repudiou",
    "rejeita", "rejeitar", "rejeitou",
    "recusa", "recusar", "recusou",
    "proibe", "proibir", "proibiu", "proibido",
    "impede", "impedir", "impediu", "impedido",
    "obstrui", "obstruir", "obstruiu",
    "boicote", "boicotar", "boicotou",
    "protesta", "protestar", "protestou",
    "manifestacao", "manifestacoes", "manifestantes",
    "greve", "greves", "paralisacao",
    "demissao", "demissoes", "demitido", "demitida",
    "exonerado", "exonerada", "afastado", "afastada",
    "cassado", "cassada",
    "sequestrou", "sequestrar",
    "extorsao", "chacina", "chacinas", "massacre",
    "conspiracao", "golpismo",
    "arruinar", "arruinou", "arruinando",
    "sabotar", "sabotou", "sabotando",
    "extorquir", "extorquiu",
    "dilapidar", "dilapidou",
    "violar", "violou",
    "confessa", "confessou", "recua", "recuou",
    "cede", "cedeu", "falha", "erra", "errou",
    "omite", "omitiu", "esconde", "escondeu",
    "desgoverno", "caos", "retrocesso",
    "sucateamento", "desmonte", "apagao",
    "quebrar", "quebrando",
}

_AMBIGUAS_ASC = {"aumento", "aumenta", "aumentou", "aumentar",
                 "crescimento", "cresceu", "cresce", "crescente",
                 "recorde", "recordes", "alta", "altas",
                 "dispara", "disparou", "disparar", "dispare"}

_AMBIGUAS_DESC = {"queda", "cair", "caiu", "caindo", "cai",
                  "reducao", "reducoes", "reduz", "reduziu", "reduzir",
                  "corte", "cortes", "cortar", "cortou"}

_AMBIGUAS_NEUTRO = {"reforma", "reformas", "mudanca", "mudancas",
                    "mudar", "mudou", "alteracao", "alteracoes",
                    "alterar", "alterou"}

_CONTEXTOS_INVERSAO = {"juros", "taxa", "taxas", "imposto", "impostos",
                       "ipi", "icms", "irpf", "irpj",
                       "inflacao", "desemprego", "criminalidade",
                       "violencia", "morte", "mortes", "homicidio",
                       "homicidios", "assassinato", "assassinatos",
                       "tragedia", "tragedias", "corrupcao", "corruptos",
                       "gastos", "gasto", "burocracia"}

_INTENSIFICADORES = {
    "muito", "mais", "maior", "maiores", "grande", "grandes",
    "extremamente", "altamente", "intensamente",
    "fortemente", "profundamente", "totalmente",
    "completamente", "absolutamente", "drasticamente",
    "significativamente", "consideravelmente",
    "substancialmente", "visivelmente", "claramente",
    "incrivelmente", "surpreendentemente", "absurdamente",
    "grave", "gravemente", "serio", "seriamente",
    "urgente", "urgentemente", "altissimo", "altissima",
}

_ADVERBIOS_POLARIDADE = {
    "infelizmente": -2, "lamentavelmente": -2,
    "felizmente": 2, "surpreendentemente": 1,
    "curiosamente": 1, "estranhamente": -1,
    "paradoxalmente": -1, "inexplicavelmente": -1,
    "naturalmente": 1, "obviamente": 1,
}

_MODAIS = {"pode", "podem", "poderia", "poderiam",
           "deve", "devem", "deveria", "deveriam",
           "precisa", "precisam", "precisaria",
           "parece", "parecem", "parecia"}

_NEGACAO = {
    "nao", "nunca", "jamais", "nem", "ninguem",
    "nenhum", "nenhuma", "nenhuns", "nenhumas",
    "tampouco", "senao",
    "nada",
}

_NEGACAO_FRACA = {
    "sem", "exceto",
}

_NEGACAO_COMPOSTA = re.compile(
    r"(longe\s+de\s+ser|deix[oa]u?\s+a\s+desejar|ao\s+contrario|"
    r"em\s+vez\s+de|falta\s+de|ausencia\s+de|apesar\s+de|"
    r"em\s+meio\s+a|contrario\s+do\s+que)", re.I
)

_PADROES_NEGATIVOS = re.compile(
    r"\b(?:e|foi|sao|foram|era|eram)\s+"
    r"(?:investigado|investigada|condenado|condenada|preso|presa|"
    r"denunciado|denunciada|multado|multada|demitido|demitida|"
    r"processado|processada|intimado|intimada|notificado|notificada|"
    r"embargado|embargada|interditado|interditada|confiscado|confiscada|"
    r"expulso|expulsa|suspenso|suspensa|bloqueado|bloqueada|"
    r"cancelado|cancelada|acusado|acusada|indicado|indicada|"
    r"afastado|afastada|exonerado|exonerada|cassado|cassada|"
    r"extraditado|extraditada|despejado|despejada)\b", re.I
)

_PADROES_POSITIVOS = re.compile(
    r"\b(?:e|foi|sao|foram|era|eram)\s+"
    r"(?:premiado|premiada|homenageado|homenageada|reconhecido|reconhecida|"
    r"condecorado|condecorada|laureado|laureada|agraciado|agraciada|"
    r"contemplado|contemplada|selecionado|selecionada|aprovado|aprovada|"
    r"autorizado|autorizada|liberado|liberada|classificado|classificada|"
    r"habilitado|habilitada|eleito|eleita|nomeado|nomeada|"
    r"empossado|empossada)\b", re.I
)

_PADROES_NEG_FRASE = re.compile(
    r"\b(alerta\s+para|preocupa|critica|teme|receia|repudia|"
    r"condena|rejeita|proibe|impede|boicota|protesta|"
    r"lamenta|lamentou|repudia|combate|combater)\b", re.I
)

_PADROES_POS_FRASE = re.compile(
    r"\b(comemora|celebra|festeja|inaugura|lanca|conquista|"
    r"vence|venceu|aprovou|investe|investiu|contrata|"
    r"contratou|amplia|ampliou|expande)\b", re.I
)

_SUJEITO_VERBO_VERBOS = {"supera", "superou", "superar", "superado",
                         "atinge", "atingiu", "atingir", "bate", "bater",
                         "bateu", "vence", "venceu", "vencer"}

_PALAVRAS_FORTES = {
    "morte": 2, "mortes": 2, "morto": 2, "mortos": 2, "morrer": 2,
    "matar": 2, "assassinato": 2, "assassinado": 2, "assassinada": 2,
    "tragedia": 2, "tragedias": 2, "tragico": 2, "catastrofe": 2, "desastre": 2,
    "devastador": 2, "destruicao": 2, "destruir": 2, "genocidio": 2,
    "terrorismo": 2, "terrorista": 2, "sequestro": 2,
    "corrupcao": 2, "corrupto": 2, "propina": 2,
    "prisao": 2, "condenacao": 2, "condenado": 2, "condenada": 2,
    "fraude": 2, "falencia": 2, "bancarrota": 2,
    "guerra": 2, "massacre": 2, "chacina": 2, "rombo": 2,
    "sucesso": 2, "vitoria": 2, "vitorioso": 2, "triunfo": 2,
    "excelente": 2, "extraordinario": 2, "espetacular": 2,
    "premiado": 2, "premiada": 2, "homenageado": 2, "reconhecido": 2,
    "superou": 2, "conquista": 2, "conquistas": 2,
    "maravilhoso": 2, "fenomenal": 2, "brilhante": 2,
    "campeao": 2, "campea": 2, "vencedor": 2, "vencedora": 2,
    "superavit": 2, "perdeu": 2, "alvo": 2,
    "quebra": 2, "quebrou": 2, "quebrar": 2,
    "arruinar": 2, "arruinou": 2,
    "sabotar": 2, "sabotou": 2,
    "extorquir": 2, "extorquiu": 2,
    "dilapidar": 2, "dilapidou": 2,
    "caos": 2, "desgoverno": 2,
}


# ── FUNÇÕES AUXILIARES ──

def _peso_palavra(palavra):
    return _PALAVRAS_FORTES.get(palavra, 1)


def _peso_palavra_enhanced(token, lemas=None, stems=None):
    p = _peso_no_lexico(token, _PALAVRAS_FORTES, lemas, stems)
    return p if p is not None else 1


def _pontuar_texto(tokens, palavras_set, lemas=None, stems=None, peso_base=1):
    score = 0
    for i, token in enumerate(tokens):
        if _em_lexico(token, palavras_set, lemas, stems):
            peso = _peso_palavra_enhanced(token, lemas, stems)
            if i > 0 and tokens[i - 1] in _INTENSIFICADORES:
                peso = round(peso * 1.5)
            if i < len(tokens) - 1 and tokens[i + 1] in _INTENSIFICADORES:
                peso = round(peso * 1.5)
            score += peso * peso_base
    return score


def _propagar_vies(doc, tokens, lemas, stems):
    """Propaga viés por dependências sintáticas (spaCy).

    Regras:
    1. Verbo positivo + sujeito negativo => -3
    2. Verbo negativo + sujeito => -1 (ou -2 se sujeito tb negativo)
    3. Verbo negativo + objeto direto => -1
    4. Advérbios de polaridade => score direto
    5. Verbos modais reduzem peso de palavras no escopo
    """
    if not doc or _DISPONIVEL != "spacy":
        return 0

    score = 0

    # Regras 1-3: varre verbos e suas dependências
    for sent in doc.sents:
        for tok in sent:
            tok_clean = limpar_texto(tok.lemma_ if tok.lemma_ != "-PRON-" else tok.text)
            if not tok_clean or len(tok_clean) <= 1:
                continue

            # Regra 1: verbo positivo + sujeito negativo
            if _em_lexico(tok_clean, _POSITIVAS, lemas, stems) or \
               _em_lexico(tok_clean, _SUJEITO_VERBO_VERBOS, lemas, stems):
                for child in tok.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subj = limpar_texto(child.text)
                        if subj and _em_lexico(subj, _NEGATIVAS, lemas, stems):
                            score -= 3

            # Regra 2: verbo negativo propaga para sujeito
            if _em_lexico(tok_clean, _NEGATIVAS, lemas, stems):
                for child in tok.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subj = limpar_texto(child.text)
                        if subj:
                            if _em_lexico(subj, _NEGATIVAS, lemas, stems):
                                score -= 2
                            else:
                                score -= 1

                    # Regra 3: verbo negativo propaga para objeto direto
                    if child.dep_ == "obj":
                        obj = limpar_texto(child.text)
                        if obj and len(obj) > 1:
                            score -= 1

    # Regra 4: advérbios de polaridade
    for tok in doc:
        tok_lower = limpar_texto(tok.text.lower())
        if tok_lower in _ADVERBIOS_POLARIDADE:
            score += _ADVERBIOS_POLARIDADE[tok_lower]

    # Regra 5: modais reduzem intensidade (só palavras de peso >= 2)
    for tok in doc:
        tok_clean = limpar_texto(tok.text.lower() if tok.text else "")
        if tok_clean in _MODAIS:
            for child in tok.head.subtree:
                if child.i <= tok.i:
                    continue
                child_clean = limpar_texto(child.lemma_ if child.lemma_ != "-PRON-" else child.text)
                if child_clean:
                    peso = _peso_palavra_enhanced(child_clean, lemas, stems)
                    if peso >= 2:
                        if _em_lexico(child_clean, _NEGATIVAS, lemas, stems):
                            score += 1
                        elif _em_lexico(child_clean, _POSITIVAS, lemas, stems):
                            score -= 1

    return score


def _processar_ambiguas(tokens, lemas=None, stems=None, doc=None):
    score = 0

    if doc:
        score += _propagar_vies(doc, tokens, lemas, stems)

    for i, token in enumerate(tokens):
        if _em_lexico(token, _AMBIGUAS_ASC, lemas, stems):
            peso = _peso_palavra_enhanced(token, lemas, stems)
            vizinhos = tokens[max(0, i - 5):i] + tokens[i + 1:min(len(tokens), i + 6)]
            tem_neg = any(_em_lexico(v, _NEGATIVAS, lemas, stems) for v in vizinhos)
            if tem_neg:
                score -= 2 * peso
            else:
                score += peso

        elif _em_lexico(token, _AMBIGUAS_DESC, lemas, stems):
            vizinhos = tokens[max(0, i - 5):i] + tokens[i + 1:min(len(tokens), i + 6)]
            tem_inversao = any(_em_lexico(v, _CONTEXTOS_INVERSAO, lemas, stems) for v in vizinhos)
            if tem_inversao:
                score += 3
            else:
                score -= 2

        elif _em_lexico(token, _AMBIGUAS_NEUTRO, lemas, stems):
            vizinhos = tokens[max(0, i - 5):i] + tokens[i + 1:min(len(tokens), i + 5)]
            tem_neg = any(_em_lexico(v, _NEGATIVAS, lemas, stems) for v in vizinhos)
            tem_pos = any(_em_lexico(v, _POSITIVAS, lemas, stems) for v in vizinhos)
            if tem_neg and not tem_pos:
                score -= 1
            elif tem_pos and not tem_neg:
                score += 1
    return score


def _processar_negacao(tokens, lemas=None, stems=None, doc=None):
    if doc and _DISPONIVEL == "spacy":
        return _processar_negacao_dependencias(doc, lemas, stems)
    return _processar_negacao_janela(tokens, lemas, stems)


def _processar_negacao_janela(tokens, lemas=None, stems=None):
    score = 0
    for i, token in enumerate(tokens):
        if token in _NEGACAO:
            peso_neg = 3
        elif token in _NEGACAO_FRACA:
            peso_neg = 2
        else:
            continue
        for j in range(i + 1, min(i + 4, len(tokens))):
            t = tokens[j]
            if _em_lexico(t, _POSITIVAS, lemas, stems):
                score -= peso_neg
            elif _em_lexico(t, _NEGATIVAS, lemas, stems):
                score += peso_neg
            elif _em_lexico(t, _AMBIGUAS_ASC, lemas, stems):
                score -= peso_neg
            elif _em_lexico(t, _AMBIGUAS_DESC, lemas, stems):
                score += peso_neg
    return score


def _processar_negacao_dependencias(doc, lemas=None, stems=None):
    score = 0
    for token in doc:
        token_clean = limpar_texto(token.lemma_ if token.lemma_ != "-PRON-" else token.text)
        if not token_clean or len(token_clean) <= 1:
            continue
        if token_clean in _NEGACAO:
            peso_neg = 3
        elif token_clean in _NEGACAO_FRACA:
            peso_neg = 2
        else:
            continue

        head = token.head
        affected = set()
        for child in head.subtree:
            child_clean = limpar_texto(child.text)
            if child_clean and child.i > token.i and len(child_clean) > 1:
                affected.add(child_clean)

        for af in affected:
            if _em_lexico(af, _POSITIVAS, lemas, stems):
                score -= peso_neg
            elif _em_lexico(af, _NEGATIVAS, lemas, stems):
                score += peso_neg
            elif _em_lexico(af, _AMBIGUAS_ASC, lemas, stems):
                score -= peso_neg
            elif _em_lexico(af, _AMBIGUAS_DESC, lemas, stems):
                score += peso_neg
    return score


_FRAMING_NEG = re.compile(
    r"\b(?:"
    r"sem\s+(?:previsao|solucao|fim|controle|limite)|"
    r"apos\s+(?:denuncia|escandalo|polemica|revelacao|acusacao)|"
    r"sob\s+(?:pressao|investigacao|fogo|ataque|suspeita)|"
    r"governo\s+(?:admite|confessa|recua|cede|falha)"
    r")\b", re.I
)

_FRAMING_NEG_SIMPLES = re.compile(
    r"\b(?:rebate|acusa|nega|nego|negou)\b", re.I
)

_FRAMING_FORCA_NEUTRO = re.compile(
    r"\b(?:entenda|explica|como\s+funciona|como\s+se\s+da|veja\s+como)\b", re.I
)

_INTENS_COMPOSTOS = {
    r"\bcada\s+vez\s+mais\b": 1,
    r"\bsem\s+precedentes\b": 2,
    r"\bnunca\s+antes\s+visto\b": 2,
    r"\brecorde\s+historico\b": 1,
    r"\bmais\s+e\s+mais\b": 1,
    r"\bpela\s+primeira\s+vez\b": 0,
}

_INTENS_NEG = re.compile(
    r"\b(cada\s+vez\s+mais|sem\s+precedentes|nunca\s+antes\s+visto)\b", re.I
)

def _processar_padroes(texto, tokens, lemas, stems):
    score = 0
    forca_neutro = False

    if _PADROES_NEGATIVOS.search(texto):
        score -= 2
    if _PADROES_POSITIVOS.search(texto):
        score += 2
    if _PADROES_NEG_FRASE.search(texto):
        score -= 2
    if _PADROES_POS_FRASE.search(texto):
        score += 2

    # Frente 3: padrões de framing jornalístico
    if _FRAMING_NEG.search(texto):
        score -= 2
    if _FRAMING_NEG_SIMPLES.search(texto):
        score -= 1

    # Frente 3: força neutro (manchetes explicativas)
    if _FRAMING_FORCA_NEUTRO.search(texto):
        forca_neutro = True

    # Frente 4: intensificadores compostos
    if _INTENS_NEG.search(texto):
        for token in tokens:
            if _em_lexico(token, _NEGATIVAS, lemas, stems):
                peso = _peso_palavra_enhanced(token, lemas, stems)
                score -= peso
                break

    return score, forca_neutro


def analisar_sentimento(manchete):
    if not manchete or not isinstance(manchete, str):
        return "Neutro"

    texto = manchete.strip()
    texto_limpo = limpar_texto(texto)
    tokens = texto_limpo.split()

    if not tokens:
        return "Neutro"

    lemas = _obter_lemas(texto)
    stems = _obter_stems(tokens) if not lemas else None

    doc = _NLP(texto) if _NLP else None

    score = 0

    score += _pontuar_texto(tokens, _POSITIVAS, lemas, stems, peso_base=1)
    score -= _pontuar_texto(tokens, _NEGATIVAS, lemas, stems, peso_base=1)

    score += _processar_ambiguas(tokens, lemas, stems, doc)

    score += _processar_negacao(tokens, lemas, stems, doc)

    padroes_score, forca_neutro = _processar_padroes(texto, tokens, lemas, stems)
    score += padroes_score

    if forca_neutro:
        return "Neutro"

    if _NEGACAO_COMPOSTA.search(texto):
        score -= 3

    if score >= 2:
        return "Positivo"
    elif score <= -2:
        return "Negativo"
    else:
        return "Neutro"
