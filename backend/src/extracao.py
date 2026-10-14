# ============================================================
# MODULO: extracao.py
# Responsavel por ler o PDF da prova e separar as questoes
# ============================================================
import re
from pypdf import PdfReader

def ler_pdf(caminho_pdf):
    """Le um PDF e retorna todo o texto concatenado."""
    leitor = PdfReader(caminho_pdf)
    partes = []
    for pagina in leitor.pages:
        conteudo = pagina.extract_text()
        if conteudo:
            partes.append(conteudo)
    return chr(10).join(partes)

def separar_questoes(texto_completo, questao_inicial=9, questao_final=35, limite_posicao=80000):
    """
    Separa as questoes do componente especifico.
    Retorna um dicionario {numero_questao: texto_da_questao}.

    - questao_inicial / questao_final: faixa das questoes especificas (padrao ENADE CC: 9 a 35)
    - limite_posicao: ignora ocorrencias de 'QUESTAO' depois dessa posicao (evita gabarito no fim)
    """
    padrao = re.compile(r"QUEST[AO~]+O?\s*(\d{1,2})", re.IGNORECASE)
    # fallback mais simples se o de cima nao pegar
    padrao = re.compile(r"QUEST[\wÃÂÁÀ]*O\s+(\d{1,2})", re.IGNORECASE)

    todas = [(int(m.group(1)), m.start()) for m in padrao.finditer(texto_completo)]

    posicoes = {}
    for numero, pos in todas:
        if questao_inicial <= numero <= questao_final and pos < limite_posicao:
            if numero not in posicoes:
                posicoes[numero] = pos

    numeros = sorted(posicoes.keys())
    questoes = {}
    for i, numero in enumerate(numeros):
        inicio = posicoes[numero]
        if i + 1 < len(numeros):
            fim = posicoes[numeros[i + 1]]
        else:
            fim = inicio + 2500
        questoes[numero] = texto_completo[inicio:fim].strip()

    return questoes

# Teste rapido (so roda se executar este arquivo diretamente)
if __name__ == "__main__":
    caminho = r"C:\Users\joaop\OneDrive\Área de Trabalho\Projeto Estagio Obrigatorio\2021_PV_bacharelado_ciencia_computacao.pdf"
    texto = ler_pdf(caminho)
    print("Caracteres extraidos:", len(texto))
    questoes = separar_questoes(texto)
    print("Questoes encontradas:", sorted(questoes.keys()))
    print("Total:", len(questoes))
