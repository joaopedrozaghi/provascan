# ============================================================
# BACKEND: main.py (FastAPI) - com historico de analises
# ============================================================
import os
import shutil
import tempfile
import sys
import json
import re
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import pipeline

app = FastAPI(title="ProvaScan API")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# Pasta onde ficam as analises salvas
PASTA_HISTORICO = os.path.join(os.path.dirname(__file__), "historico")
os.makedirs(PASTA_HISTORICO, exist_ok=True)

def resultado_para_json(resultado):
    return {
        "num_alunos": int(resultado["num_alunos"]),
        "ranking": resultado["ranking"].to_dict(orient="records"),
        "tabela": resultado["tabela"][
            ["questao_prova", "tema", "pct_acerto", "indice_discriminacao",
             "classif_discriminacao", "distrator", "distrator_pct"]
        ].to_dict(orient="records"),
        "diagnostico": resultado["diagnostico"],
    }

def nome_seguro(nome):
    """Transforma o nome digitado num nome de arquivo seguro."""
    seguro = re.sub(r"[^a-zA-Z0-9_-]", "_", nome.strip())
    return seguro or "analise"

@app.get("/")
def raiz():
    return {"status": "ok", "mensagem": "API do ProvaScan esta rodando"}

@app.post("/analisar")
async def analisar(
    prova: UploadFile = File(...),
    arq1: UploadFile = File(...),
    arq3: UploadFile = File(...),
    co_grupo: int = Form(4004),
    nome: str = Form("Analise"),
):
    """Recebe os arquivos, roda o pipeline, SALVA no historico e devolve os resultados."""
    tmp = tempfile.mkdtemp()
    try:
        caminho_prova = os.path.join(tmp, "prova.pdf")
        caminho_arq1 = os.path.join(tmp, "arq1.txt")
        caminho_arq3 = os.path.join(tmp, "arq3.txt")

        for arquivo, caminho in [(prova, caminho_prova), (arq1, caminho_arq1), (arq3, caminho_arq3)]:
            with open(caminho, "wb") as f:
                shutil.copyfileobj(arquivo.file, f)

        resultado = pipeline.analisar_prova(
            caminho_pdf=caminho_prova, caminho_arq1=caminho_arq1,
            caminho_arq3=caminho_arq3, co_grupo=co_grupo,
        )
        dados = resultado_para_json(resultado)
        dados["nome"] = nome
        dados["data"] = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Salvar no historico
        arquivo_hist = os.path.join(PASTA_HISTORICO, nome_seguro(nome) + ".json")
        with open(arquivo_hist, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

        return JSONResponse(content=dados)

    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

@app.get("/historico")
def listar_historico():
    """Lista todas as analises salvas (nome, data, id)."""
    itens = []
    for arquivo in os.listdir(PASTA_HISTORICO):
        if arquivo.endswith(".json"):
            try:
                with open(os.path.join(PASTA_HISTORICO, arquivo), "r", encoding="utf-8") as f:
                    d = json.load(f)
                itens.append({
                    "id": arquivo[:-5],  # nome do arquivo sem .json
                    "nome": d.get("nome", arquivo[:-5]),
                    "data": d.get("data", ""),
                    "num_alunos": d.get("num_alunos", 0),
                })
            except Exception:
                pass
    return itens

@app.get("/historico/{id_analise}")
def carregar_analise(id_analise: str):
    """Carrega uma analise salva especifica (instantaneo)."""
    caminho = os.path.join(PASTA_HISTORICO, nome_seguro(id_analise) + ".json")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return JSONResponse(content=json.load(f))
    return JSONResponse(status_code=404, content={"erro": "Analise nao encontrada"})

@app.delete("/historico/{id_analise}")
def apagar_analise(id_analise: str):
    """Apaga uma analise do historico."""
    caminho = os.path.join(PASTA_HISTORICO, nome_seguro(id_analise) + ".json")
    if os.path.exists(caminho):
        os.remove(caminho)
        return {"status": "apagado"}
    return JSONResponse(status_code=404, content={"erro": "Nao encontrada"})
