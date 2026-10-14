# Projeto de Estágio - Anotações e Decisões

> Documento de acompanhamento. Serve para não se perder entre as sessões.
> Aluno: João Pedro Zaghi Congio Tereza | Orientador: Diego Roberto Gonçalves de Pontes
> Tema: Identificação e Análise de Fragilidades no Desempenho de Estudantes (Ciência de Dados)

---

## 0. VISÃO FINAL DO PROJETO (o objetivo real)

Construir uma **APLICAÇÃO reutilizável** ("Analisador de Provas") onde:
1. O usuário envia uma prova qualquer no padrão ENADE/ADA (PDF) + as respostas dos alunos.
2. O agente de IA processa TUDO automaticamente: lê as questões, classifica os temas,
   corrige e cruza com o desempenho dos alunos.
3. A aplicação mostra na tela: indicadores (TCT), fragilidades por tema e recomendações.

NÃO é só um script para o ENADE 2021 — é uma ferramenta genérica que serve para outras provas.
O trabalho com o ENADE 2021 é o primeiro caso de uso / validação da ferramenta.

### Operação automática + confiável (decisão)
A aplicação roda de forma AUTÔNOMA (sem revisão manual obrigatória), como pede a proposta.
PORÉM, o agente registra um NÍVEL DE CONFIANÇA por classificação, gravado em log, para
auditoria e para citar no relatório como controle de qualidade. Assim é automático E rigoroso.

### Ponto em aberto importante (CONFIRMAR COM O DIEGO)
Para analisar qualquer prova, a aplicação precisa das RESPOSTAS DOS ALUNOS + gabarito.
- No ENADE isso vem dos microdados.
- Na ADA / outras provas: de onde virão esses dados? Em qual formato?
A aplicação será desenhada para receber: (a) PDF da prova + (b) planilha de respostas em
um FORMATO PADRÃO. Qualquer prova convertida para esse formato funcionará.

---

## 1. As 3 camadas conceituais

1. **Dados tratados** (base limpa) — a fundação.
2. **Análise estatística** (Teoria Clássica dos Testes) — o coração, é o mais cobrado.
3. **Aplicação com agente de IA** (LLM + RAG) — lê os resultados e gera relatórios/ações.

O agente NÃO faz o projeto sozinho: ele é o "cérebro" que lê texto e responde. O fluxo em
volta (extração, organização, análise, tela) é o código que vamos escrever.

---

## 2. Decisões já tomadas

| Item | Decisão |
|---|---|
| Base de dados (1º caso) | **ENADE 2021** (microdados do INEP) |
| Curso | **Ciência da Computação – Bacharelado** |
| Código do curso (CO_GRUPO) | **4004** |
| Linguagem | **Python** |
| Ambiente de código | **Jupyter Notebook (análise) + scripts .py (aplicação)** |
| LLM do agente | **Ollama (local, gratuito)** — modelo `llama3.1:8b` |
| Extração do PDF | **Automática com Python** (extrai o TEXTO dos enunciados) |
| Classificação de temas | Feita pelo LLM, **automática**, com log de confiança |
| Interface da aplicação | **Streamlit** (provável — simples, em Python) |

---

## 3. Estrutura de pastas (no PC do João)

Atual:
```
Projeto Estagio Obrigatorio/
├── dados/microdados_enade_2021/microdados_Enade_2021_LGPD/
│   ├── 1.LEIA-ME/   (dicionário, manual, questionários)
│   └── 2.DADOS/     (48 arquivos .txt dos microdados)
├── docs/        (prova, gabarito, dicionário, ESTE arquivo)
├── notebooks/   (01_explorar_dados.ipynb)
└── resultados/  (gráficos e tabelas)
```

Estrutura futura (quando a aplicação crescer) — será montada depois:
```
├── app/            (a aplicação / interface Streamlit)
├── src/            (módulos reutilizáveis)
│   ├── extracao.py     (ler PDF e separar questões)
│   ├── agente.py       (Ollama: classificar temas + confiança)
│   ├── analise_tct.py  (dificuldade, discriminação, distratores)
│   └── relatorio.py    (RAG + geração do diagnóstico)
```

Caminho dos dados:
`C:\Users\joaop\OneDrive\Área de Trabalho\Projeto Estagio Obrigatorio\dados\microdados_enade_2021\microdados_Enade_2021_LGPD\2.DADOS`

---

## 4. Entendimento dos dados (IMPORTANTE)

### Arquivos
- **arq1** → `CO_GRUPO` (identifica curso) e `CO_CURSO`.
- **arq3** → vetores de prova (respostas, gabarito, acertos) e `TP_PRES`.
- Junção por `CO_CURSO`. (LGPD: não dá para cruzar no nível de aluno individual.)

### Colunas-chave (vetores) no arq3
- `DS_VT_GAB_OCE_FIN` → gabarito do Componente Específico (27 questões)
- `DS_VT_ESC_OCE` → resposta marcada pelo aluno (27) — ÍNTEGRO, usar como base
- `DS_VT_ACE_OCE` → acertos pré-calculados — COM DEFEITO (perde zeros à esquerda), NÃO usar

### Universo analisado
- 12.733 registros de CC → 9.993 com TP_PRES=555 → **9.987** válidos (sem vetor vazio).
- Prova: 35 questões = 1-8 Formação Geral + 9-35 Componente Específico (27 objetivas).

### Conversão de numeração (DECIFRADO)
> **Questão na prova = Q(da análise) + 8**
- Q1 análise = Questão 9 | Q18 análise = Questão 26 | Q27 análise = Questão 35

### Questões anuladas (NaN, fora da TCT)
Análise: **Q4, Q5, Q9, Q13, Q17, Q21, Q24, Q25** (8 anuladas) → sobram **19 válidas**.
Algumas anuladas por critério estatístico (ponto-bisserial < 0,20) → achado p/ relatório.

---

## 5. Resultados já obtidos

### Índice de Dificuldade (TCT)
Nenhuma questão foi "fácil" (nenhuma acima de 70% de acerto). Prova difícil.

As 5 MAIORES FRAGILIDADES (questões mais difíceis) e temas:

| Prova | Análise | % acerto | Tema / Objeto de conhecimento |
|---|---|---|---|
| Q26 | Q18 | 15,3% | Interação Humano-Computador (interfaces adaptativas) |
| Q34 | Q26 | 22,8% | Algoritmos em Grafos (algoritmo de Dijkstra) |
| Q31 | Q23 | 23,1% | Teoria da Computação (Máquina de Turing / autômatos) |
| Q14 | Q6  | 25,0% | Arquitetura de Computadores (Von Neumann) |
| Q24 | Q16 | 28,4% | Segurança / Criptografia (ponta a ponta, AES, SHA) |

Gráfico salvo em: `resultados/dificuldade_questoes.png`

---

## 5b. RESULTADO CENTRAL — Ranking de Fragilidades por Tema (agente + TCT)

O agente Ollama (llama3.1:8b) classificou automaticamente as 27 questões (todas confiança
alta). Cruzando TEMA (agente) x DIFICULDADE (TCT, ~10 mil alunos), agrupado por tema:

| Posição | Tema | Média acerto | Nº questões |
|---|---|---|---|
| 1 (maior fragilidade) | Teoria da Computação | 23,1% | 1 |
| 2 | Interação Humano-Computador | 26,7% | 2 |
| 3 | Segurança da Informação | 28,4% | 1 |
| 4 | Arquitetura de Computadores | 29,4% | 2 |
| 5 | Algoritmos e Estrutura de Dados | 35,7% | 4 (mais confiável) |
| 6 | Sistemas Operacionais | 40,7% | 1 |
| 7 | Compiladores | 45,4% | 1 |
| 8 | Engenharia de Software | 51,0% | 1 |
| 9 | Sistemas Distribuídos | 51,4% | 1 |
| 10 | Banco de Dados | 52,2% | 2 |
| 11 | Inteligência Artificial | 53,4% | 2 |
| 12 (menor fragilidade) | Lógica e Matemática | 62,7% | 1 |

Arquivos gerados em `resultados/`:
- `dificuldade.csv` (índice de dificuldade por questão)
- `ranking_fragilidades.csv` (ranking por tema)
- `dificuldade_questoes.png` (gráfico de dificuldade por questão)
- `ranking_fragilidades.png` (gráfico do ranking por tema)

Pipeline do agente (notebook `02_agente_ia.ipynb`): ler PDF (pypdf) → separar questões 9-35
→ classificar tema+confiança (Ollama) → juntar com dificuldade → agrupar por tema → gráfico.
Decisão: o agente NÃO resolve a prova; a resposta certa vem do gabarito oficial (microdados).

---

## 5c. TCT COMPLETA + RAG (relatório automático)

TCT completa (notebook 01), salva em `resultados/`:
- `discriminacao.csv` — índice de discriminação (método Kelley 27%).
  Achado: Q18 (D=0,20) e Q26 (D=0,19) são FRACAS = difíceis E discriminam mal
  (nem os bons alunos acertaram → fragilidade coletiva real / possível problema de item).
- `tabela_tct_completa.csv` — dificuldade + discriminação + distrator mais marcado por questão.
  Distratores fortes (confusão conceitual): Q18 alt.E 41,5%; Q6 alt.A 42,2%; Q2 alt.A 42,4%.

RAG (notebook 02): o agente lê um CONTEXTO com os dados reais (ranking + 5 questões mais
difíceis com seus indicadores) e GERA um relatório pedagógico (diagnóstico + fragilidades +
recomendações). Salvo em `resultados/relatorio_agente.txt`.
- Funcionou bem: usou os números reais, interpretou conexões entre indicadores.
- CORRIGIDO: o contexto do RAG agora já traz a classificação em palavra calculada em Python
  (fraca/razoavel/boa/otima para discriminação; muito dificil/dificil/media/facil para
  dificuldade). O prompt também instrui usar numeração da PROVA e explica o que "fraca"
  significa. Resultado: agente parou de errar adjetivos e interpretou corretamente
  ("questões difíceis com discriminação fraca = fragilidade coletiva, até bons alunos erram").
- DECISÃO: usar numeração da PROVA (9 a 35) em relatórios e saídas, por ser mais clara ao leitor.
  (ainda falta ajustar os GRÁFICOS para também usarem numeração da prova.)
- Opcional futuro: pedir recomendações mais específicas por tema no prompt.

---

## 6. Mapeamento com a proposta

- 3.1 Levantamento e Preparação ......... FEITO (carga + limpeza)
- 3.2 Modelagem dos Indicadores ......... FEITO (temas classificados pelo agente)
- 3.3 Análise de Desempenho e TCT ....... FEITO (dificuldade + discriminação + distratores)
- 3.4 Interpretação e Padrões ........... FEITO (ranking + gráficos + diagnóstico do agente)
- 3.5 Documentação / Relatório .......... contínuo

## 5d. APLICAÇÃO STREAMLIT (Versão 1 - painel) — FUNCIONANDO

Arquivo `app.py` na pasta principal do projeto. Roda com: `streamlit run app.py`
(na primeira vez pede e-mail — deixar em branco e dar Enter). Abre em http://localhost:8501.
Para parar: Ctrl+C no terminal.

A aplicação (Versão 1) mostra em uma página web:
1. Visão geral (9.987 alunos, 19 válidas, 8 anuladas)
2. Ranking de fragilidades por tema (gráfico + tabela)
3. Dificuldade por questão (numeração da prova)
4. Diagnóstico gerado pelo agente de IA (lê relatorio_agente.txt)

Ela lê os arquivos salvos em `resultados/`. Gráfico de dificuldade com numeração da PROVA
salvo também em `dificuldade_questoes_prova.png`.

## 5e. APLICAÇÃO STREAMLIT — VERSÃO PREMIUM (v2) FUNCIONANDO

`app.py` turbinado, rodando com `streamlit run app.py`. Recursos:
- CSS customizado: fundo gradiente escuro, título com gradiente azul→ciano.
- Cartões de métrica e de fragilidade com efeito HOVER (sobem com sombra ao passar o mouse).
- Gráficos INTERATIVOS com Plotly (tema plotly_dark), tooltips customizados.
- 4 abas: Visão Geral | Fragilidades | Indicadores (TCT) | Diagnóstico IA.
- Gráfico novo "Mapa de qualidade das questões" (scatter dificuldade x discriminação,
  tamanho da bolha = força do distrator, linha de corte em 0,20).
- Seção expansível com tabela completa; barra lateral com infos do projeto.
- Instalado: plotly.

### Como mostrar para o Diego
- Forma recomendada: rodar no próprio PC (`streamlit run app.py`) e compartilhar a tela.
- Publicar na nuvem (Streamlit Community Cloud) é possível, MAS o Ollama roda local, então
  a parte de IA não funcionaria facilmente na nuvem. Deixar para depois, se o Diego pedir.

### LEMBRETE PERMANENTE sobre cópia de código
Toda vez que um trecho tem "\n" dentro de aspas, a cópia para o VS Code quebra e gera
"SyntaxError: unterminated string literal". Solução adotada: evitar "\n" em strings
(usar chr(10).join(lista), ou juntar texto numa linha só com separadores | ).

## 7bis. Falta para fechar (quando retomar)
- Aplicação Versão 3: receber uma PROVA NOVA (PDF) + planilha de respostas e processar tudo
  na hora (hoje a app só exibe os resultados já calculados do ENADE 2021).
- Organizar código em módulos reutilizáveis (src/: extracao, agente, analise_tct, relatorio).
- Opcional: refinar recomendações do agente (mais específicas por tema); ajustar "(1 questoes)"
  para singular/plural correto.
- CONFIRMAR COM O DIEGO (prioridade, pois define a Versão 3):
  * O resultado atual está no caminho certo?
  * De onde virão as respostas dos alunos de provas futuras (ADA etc.) e em qual formato?
  * Nível de automação total (sem revisão) é aceitável; como citar o log de confiança.
  * Validar os indicadores da TCT escolhidos.

## 5f. VERSÃO 3 EM CONSTRUÇÃO — Aplicação completa (upload + processa tudo)

DECISÃO: construir aplicação premium que RECEBE arquivos (PDF da prova + microdados) e com
UM botão processa tudo e mostra os resultados. Stack escolhida: FastAPI (backend) +
HTML/CSS/JS (frontend). Assumindo formato ENADE (ajustar p/ ADA depois).
Instalado: fastapi, uvicorn, python-multipart, plotly, streamlit-option-menu, streamlit-extras.

### Módulos criados em backend/src/ (código "de produção", reaproveita os notebooks):
- `extracao.py` — ler_pdf() e separar_questoes() (genérica, parâmetros de faixa de questões). OK.
- `analise_tct.py` — carregar_dados_curso(co_grupo), montar_tabela_acertos(),
  indice_dificuldade(), indice_discriminacao() (Kelley 27%), analisar_distratores(),
  classificar_dificuldade/discriminacao(), analise_completa(). OK, testado = 9987 alunos.
- `agente.py` — classificar_tema() + normalizar_tema() (resolve "Banco" vs "Bancos de Dados"),
  classificar_todas(), gerar_diagnostico(). OK.
- `pipeline.py` — analisar_prova(): orquestra tudo e retorna {num_alunos, tabela, ranking,
  diagnostico}. TESTADO DE PONTA A PONTA e funcionando (um comando faz tudo).

### Observações técnicas importantes
- LLM não é determinístico: pode variar classificação entre execuções e escrever o tema de
  formas diferentes. Resolvido com normalizar_tema() (força tema da lista oficial TEMAS_PADRAO).
- Processar tudo demora vários minutos (classificar 27 questões é a parte lenta) -> na app
  web PRECISA de barra de progresso para o usuário não achar que travou.
- DtypeWarning do pandas é inofensivo (pode silenciar com low_memory=False).
- Lembrete eterno: nunca usar "\n" dentro de aspas no código colado (quebra na cópia) -> usar chr(10).

### Próximos passos da Versão 3
1. Criar backend/main.py (FastAPI): endpoint que recebe uploads e chama pipeline.analisar_prova.
2. Criar frontend premium (HTML/CSS/JS): upload + botão Analisar + telas de resultado.
3. Conectar frontend <-> backend; barra de progresso.

## 5g. APLICAÇÃO WEB COMPLETA (Versão 3) — FUNCIONANDO DE PONTA A PONTA

Nome do produto: **ProvaScan**.

### Backend (FastAPI) — `backend/main.py`
- Endpoint GET "/" (status) e POST "/analisar" (recebe prova PDF + arq1 + arq3 + co_grupo,
  salva em pasta temporária, chama pipeline.analisar_prova e devolve JSON com
  num_alunos, ranking, tabela, diagnostico). CORS liberado.
- Rodar: `cd backend` depois `uvicorn main:app --reload` (fica em http://127.0.0.1:8000).

### Frontend premium — pasta `frontend/` (index.html, style.css, script.js)
- Estilo final escolhido (ref. do usuário "EXPENSE IT"): FUNDO PRETO + AURORA VERDE animada,
  título gigante em maiúsculas, verde neon com degradê, fonte Inter (Google Fonts).
  (Antes tínhamos tentado roxo/Streamlit, mas o usuário quis verde/preto num frontend HTML.)
- Navbar fixa, hero, duas ABAS: ENADE (funcional) e ADA (painel "EM BREVE" estilizado).
- Upload de 3 arquivos (ícones SVG, "✓ Selecionado" animado ao escolher), campo CO_GRUPO,
  botão "Analisar Prova" (pulso de luz + brilho no hover + efeito de clique).
- Barra de progresso (spinner) enquanto processa.
- Resultados: 4 cards de resumo, FILTROS (por tema e por nível de dificuldade),
  3 gráficos Plotly (ranking, dificuldade por questão, mapa dificuldade x discriminação),
  tabela com busca por tema, e o diagnóstico da IA.
- script.js guarda os dados em DADOS_GLOBAL e redesenha com desenharTudo() ao mexer nos filtros.

### COMO ABRIR O SITE (toda vez)
1. Ollama rodando (ícone da lhama).
2. VS Code terminal: `cd "...\Projeto Estagio Obrigatorio\backend"` depois `uvicorn main:app --reload`.
3. Dois cliques em frontend/index.html (abre no navegador).
Parar: Ctrl+C no terminal do backend.

### Performance
- Trocado o modelo do Ollama de llama3.1:8b para **llama3.2:3b** (mais rápido; classificação
  continuou boa). MODELO fica definido no topo de backend/src/agente.py.
- Ideia futura p/ acelerar ainda mais: cache dos temas já classificados.

## 7ter. Pendências / próximos passos
- Escrever o RELATÓRIO/TCC (atividade 3.5) — ainda falta, é o que mais convém focar agora.
- CONFIRMAR COM O DIEGO (define a aba ADA): formato dos dados da ADA (igual ENADE?),
  nível de automação aceitável, validar indicadores da TCT.
- Opcional: botão/atalho .bat para abrir backend + navegador de uma vez.
- Opcional: refinamentos visuais pontuais conforme feedback.

## 5h. MELHORIAS FINAIS DA APLICAÇÃO (ProvaScan)

- Voltou para o modelo **llama3.1:8b** (classificação melhor que o 3b). O 3b dava
  "Nao classificado" e temas inconsistentes. Como agora há cache + histórico, rodar o 8b
  uma vez por prova não é problema. (Apagar a pasta backend/src/cache força reclassificar.)
- CACHE de temas: backend/src/agente.py salva a classificação por "assinatura" da prova
  (hash). Repetir a mesma prova fica instantâneo. normalizar_tema() trata "Nao classificado".
- HISTÓRICO de análises (backend/main.py): endpoints /historico (lista), /historico/{id}
  (carrega), DELETE /historico/{id} (apaga). Cada análise é salva em backend/historico/*.json
  com o NOME que o usuário digita no campo "Nome da analise". Aparece como cards em
  "Analises Salvas"; clicar em "Ver resultados" carrega instantâneo; botão lixeira apaga.
- IMPORTANTE: rodar o backend DA PASTA backend (onde está main.py), não de src:
  `cd backend` depois `uvicorn main:app --reload`. (Rodar de src dá "Could not import module main".)
- Barra de progresso corrigida: a bolinha fica girando e a mensagem muda a cada 8s
  (Enviando... / Lendo PDF... / IA classificando... / TCT... / diagnóstico... / finalizando).
- Função cor() dos gráficos com 5 faixas (vermelho->verde) para o ranking não ficar tudo laranja.
- Botão "Baixar Diagnostico em PDF" no fim do painel de diagnóstico (usa jsPDF, só o texto).
- Tempos medidos (8b): classificar temas ~385s (gargalo), diagnóstico ~80s, resto rápido.

## 5i. RESUMO PARA APRESENTAÇÃO
Criado arquivo RESUMO_PARA_APRESENTACAO.md (explica o que a app faz, LLM/TCT/RAG e cada
gráfico, em linguagem simples para o Diego). Copiar para a pasta docs do projeto.

## CHECKLIST DA PROPOSTA (conferido)
- 3.1 Levantamento e Preparação ......... FEITO
- 3.2 Modelagem dos Indicadores ......... FEITO
- 3.3 Análise de Desempenho e TCT ....... FEITO
- 3.4 Interpretação e Padrões ........... FEITO
- 3.5 Documentação / RELATÓRIO FINAL .... FALTA (é o próximo grande passo)
A parte técnica está concluída e ATÉ ALÉM do pedido (a proposta só pedia análise; foi
construída uma aplicação web completa com agente de IA, histórico e exportação de PDF).

## PRÓXIMO PASSO QUANDO VOLTAR (prioridade)
1. ESCREVER O RELATÓRIO FINAL (atividade 3.5) — o Kiro vai ajudar a montar estrutura
   (introdução, objetivos, metodologia TCT+LLM+RAG, arquitetura/abordagem, resultados,
   conclusão) e preencher usando tudo que já foi construído.
2. Mostrar a ferramenta ao Diego e alinhar pendências:
   - formato dos dados da ADA (para ativar a aba ADA)
   - nível de automação total é aceitável academicamente / como citar o log de confiança
   - validar os indicadores da TCT escolhidos.

## STATUS GERAL: Atividades 3.1-3.4 CONCLUÍDAS. Aplicação ProvaScan completa e funcionando
(upload + botão + pipeline + resultados interativos + histórico + PDF). Falta a 3.5
(relatório final) e adaptar para a ADA após confirmar o formato com o Diego.

---

## 7. Roteiro de construção (quando retomar)

### Fase A — Agente de IA (classificação de temas)
1. Instalar Ollama (https://ollama.com/download) + baixar `llama3.1:8b`.
2. Testar o Ollama.
3. Conectar Python ao Ollama (biblioteca `ollama`).
4. Módulo de EXTRAÇÃO: ler PDF e separar os enunciados das questões.
5. Módulo do AGENTE: classificar tema + nível de confiança (automático, com log).

### Fase B — Completar a análise TCT
6. Índice de discriminação (correlação ponto-bisserial).
7. Análise de distratores.
8. Agrupar indicadores por TEMA → ranking de fragilidades.

### Fase C — Aplicação
9. RAG: o agente consulta os resultados e gera diagnóstico + recomendações.
10. Interface (Streamlit): enviar prova + respostas e ver tudo na tela.
11. Generalizar: aceitar qualquer prova no formato padrão (ENADE, ADA...).

### Lembretes
- Hardware do João: Acer Nitro, i7-11800H, 16 GB RAM, GPU GTX 1660 → roda modelos 8B bem.
- Ollama de texto não lê diagramas; para TEMA o texto costuma bastar.
- A aplicação precisa de respostas dos alunos + gabarito de CADA prova (ver ponto em aberto).

### Confirmar com o Diego
- Foco em Ciência da Computação Bacharelado (ENADE 2021). [provável OK]
- Validar indicadores da TCT.
- A ADA (e outras provas) têm dados de resposta por aluno? Em que formato?
- O nível de automação total (sem revisão) é aceitável academicamente? Como citar o controle
  de confiança no relatório.
```
