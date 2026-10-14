# ============================================================
# MODULO: analise_tct.py
# Calcula os indicadores da Teoria Classica dos Testes:
# dificuldade, discriminacao e distratores.
# ============================================================
import pandas as pd
import numpy as np

def carregar_dados_curso(caminho_arq1, caminho_arq3, co_grupo):
    """
    Carrega os microdados e filtra os alunos de um curso (CO_GRUPO).
    Retorna um DataFrame com os alunos validos (TP_PRES=555) daquele curso.
    """
    arq1 = pd.read_csv(caminho_arq1, sep=";", encoding="latin-1", decimal=".")
    arq3 = pd.read_csv(caminho_arq3, sep=";", encoding="latin-1", decimal=".")

    # Cursos do CO_GRUPO desejado
    codigos = arq1[arq1["CO_GRUPO"] == co_grupo]["CO_CURSO"].unique()

    # Alunos desses cursos
    dados = arq3[arq3["CO_CURSO"].isin(codigos)]

    # So validos (presente com resultado valido) e com vetor de escolha preenchido
    dados = dados[dados["TP_PRES"] == 555]
    dados = dados[dados["DS_VT_ESC_OCE"].notna()].copy()
    return dados

def montar_tabela_acertos(dados):
    """
    A partir das escolhas dos alunos e do gabarito, monta a tabela de acertos
    (1=acertou, 0=errou, NaN=questao anulada).
    Retorna: (acertos, escolhas, gabarito)
    """
    gabarito = str(dados["DS_VT_GAB_OCE_FIN"].iloc[0])
    n_questoes = len(gabarito)

    escolha_texto = dados["DS_VT_ESC_OCE"].astype(str)
    escolhas = escolha_texto.apply(lambda x: pd.Series(list(x)))
    escolhas.columns = [f"Q{i}" for i in range(1, n_questoes + 1)]

    acertos = pd.DataFrame(index=escolhas.index)
    for i in range(1, n_questoes + 1):
        letra_certa = gabarito[i - 1]
        col = f"Q{i}"
        if letra_certa in ("X", "Z"):
            acertos[col] = np.nan
        else:
            acertos[col] = (escolhas[col] == letra_certa).astype(int)

    return acertos, escolhas, gabarito

def indice_dificuldade(acertos):
    """Retorna a Series com o indice de dificuldade (% acerto) de cada questao."""
    return acertos.mean()

def indice_discriminacao(acertos, proporcao=0.27):
    """
    Calcula o indice de discriminacao (metodo Kelley) de cada questao.
    Compara os 27% melhores com os 27% piores.
    """
    nota_total = acertos.sum(axis=1)
    n = len(nota_total)
    tam = int(n * proporcao)
    ordem = nota_total.sort_values(ascending=False)
    melhores = ordem.head(tam).index
    piores = ordem.tail(tam).index

    disc = {}
    for q in acertos.columns:
        am = acertos.loc[melhores, q].mean()
        ap = acertos.loc[piores, q].mean()
        disc[q] = np.nan if np.isnan(am) else (am - ap)
    return pd.Series(disc)

def analisar_distratores(escolhas, gabarito):
    """
    Para cada questao, encontra o distrator mais marcado (alternativa errada mais popular).
    Retorna um dicionario {num_questao: (letra_distrator, pct)}.
    """
    info = {}
    for q in range(1, len(gabarito) + 1):
        col = f"Q{q}"
        letra_certa = gabarito[q - 1]
        if letra_certa in ("X", "Z"):
            info[q] = (None, None)
            continue
        contagem = escolhas[col].value_counts(normalize=True)
        erradas = contagem.drop([letra_certa, "*", "."], errors="ignore")
        if len(erradas) > 0:
            info[q] = (erradas.idxmax(), round(erradas.max() * 100, 1))
        else:
            info[q] = (None, None)
    return info

def classificar_dificuldade(p):
    if pd.isna(p): return "anulada"
    if p < 0.30: return "muito dificil"
    if p < 0.50: return "dificil"
    if p < 0.70: return "media"
    return "facil"

def classificar_discriminacao(d):
    if pd.isna(d): return "anulada"
    if d >= 0.40: return "otima"
    if d >= 0.30: return "boa"
    if d >= 0.20: return "razoavel"
    return "fraca"

def analise_completa(dados):
    """
    Roda toda a analise TCT e retorna um DataFrame com todos os indicadores por questao.
    """
    acertos, escolhas, gabarito = montar_tabela_acertos(dados)
    dif = indice_dificuldade(acertos)
    disc = indice_discriminacao(acertos)
    distr = analisar_distratores(escolhas, gabarito)

    linhas = []
    for i in range(1, len(gabarito) + 1):
        col = f"Q{i}"
        linhas.append({
            "questao_analise": i,
            "indice_dificuldade": dif[col],
            "indice_discriminacao": disc[col],
            "classif_dificuldade": classificar_dificuldade(dif[col]),
            "classif_discriminacao": classificar_discriminacao(disc[col]),
            "distrator": distr[i][0],
            "distrator_pct": distr[i][1],
        })
    tabela = pd.DataFrame(linhas)
    return tabela, len(dados)

# Teste rapido
if __name__ == "__main__":
    PASTA = r"C:\Users\joaop\OneDrive\Área de Trabalho\Projeto Estagio Obrigatorio\dados\microdados_enade_2021\microdados_Enade_2021_LGPD\2.DADOS"
    arq1 = PASTA + r"\microdados2021_arq1.txt"
    arq3 = PASTA + r"\microdados2021_arq3.txt"

    dados = carregar_dados_curso(arq1, arq3, co_grupo=4004)
    tabela, n = analise_completa(dados)
    print("Alunos analisados:", n)
    print(tabela.to_string(index=False))
