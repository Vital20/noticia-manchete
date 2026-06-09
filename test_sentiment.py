from sentiment import analisar_sentimento


def testar(manchete, esperado, descricao=""):
    resultado = analisar_sentimento(manchete)
    ok = resultado == esperado
    status = "OK" if ok else "ERRO"
    if ok:
        print(f"  [{status}] {descricao or manchete[:50]}")
    else:
        print(f"  [{status}] {descricao or manchete[:50]}")
        print(f"    esperado: {esperado}, obtido: {resultado}")
    return ok


def executar_testes():
    testes = [
        # --- Positivas simples ---
        ("Sucesso da empresa no mercado internacional", "Positivo",
         "sucesso -> Positivo"),
        ("Projeto premiado internacionalmente", "Positivo",
         "premiado -> Positivo"),
        ("Pesquisa traz esperanca para pacientes", "Positivo",
         "esperanca -> Positivo"),
        ("Paises celebram acordo de paz historico", "Positivo",
         "acordo de paz -> Positivo"),
        ("Descoberta cientifica revoluciona tratamento", "Positivo",
         "descoberta -> Positivo"),
        ("Empresa bate recorde de vendas no trimestre", "Positivo",
         "recorde de vendas -> Positivo"),
        ("Investimento em educacao cresce 20 este ano", "Positivo",
         "investimento cresce -> Positivo"),
        ("Vacinacao avanca no interior do pais", "Positivo",
         "vacinacao avanca -> Positivo"),
        ("Exportacoes brasileiras batem recorde historico", "Positivo",
         "exportacoes recorde -> Positivo"),
        ("Turismo supera niveis pre-pandemia", "Neutro",
         "turismo supera -> Neutro (so +1)"),

        # --- Negativas simples ---
        ("Tragedia no transito deixa mortos e feridos", "Negativo",
         "tragedia mortos -> Negativo"),
        ("Governo investigado por corrupcao e propina", "Negativo",
         "investigado corrupcao -> Negativo"),
        ("Crise economica aumenta desemprego no pais", "Negativo",
         "crise desemprego -> Negativo"),
        ("Violencia urbana preocupa moradores", "Negativo",
         "violencia preocupa -> Negativo"),
        ("Pandemia causa mortes e contaminacao em massa", "Negativo",
         "pandemia mortes -> Negativo"),
        ("Rombo nas contas publicas supera expectativa", "Negativo",
         "rombo supera -> Negativo (sujeito negativo + verbo positivo)"),
        ("Aumento da violencia preocupa autoridades", "Negativo",
         "aumento da violencia -> Negativo (ascendente + contexto negativo)"),
        ("Inflacao dispara e pressiona consumo das familias", "Negativo",
         "inflacao dispara -> Negativo"),
        ("Escandalo de corrupcao atinge ministerio", "Negativo",
         "escandalo corrupcao -> Negativo"),
        ("Desmatamento na Amazonia bate novo recorde", "Negativo",
         "desmatamento recorde -> Negativo (recorde + contexto negativo)"),

        # --- Neutras ---
        ("Reuniao define novas diretrizes para o setor", "Neutro",
         "reuniao diretrizes -> Neutro"),
        ("Prefeitura anuncia mudancas no transito", "Neutro",
         "mudancas -> Neutro"),
        ("Governo propoe reforma tributaria ao congresso", "Neutro",
         "reforma -> Neutro"),
        ("Empresa fecha contrato com fornecedor externo", "Neutro",
         "contrato -> Neutro"),

        # --- Negacao ---
        ("Governo afirma que nao houve aumento de casos", "Negativo",
         "negacao de aumento -> Negativo"),
        ("Prefeitura diz que nao ha mais recursos", "Neutro",
         "sem palavras no lexico -> Neutro"),
        ("Empresa informa que nao teve lucro no trimestre", "Negativo",
         "nao + lucro -> Negativo"),
        ("Reuniao termina sem acordo entre as partes", "Neutro",
         "sem acordo -> Neutro"),
        ("Pesquisa mostra que nao ha risco de contaminacao", "Positivo",
         "nao + risco -> Positivo"),

        # --- Contexto de inversao (descendente com contexto) ---
        ("Banco Central reduz taxa de juros para 10,75", "Positivo",
         "reducao de juros -> Positivo (inversao)"),
        ("Queda da inflacao alivia orcamento das familias", "Positivo",
         "queda da inflacao -> Positivo (inversao)"),
        ("Corte de impostos estimula economia", "Positivo",
         "corte de impostos -> Positivo (inversao)"),
        ("Governo anuncia reducao no IPI para industria", "Positivo",
         "reducao no IPI -> Positivo (inversao)"),
        ("Criminalidade cai pelo quarto mes consecutivo", "Positivo",
         "criminalidade cai -> Positivo (inversao)"),
        ("Desemprego tem maior queda em dez anos", "Positivo",
         "queda do desemprego -> Positivo (inversao)"),
        ("Violencia tem reducao significativa no estado", "Positivo",
         "reducao da violencia -> Positivo (inversao)"),

        # --- Intensificadores ---
        ("Resultado extremamente positivo para a economia", "Positivo",
         "extremamente + positivo -> Positivo"),
        ("Situacao muito grave preocupa autoridades", "Negativo",
         "muito + grave -> Negativo"),

        # --- Padroes de manchete ---
        ("Ex-ministro e condenado por corrupcao", "Negativo",
         "padrao condenado -> Negativo"),
        ("Empresario e preso em operacao da policia", "Negativo",
         "padrao preso -> Negativo"),
        ("Secretario e investigado por desvio de recursos", "Negativo",
         "padrao investigado -> Negativo"),
        ("Cientista e premiado por descoberta inovadora", "Positivo",
         "padrao premiado -> Positivo"),
        ("Professor e homenageado por contribuicao", "Positivo",
         "padrao homenageado -> Positivo"),

        # --- Ambiguas neutras ---
        ("Reforma trabalhista e criticada por sindicatos", "Negativo",
         "reforma + criticada -> Negativo"),
        ("Mudanca na legislacao ambiental preocupa ONGs", "Negativo",
         "mudanca + preocupa -> Negativo"),
        ("Alteracao no estatuto e bem recebida", "Neutro",
         "alteracao + bem recebida -> Neutro (bem nao esta no lexico)"),

        # --- Verbos de acao negativa ---
        ("Presidente rejeita proposta de acordo", "Negativo",
         "rejeita -> Negativo"),
        ("Justica condena ex-diretor por fraudes", "Negativo",
         "condena -> Negativo junto com fraudes"),
        ("STF proibe novas nomeacoes", "Negativo",
         "proibe -> Negativo"),

        # --- Palavras fortes (peso +/-2) ---
        ("Chacina deixa vitimas em comunidade", "Negativo",
         "chacina -> Negativo (peso 2)"),
        ("Sucesso absoluto na campanha de vacinacao", "Positivo",
         "sucesso -> Positivo (peso 2)"),

        # --- Compostas de negacao ---
        ("Resultado longe de ser o esperado", "Negativo",
         "longe de ser -> Negativo"),
        ("Projeto deixa a desejar na execucao", "Negativo",
         "deixa a desejar -> Negativo"),

        # --- Edge cases ---
        ("", "Neutro", "vazio -> Neutro"),
        (None, "Neutro", "None -> Neutro"),
        ("   ", "Neutro", "espacos -> Neutro"),
        ("Ontem", "Neutro", "palavra unica curta -> Neutro"),

        # --- Casos mistos que devem ser Neutro ---
        ("Inflacao cai mas desemprego aumenta", "Neutro",
         "inflacao cai (+) + desemprego aumenta (-) -> Neutro"),
        ("Governo anuncia medidas e oposicao critica", "Negativo",
         "critica -> Negativo"),

        # --- Variacoes morfologicas (teste de lematizacao/stemming) ---
        ("Pesquisadores descobriram nova vacina promissora", "Positivo",
         "descobriram (variacao de descobrir) -> Positivo"),
        ("Corruptos foram presos pela policia federal", "Negativo",
         "corruptos (variacao de corrupto) + presos -> Negativo"),
        ("Empresas corruptas investigadas em operacao", "Negativo",
         "corruptas (variacao de corrupto) -> Negativo"),
        ("Vitorias consecutivas animam torcida", "Positivo",
         "vitorias (plural de vitoria) -> Positivo"),
    ]

    total = len(testes)
    acertos = 0
    erros = 0

    print(f"\n{'='*60}")
    print(f"  Testando analisar_sentimento()")
    print(f"{'='*60}\n")

    for manchete, esperado, descricao in testes:
        if testar(manchete, esperado, descricao):
            acertos += 1
        else:
            erros += 1

    print(f"\n{'='*60}")
    print(f"  Resultado: {acertos}/{total} acertos ({acertos/total*100:.0f}%)")
    if erros:
        print(f"  ERROS: {erros}")
    print(f"{'='*60}\n")

    return erros == 0


if __name__ == "__main__":
    import sys
    ok = executar_testes()
    sys.exit(0 if ok else 1)
