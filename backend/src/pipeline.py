# ============================================================
# MODULO: pipeline.py
# Orquestra todo o processo: extracao -> analise TCT -> agente -> diagnostico.
# E a funcao que o backend chama quando o usuario envia uma prova.
# ============================================================
import pandas as pd

import extracao
import analise_tct
import agente

def classificar_discriminacao_texto(d):
    return analise_tct.classificar_discriminacao(d)

def montar_contexto(ranking, tabela_completa):
    """Monta o texto-contexto (RAG) com os dados reais para o agente ler."""
    linhas = []
    linhas.append("RANKING DE FRAGILIDADES POR TEMA (menor acerto = maior dificuldade):")
    for _, r in ranking.iterrows():
        linhas.append(f"- {r['tema']}: {r['media_acerto']}% de acerto medio ({int(r['num_questoes'])} questoes)")

    linhas.append("")
    linhas.append("DETALHE DAS 5 QUESTOES MAIS DIFICEIS (numeracao da PROVA):")
    mais_dificeis = tabela_completa.dropna(subset=["indice_dificuldade"]).sort_values("indice_dificuldade").head(5)
    for _, l in mais_dificeis.iterrows():
        pct = round(l["indice_dificuldade"] * 100, 1)
        disc = round(l["indice_discriminacao"], 2)
        linhas.append(
            f"- Questao {int(l['questao_prova'])} (tema {l['tema']}): {pct}% acertaram "
            f"(dificuldade {l['classif_dificuldade']}); discriminacao {disc} "
            f"(classificacao: {l['classif_discriminacao']}); distrator alternativa {l['distrator']} com {l['distrator_pct']}%"
        )
    return chr(10).join(linhas)

def analisar_prova(caminho_pdf, caminho_arq1, caminho_arq3, co_grupo=4004,
                   questao_inicial=9, questao_final=35, offset_numeracao=8):
    import time
    t0 = time.time()

    # 1) Extrair e separar questoes do PDF
    texto = extracao.ler_pdf(caminho_pdf)
    questoes = extracao.separar_questoes(texto, questao_inicial, questao_final)
    print(f"[TEMPO] Extracao PDF: {time.time()-t0:.1f}s ({len(questoes)} questoes)")

    # 2) Classificar temas com o agente
    t1 = time.time()
    temas = agente.classificar_todas(questoes)
    temas_df = pd.DataFrame(temas)
    print(f"[TEMPO] Agente classificar temas: {time.time()-t1:.1f}s")

    # 3) Carregar dados e rodar a TCT
    t2 = time.time()
    dados = analise_tct.carregar_dados_curso(caminho_arq1, caminho_arq3, co_grupo)
    tct, num_alunos = analise_tct.analise_completa(dados)
    tct["questao_prova"] = tct["questao_analise"] + offset_numeracao
    print(f"[TEMPO] Carregar dados + TCT: {time.time()-t2:.1f}s")

    # 4) Juntar tema + TCT
    tabela = temas_df.merge(tct, on="questao_prova", how="left")
    tabela_validas = tabela.dropna(subset=["indice_dificuldade"]).copy()
    tabela_validas["pct_acerto"] = (tabela_validas["indice_dificuldade"] * 100).round(1)

    # 5) Ranking por tema
    ranking = tabela_validas.groupby("tema").agg(
        media_acerto=("pct_acerto", "mean"),
        num_questoes=("pct_acerto", "count")
    ).reset_index()
    ranking["media_acerto"] = ranking["media_acerto"].round(1)
    ranking = ranking.sort_values("media_acerto")

    # 6) Diagnostico com o agente (RAG)
    t3 = time.time()
    contexto = montar_contexto(ranking, tabela_validas)
    diagnostico = agente.gerar_diagnostico(contexto)
    print(f"[TEMPO] Agente gerar diagnostico: {time.time()-t3:.1f}s")
    print(f"[TEMPO] TOTAL: {time.time()-t0:.1f}s")

    return {
        "num_alunos": num_alunos,
        "tabela": tabela_validas,
        "ranking": ranking,
        "diagnostico": diagnostico,
    }


# Teste rapido do pipeline completo
if __name__ == "__main__":
    BASE = r"C:\Users\joaop\OneDrive\Área de Trabalho\Projeto Estagio Obrigatorio"
    PASTA_DADOS = BASE + r"\dados\microdados_enade_2021\microdados_Enade_2021_LGPD\2.DADOS"

    resultado = analisar_prova(
        caminho_pdf=BASE + r"\2021_PV_bacharelado_ciencia_computacao.pdf",
        caminho_arq1=PASTA_DADOS + r"\microdados2021_arq1.txt",
        caminho_arq3=PASTA_DADOS + r"\microdados2021_arq3.txt",
        co_grupo=4004,
    )
    print("Alunos:", resultado["num_alunos"])
    print()
    print("RANKING:")
    print(resultado["ranking"].to_string(index=False))
    print()
    print("DIAGNOSTICO (inicio):")
    print(resultado["diagnostico"][:500])
