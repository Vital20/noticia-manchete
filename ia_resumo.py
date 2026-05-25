import os
import time
import re
from collections import Counter
from pathlib import Path
from dotenv import load_dotenv
from utils import limpar_texto, STOPWORDS_PT, logger

_dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_dotenv_path)

MODELO_GEMINI = "gemini-2.0-flash"


def _resumo_local(manchetes):
    textos = [m.get("manchete", "") for m in manchetes if m.get("manchete")]
    portais = list(set(m.get("portal", "?") for m in manchetes))

    tema_geral = " ".join(textos)
    palavras = limpar_texto(tema_geral).split()
    palavras_filtradas = [p for p in palavras if p not in STOPWORDS_PT and len(p) > 2]
    freq = Counter(palavras_filtradas)
    palavras_chave = {w for w, _ in freq.most_common(15)}

    toms = Counter(m.get("tom", "Neutro") for m in manchetes)
    tom_predominante = toms.most_common(1)[0][0] if toms else "Neutro"
    total = len(manchetes)
    positivas = toms.get("Positivo", 0)
    negativas = toms.get("Negativo", 0)
    neutras = toms.get("Neutro", 0)

    p1 = (
        f"Foram analisadas {total} manchetes de {len(portais)} portais "
        f"({', '.join(portais)}). "
        f"A cobertura apresentou {positivas} positivas, "
        f"{negativas} negativas e {neutras} neutras, "
        f"com tom predominante **{tom_predominante.lower()}**."
    )

    texto_completo = ". ".join(textos)
    frases = re.split(r'[.!?]+', texto_completo)
    frases = [f.strip() for f in frases if len(f.strip()) > 20]
    pontuadas = []
    for frase in frases:
        fl = limpar_texto(frase)
        tokens = fl.split()
        score = sum(1 for t in tokens if t in palavras_chave)
        score += min(len(tokens) / 10, 3)
        pontuadas.append((frase, score))
    pontuadas.sort(key=lambda x: x[1], reverse=True)
    melhores = [f for f, _ in pontuadas[:5]]

    p2 = " ".join(melhores) if melhores else (
        "As manchetes abordam o tema sob diferentes perspectivas, "
        "refletindo a linha editorial de cada veiculo."
    )

    return f"{p1}\n\n{p2}"


def _resumo_gemini(manchetes):
    chave = os.getenv("GOOGLE_API_KEY")
    if not chave:
        return None

    try:
        import google.generativeai as genai
    except ImportError:
        return None

    manchetes_texto = "\n".join(
        f"- [{m.get('portal', '?')}] {m.get('manchete', '')}"
        for m in manchetes
    )

    prompt = (
        "Voce e um analista de midia especializado em resumir noticias.\n\n"
        "Abaixo estao manchetes de diferentes portais sobre um mesmo tema.\n\n"
        f"{manchetes_texto}\n\n"
        "Com base apenas nessas manchetes, escreva um resumo curto em portugues "
        "com no maximo 2 paragrafos. Destaque o tom geral da cobertura "
        "e as principais diferencas entre os portais, se houver.\n"
        "Use linguagem clara e natural."
    )

    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel(MODELO_GEMINI)
        logger.info("Chamando Gemini API...")
        start = time.time()
        resposta = model.generate_content(prompt)
        elapsed = time.time() - start
        logger.info(f"Gemini respondeu em {elapsed:.1f}s")
        return resposta.text
    except Exception as e:
        logger.warning(f"Gemini API falhou: {e}")
        return None


def gerar_resumo(manchetes):
    if not manchetes:
        return "Nenhuma manchete disponivel para gerar resumo."

    resultado = _resumo_gemini(manchetes)
    if resultado:
        return resultado

    logger.info("Usando resumo local (fallback)")
    return _resumo_local(manchetes)
