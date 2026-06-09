"""Bateria de testes com manchetes reais classificadas manualmente."""
from sentiment import analisar_sentimento_detalhado, analisar_sentimento


MANCHETES_REAIS = [
    # === Positivas ===
    ("Dolar cai apos anuncio do Banco Central", "Positivo"),
    ("Brasil bate recorde na exportacao de carne", "Positivo"),
    ("Desemprego recua para menor nivel em 10 anos", "Positivo"),
    ("Prefeitura anuncia programa de moradia popular", "Positivo"),
    ("Senado aprova reforma tributaria em 1 turno", "Positivo"),
    ("Vacinacao infantil atinge 90 por cento de cobertura", "Positivo"),
    ("Bolsa Familia atende 21 milhoes de familias", "Positivo"),
    ("Brasil conquista ouro inedito no Mundial de Atletismo", "Positivo"),
    ("Producao industrial cresce 3 por cento no trimestre", "Positivo"),
    ("Artista brasileiro vence premio internacional", "Positivo"),
    ("Governo libera 2 bilhoes para saude", "Positivo"),
    ("Brasil e China assinam acordos comerciais", "Positivo"),
    ("Empregos formais crescem pelo 8 mes seguido", "Positivo"),
    ("Escola publica e premiada por projeto inovador", "Positivo"),
    ("Cientistas brasileiros descobrem nova especie na Amazonia", "Positivo"),
    ("Time brasileiro vence campeonato sul americano", "Positivo"),
    ("Numero de assassinatos cai pelo 3 mes consecutivo", "Positivo"),
    ("Programa de inclusao digital beneficia 5 milhoes", "Positivo"),
    ("Brasil e eleito para conselho da ONU", "Positivo"),
    ("Exportacoes do agronegocio batem recorde", "Positivo"),
    ("Estudo mostra melhora na qualidade do ar", "Positivo"),
    ("Pesquisadores desenvolvem vacina contra dengue", "Positivo"),
    ("Pais registra superavit comercial recorde", "Positivo"),
    ("Projeto social tira 10 mil criancas da rua", "Positivo"),
    ("SUS incorpora novo tratamento contra cancer", "Positivo"),
    ("Queda da inflacao alivia orcamento das familias", "Positivo"),
    ("Criminalidade cai pelo quarto mes consecutivo", "Positivo"),

    # === Negativas ===
    ("Inflacao fecha 2026 acima do esperado", "Negativo"),
    ("Incendios florestais devastam regiao amazonica", "Negativo"),
    ("Tempestade deixa milhares sem energia no Sul", "Negativo"),
    ("Greve de professores paralisa escolas em 12 estados", "Negativo"),
    ("Acidente na BR 101 deixa 15 feridos", "Negativo"),
    ("Camara instala CPI para investigar fraudes", "Negativo"),
    ("Casos de dengue aumentam 40 por cento no verao", "Negativo"),
    ("Falta de medicamentos atinge hospitais publicos", "Negativo"),
    ("Acusacoes de corrupcao envolvem ex ministro", "Negativo"),
    ("Nivel dos rios na Amazonia atinge menor marca historica", "Negativo"),
    ("Operacao policial prende suspeitos de trafico", "Negativo"),
    ("Preco da gasolina sobe pela 4 vez no ano", "Negativo"),
    ("Obras da ferrovia sao paralisadas por falta de verba", "Negativo"),
    ("Violencia urbana preocupa moradores", "Negativo"),
    ("Escandalo de corrupcao atinge ministerio", "Negativo"),
    ("Rombo nas contas publicas supera expectativa", "Negativo"),
    ("Desmatamento na Amazonia bate novo recorde", "Negativo"),
    ("Governo sob pressao para explicar gastos", "Negativo"),
    ("Sem previsao para volta as aulas", "Negativo"),
    ("Apagao atinge 15 estados do Nordeste", "Negativo"),
    ("Justica condena envolvidos no desvio de recursos", "Negativo"),
    ("Crise hidrica ameaca abastecimento em Sao Paulo", "Negativo"),
    ("Greve dos bancos completa 20 dias", "Negativo"),
    ("Denuncia de assedio abala secretaria municipal", "Negativo"),
    ("Enchente desaloja familias no interior do Parana", "Negativo"),
    ("Ameaca de greve no metro deixa passageiros apreensivos", "Negativo"),
    ("Fraude em licitacao e investigada pela policia", "Negativo"),
    ("Pandemia causa mortes e contaminacao em massa", "Negativo"),
    ("Tragedia no transito deixa mortos e feridos", "Negativo"),

    # === Neutras ===
    ("Governo anuncia pacote de medidas para economia", "Neutro"),
    ("STF retoma julgamento do marco temporal", "Neutro"),
    ("Reuniao define novas diretrizes para o setor", "Neutro"),
    ("Prefeitura anuncia mudancas no transito", "Neutro"),
    ("Empresa fecha contrato com fornecedor externo", "Neutro"),
    ("Presidente participa de reuniao na ONU", "Neutro"),
    ("Camara dos Deputados retoma trabalhos", "Neutro"),
    ("Novo decreto altera regras para comercio exterior", "Neutro"),
    ("Entenda o que mudou com a reforma", "Neutro"),
    ("Prefeitura anuncia programa de recapeamento", "Neutro"),
    ("Governo publica edital para concessao de aeroportos", "Neutro"),
    ("Secretario participa de evento em Brasilia", "Neutro"),
]

ERROS_TOTAIS = 0
ACERTOS_TOTAIS = 0


def testar():
    global ERROS_TOTAIS, ACERTOS_TOTAIS
    print(f"{'='*70}")
    print(f"  Testes com Manchetes Reais — {len(MANCHETES_REAIS)} casos")
    print(f"{'='*70}\n")

    resultados_por_classe = {"Positivo": {"ok": 0, "total": 0},
                             "Negativo": {"ok": 0, "total": 0},
                             "Neutro": {"ok": 0, "total": 0}}

    for manchete, esperado in MANCHETES_REAIS:
        classificacao, score = analisar_sentimento_detalhado(manchete)
        ok = classificacao == esperado
        resultados_por_classe[esperado]["total"] += 1
        if ok:
            resultados_por_classe[esperado]["ok"] += 1
            ACERTOS_TOTAIS += 1
        else:
            ERROS_TOTAIS += 1
            print(f"  [ERRO] Score {score:+3d} | {classificacao:8s} (esperado {esperado:8s}) | {manchete[:55]}")
            print(f"         Resultado: {classificacao}")

    print(f"\n{'='*70}")
    print(f"  Resumo por classe:")
    for classe in ["Positivo", "Negativo", "Neutro"]:
        r = resultados_por_classe[classe]
        pct = r["ok"] / r["total"] * 100 if r["total"] else 0
        print(f"    {classe:10s}: {r['ok']:2d}/{r['total']:2d} ({pct:5.1f}%)")

    total = len(MANCHETES_REAIS)
    pct = ACERTOS_TOTAIS / total * 100
    print(f"\n  Total: {ACERTOS_TOTAIS}/{total} ({pct:.1f}%)")
    print(f"{'='*70}\n")

    return ERROS_TOTAIS == 0


if __name__ == "__main__":
    import sys
    ok = testar()
    sys.exit(0 if ok else 1)
