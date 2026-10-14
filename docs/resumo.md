# ProvaScan — Resumo para apresentação (explicar ao Diego)

## O que a aplicação faz (em 1 frase)
A pessoa envia uma prova (PDF) + os dados dos alunos, clica em "Analisar", e o sistema
descobre automaticamente em quais temas os alunos têm mais dificuldade e gera um
diagnóstico pedagógico.

## Como funciona (o fluxo)
1. Lê o PDF e separa as questões
2. A IA (LLM) classifica o tema de cada questão
3. Calcula a estatística dos ~10 mil alunos (TCT)
4. Cruza "tema + desempenho" -> acha as fragilidades
5. A IA (RAG) escreve o diagnóstico com recomendações

## Conceitos (resumido)

### LLM (modelo de linguagem / a "IA")
Modelo que lê e entende texto (tipo ChatGPT). No projeto roda LOCALMENTE no PC
(Ollama + modelo Llama) — de graça e privado. Ele lê cada questão e diz o tema
(ex.: "isso é de Redes").

### TCT (Teoria Clássica dos Testes)
Estatística que mede a qualidade da prova, questão por questão. Três medidas:
- Dificuldade = % de alunos que acertou (baixo = tema difícil)
- Discriminação = se a questão separa quem sabe de quem não sabe
- Distratores = qual alternativa errada mais confundiu os alunos

### RAG (Retrieval-Augmented Generation)
Técnica onde a IA, antes de escrever o relatório, LÊ os dados reais calculados e escreve
BASEADA neles (não inventa números). Por isso o diagnóstico é confiável.

> Divisão de trabalho: a TCT (estatística) mede as dificuldades com dados reais;
> a IA só dá nome aos temas e escreve o relatório. As fragilidades vêm dos números.

## O que cada gráfico mostra

1. Ranking de Fragilidades por Tema (barras horizontais)
   Média de acerto por tema. Temas no topo (vermelho) = maiores fragilidades.
   "É aqui que estão os maiores buracos de aprendizado."

2. Dificuldade por Questão (barras verticais)
   % de acerto de cada questão, da mais difícil (vermelho) à mais fácil (verde).
   "Mostra questão por questão onde os alunos tropeçaram."

3. Mapa: Dificuldade x Discriminação (bolhas)
   Eixo horizontal = dificuldade; eixo vertical = discriminação; linha vermelha = limite 0,20.
   Bolhas abaixo da linha e à esquerda = questões difíceis que nem os bons alunos acertaram
   (fragilidade coletiva real). Tamanho da bolha = força do distrator.
   "Separa 'questão difícil mas boa' de 'questão difícil que ninguém soube'."

4. Tabela de Detalhamento
   Cada questão com tema, % de acerto, discriminação e distrator mais marcado.

5. Diagnóstico da IA
   Texto final: resumo geral + principais fragilidades + recomendações de ensino.
   "A IA transforma os números num plano de ação para o professor."

## Frase de abertura (sugestão)
"Construí uma ferramenta que analisa provas como o ENADE. Ela usa estatística (Teoria
Clássica dos Testes) sobre o desempenho de ~10 mil alunos para medir as dificuldades, e uma
IA local para classificar os temas das questões e gerar um diagnóstico pedagógico automático.
O resultado mostra, de forma visual, em quais assuntos os alunos de Ciência da Computação têm
mais fragilidade — saindo da nota fria para o detalhe do que precisa ser reforçado."

## Resultado principal (ENADE 2021 Ciência da Computação, 9.987 alunos)
Maiores fragilidades: Teoria da Computação, Interação Humano-Computador, Segurança da
Informação, Arquitetura de Computadores e Algoritmos e Estrutura de Dados.
Observação: a prova foi difícil (nenhuma questão passou de ~65% de acerto).
