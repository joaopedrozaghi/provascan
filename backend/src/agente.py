# ============================================================
# MODULO: agente.py
# Usa o Ollama (local) para classificar temas e gerar o diagnostico.
# ============================================================
import ollama
import os
import hashlib
import json

MODELO = "llama3.1:8b"

TEMAS_PADRAO = [
    "Algoritmos e Estrutura de Dados", "Programacao", "Banco de Dados",
    "Redes de Computadores", "Sistemas Operacionais", "Sistemas Distribuidos",
    "Engenharia de Software", "Arquitetura de Computadores", "Teoria da Computacao",
    "Logica e Matematica", "Inteligencia Artificial", "Seguranca da Informacao",
    "Interacao Humano-Computador", "Computacao Grafica", "Compiladores"
]

def normalizar_tema(tema_bruto, temas=None):
    """Garante que o tema retornado seja um da lista oficial."""
    if temas is None:
        temas = TEMAS_PADRAO
    if not tema_bruto or tema_bruto.strip() == "":
        return "Nao classificado"
    tb = tema_bruto.strip().lower()
    if "nao_identificado" in tb or "identificado" in tb:
        return "Nao classificado"
    for t in temas:
        if t.lower() in tb or tb in t.lower():
            return t
    # tenta por palavra-chave parcial
    for t in temas:
        palavras = t.lower().split()
        if any(p in tb for p in palavras if len(p) > 4):
            return t
    return "Nao classificado"

def classificar_tema(texto_questao, temas=None):
    """Classifica o tema de UMA questao. Retorna (tema, confianca)."""
    if temas is None:
        temas = TEMAS_PADRAO
    lista = ", ".join(temas)
    prompt = (
        "Voce e um especialista em Ciencia da Computacao analisando questoes de prova. "
        "Leia a questao e identifique o TEMA principal. "
        f"Escolha APENAS UM tema EXATAMENTE como escrito na lista: {lista}. "
        "Responda EXATAMENTE no formato: "
        "TEMA: <um tema da lista> | CONFIANCA: <alta, media ou baixa>. "
        "QUESTAO: " + texto_questao
    )
    resp = ollama.chat(model=MODELO, messages=[{"role": "user", "content": prompt}])
    conteudo = resp["message"]["content"]

    tema = "NAO_IDENTIFICADO"
    confianca = "baixa"
    for parte in conteudo.replace(chr(10), " ").split("|"):
        if "TEMA:" in parte.upper():
            tema = parte.split(":", 1)[1].strip()
        if "CONFIANCA" in parte.upper():
            confianca = parte.split(":", 1)[1].strip().lower()

    tema = normalizar_tema(tema, temas)
    return tema, confianca

def classificar_todas(questoes_texto, temas=None, usar_cache=True):
    """
    Classifica todas as questoes. Usa cache: se ja classificou esta mesma prova antes,
    le do arquivo em vez de chamar a IA de novo.
    """
    # Criar uma "assinatura" unica desta prova (baseada no texto das questoes)
    assinatura = hashlib.md5(str(sorted(questoes_texto.items())).encode()).hexdigest()
    pasta_cache = os.path.join(os.path.dirname(__file__), "cache")
    os.makedirs(pasta_cache, exist_ok=True)
    caminho_cache = os.path.join(pasta_cache, f"temas_{assinatura}.json")

    # Se ja existe no cache, le de la
    if usar_cache and os.path.exists(caminho_cache):
        with open(caminho_cache, "r", encoding="utf-8") as f:
            print("[CACHE] Temas carregados do cache (sem chamar a IA)")
            return json.load(f)

    # Senao, classifica com a IA
    resultados = []
    for numero in sorted(questoes_texto.keys()):
        tema, conf = classificar_tema(questoes_texto[numero], temas)
        resultados.append({"questao_prova": numero, "tema": tema, "confianca": conf})

    # Salva no cache para a proxima vez
    if usar_cache:
        with open(caminho_cache, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print("[CACHE] Temas salvos no cache")

    return resultados

def gerar_diagnostico(contexto):
    """Recebe um texto-contexto com os dados reais e gera o relatorio pedagogico."""
    prompt = (
        "Voce e um especialista em avaliacao educacional analisando o desempenho de "
        "estudantes de Ciencia da Computacao no ENADE. "
        "Com base EXCLUSIVAMENTE nos dados abaixo, escreva um diagnostico pedagogico. "
        "REGRAS: use a numeracao da PROVA ao citar questoes; use EXATAMENTE a classificacao "
        "de discriminacao fornecida (fraca, razoavel, boa, otima), sem inventar adjetivos; "
        "discriminacao fraca significa que ate os bons alunos erraram; nao invente numeros. "
        "DADOS: " + contexto + " "
        "Escreva 3 secoes: 1) DIAGNOSTICO GERAL; 2) PRINCIPAIS FRAGILIDADES (3 temas, com os "
        "numeros reais e a classificacao de discriminacao); 3) RECOMENDACOES praticas por tema. "
        "Escreva em portugues, profissional e objetivo."
    )
    resp = ollama.chat(model=MODELO, messages=[{"role": "user", "content": prompt}])
    return resp["message"]["content"]

# Teste rapido
if __name__ == "__main__":
    questao_teste = ("QUESTAO 35: Um sistema distribuido e aquele no qual os componentes "
                     "de hardware ou software, localizados em computadores interligados em rede, "
                     "comunicam-se e coordenam suas acoes enviando mensagens entre si.")
    tema, conf = classificar_tema(questao_teste)
    print(f"Tema: {tema} | Confianca: {conf}")
