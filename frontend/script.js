// ============================================================
// ProvaScan - script.js
// ============================================================
const API = "http://127.0.0.1:8000";
let DADOS_GLOBAL = null;

function ligarDrop(dropId, inputId, nameId) {
    const drop = document.getElementById(dropId);
    const input = document.getElementById(inputId);
    const nome = document.getElementById(nameId);
    input.addEventListener("change", () => {
        if (input.files.length > 0) {
            nome.textContent = input.files[0].name;
            drop.classList.add("filled");
        }
    });
}
ligarDrop("drop-prova", "file-prova", "name-prova");
ligarDrop("drop-arq1", "file-arq1", "name-arq1");
ligarDrop("drop-arq3", "file-arq3", "name-arq3");

document.getElementById("btn-analisar").addEventListener("click", async () => {
    const prova = document.getElementById("file-prova").files[0];
    const arq1 = document.getElementById("file-arq1").files[0];
    const arq3 = document.getElementById("file-arq3").files[0];
    const coGrupo = document.getElementById("co-grupo").value;
    const nomeAnalise = document.getElementById("nome-analise").value || ("Analise " + new Date().toLocaleString());

    if (!prova || !arq1 || !arq3) {
        alert("Por favor, selecione os 3 arquivos (prova, arq1 e arq3).");
        return;
    }

    const progressBox = document.getElementById("progress-box");
    const progressText = document.getElementById("progress-text");
    progressBox.style.display = "block";
    document.getElementById("results").style.display = "none";
    progressBox.scrollIntoView({ behavior: "smooth" });

    const mensagens = [
        "Enviando arquivos...",
        "Lendo o PDF e separando as questoes...",
        "A IA esta classificando o tema de cada questao (isso leva alguns minutos)...",
        "Calculando a Teoria Classica dos Testes...",
        "Gerando o diagnostico pedagogico com a IA...",
        "Quase la, finalizando..."
    ];
    let idx = 0;
    progressText.textContent = mensagens[0];
    const timer = setInterval(() => {
        idx = (idx + 1) % mensagens.length;
        progressText.textContent = mensagens[idx];
    }, 8000);

    const form = new FormData();
    form.append("prova", prova);
    form.append("arq1", arq1);
    form.append("arq3", arq3);
    form.append("co_grupo", coGrupo);
    form.append("nome", nomeAnalise);

    try {
        const resp = await fetch(API + "/analisar", { method: "POST", body: form });
        const dados = await resp.json();
        clearInterval(timer);

        if (dados.erro) { progressText.textContent = "Erro: " + dados.erro; return; }

        progressText.textContent = "Analise concluida!";
        await new Promise(r => setTimeout(r, 700));
        progressBox.style.display = "none";
        DADOS_GLOBAL = dados;
        mostrarResultados(dados);
        carregarHistorico();
    } catch (e) {
        clearInterval(timer);
        progressText.textContent = "Erro de conexao com o servidor: " + e.message;
    }
});

function mostrarResultados(dados) {
    const results = document.getElementById("results");
    results.style.display = "block";

    const pior = [...dados.ranking].sort((a,b)=>a.media_acerto-b.media_acerto)[0];
    document.getElementById("cards").innerHTML = `
        <div class="card"><div class="card-num">${dados.num_alunos}</div><div class="card-label">Alunos analisados</div></div>
        <div class="card"><div class="card-num">${dados.tabela.length}</div><div class="card-label">Questoes validas</div></div>
        <div class="card"><div class="card-num">${dados.ranking.length}</div><div class="card-label">Temas identificados</div></div>
        <div class="card"><div class="card-num">${pior.media_acerto}%</div><div class="card-label">Maior fragilidade: ${pior.tema}</div></div>
    `;

    const selTema = document.getElementById("filtro-tema");
    selTema.innerHTML = '<option value="todos">Todos os temas</option>';
    [...new Set(dados.tabela.map(t => t.tema))].sort().forEach(t => {
        selTema.innerHTML += `<option value="${t}">${t}</option>`;
    });

    desenharTudo();
    document.getElementById("diagnostico").textContent = dados.diagnostico;
    results.scrollIntoView({ behavior: "smooth" });
}

function desenharTudo() {
    const dados = DADOS_GLOBAL;
    const tema = document.getElementById("filtro-tema").value;
    const nivel = document.getElementById("filtro-nivel").value;

    let tabela = [...dados.tabela];
    if (tema !== "todos") tabela = tabela.filter(t => t.tema === tema);
    if (nivel !== "todos") {
        tabela = tabela.filter(t => {
            if (nivel === "dificil") return t.pct_acerto < 30;
            if (nivel === "medio") return t.pct_acerto >= 30 && t.pct_acerto < 50;
            if (nivel === "facil") return t.pct_acerto >= 50;
        });
    }

    const rk = [...dados.ranking].sort((a,b)=>a.media_acerto-b.media_acerto);
    Plotly.newPlot("grafico-ranking", [{
        type:"bar", orientation:"h",
        x: rk.map(r=>r.media_acerto), y: rk.map(r=>r.tema),
        text: rk.map(r=>r.media_acerto+"%"), textposition:"outside",
        marker:{color: rk.map(r=>cor(r.media_acerto))},
        hovertemplate:"<b>%{y}</b><br>Acerto: %{x}%<extra></extra>"
    }], layoutG(420), {responsive:true, displayModeBar:false});

    const tb = [...tabela].sort((a,b)=>a.pct_acerto-b.pct_acerto);
    Plotly.newPlot("grafico-dificuldade", [{
        type:"bar",
        x: tb.map(t=>"Q"+t.questao_prova), y: tb.map(t=>t.pct_acerto),
        text: tb.map(t=>t.pct_acerto+"%"), textposition:"outside",
        marker:{color: tb.map(t=>cor(t.pct_acerto))},
        hovertemplate:"<b>Q%{x}</b><br>Acerto: %{y}%<extra></extra>"
    }], layoutG(400), {responsive:true, displayModeBar:false});

    Plotly.newPlot("grafico-mapa", [{
        type:"scatter", mode:"markers+text",
        x: tabela.map(t=>t.pct_acerto), y: tabela.map(t=>t.indice_discriminacao),
        text: tabela.map(t=>"Q"+t.questao_prova), textposition:"top center",
        marker:{ size: tabela.map(t=> (t.distrator_pct||10)/2 ), color: tabela.map(t=>cor(t.pct_acerto)) },
        hovertemplate:"<b>Q%{text}</b><br>Acerto: %{x}%<br>Discriminacao: %{y:.2f}<extra></extra>"
    }], Object.assign(layoutG(440), {
        xaxis:{title:"% de acerto (dificuldade)", gridcolor:"rgba(255,255,255,0.08)"},
        yaxis:{title:"Discriminacao", gridcolor:"rgba(255,255,255,0.08)"},
        shapes:[{type:"line", x0:0, x1:100, y0:0.2, y1:0.2, line:{color:"#ef4444", dash:"dash"}}]
    }), {responsive:true, displayModeBar:false});

    const busca = document.getElementById("busca-tabela").value.toLowerCase();
    let linhas = tabela.filter(t => t.tema.toLowerCase().includes(busca));
    let html = "<table class='tabela'><tr><th>Questao</th><th>Tema</th><th>% Acerto</th><th>Discriminacao</th><th>Distrator</th></tr>";
    linhas.sort((a,b)=>a.pct_acerto-b.pct_acerto).forEach(t => {
        html += `<tr><td>Q${t.questao_prova}</td><td>${t.tema}</td><td>${t.pct_acerto}%</td><td>${t.classif_discriminacao}</td><td>${t.distrator} (${t.distrator_pct}%)</td></tr>`;
    });
    html += "</table>";
    document.getElementById("tabela-container").innerHTML = html;
}

function cor(v){
    if(v < 25) return "#ef4444";
    if(v < 35) return "#f97316";
    if(v < 45) return "#eab308";
    if(v < 55) return "#84cc16";
    return "#22c55e";
}
function layoutG(altura){
    return { height:altura, paper_bgcolor:"rgba(0,0,0,0)", plot_bgcolor:"rgba(0,0,0,0)",
        font:{color:"#E8ECFA"}, margin:{l:160,r:40,t:20,b:50},
        xaxis:{gridcolor:"rgba(255,255,255,0.08)"}, yaxis:{gridcolor:"rgba(255,255,255,0.08)"} };
}

function trocarAba(qual){
    document.getElementById("aba-enade").style.display = (qual==="enade")?"block":"none";
    document.getElementById("aba-ada").style.display = (qual==="ada")?"block":"none";
    document.getElementById("tab-enade").classList.toggle("active", qual==="enade");
    document.getElementById("tab-ada").classList.toggle("active", qual==="ada");
}

// ============================================================
// HISTORICO
// ============================================================
async function carregarHistorico() {
    try {
        const resp = await fetch(API + "/historico");
        const lista = await resp.json();
        const grid = document.getElementById("historico-grid");
        if (!lista || lista.length === 0) {
            grid.innerHTML = '<p style="color:var(--suave);text-align:center;grid-column:1/-1;">Nenhuma analise salva ainda. Faca sua primeira analise acima!</p>';
            return;
        }
        grid.innerHTML = "";
        lista.forEach(item => {
            const card = document.createElement("div");
            card.className = "hist-card";
            card.innerHTML = `
                <div class="hist-nome">${item.nome}</div>
                <div class="hist-info">${item.num_alunos} alunos · ${item.data}</div>
                <div class="hist-acoes">
                    <button class="hist-btn-ver" onclick="verAnalise('${item.id}')">Ver resultados</button>
                    <button class="hist-btn-del" onclick="apagarAnalise('${item.id}', event)" title="Apagar">🗑</button>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (e) {
        console.log("Erro ao carregar historico:", e);
    }
}

async function verAnalise(id) {
    try {
        const resp = await fetch(API + "/historico/" + id);
        const dados = await resp.json();
        if (dados.erro) { alert(dados.erro); return; }
        DADOS_GLOBAL = dados;
        mostrarResultados(dados);
    } catch (e) {
        alert("Erro ao carregar: " + e.message);
    }
}

async function apagarAnalise(id, ev) {
    ev.stopPropagation();
    if (!confirm("Apagar esta analise salva?")) return;
    await fetch(API + "/historico/" + id, { method: "DELETE" });
    carregarHistorico();
}

carregarHistorico();
// ============================================================
// BAIXAR RELATORIO EM PDF
// ============================================================
async // ============================================================
// BAIXAR SO O DIAGNOSTICO EM PDF
// ============================================================
function baixarPDF() {
    try {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF("p", "mm", "a4");
        const largura = 210;
        let y = 20;

        const nome = DADOS_GLOBAL.nome || "Analise";

        // Cabecalho
        pdf.setFontSize(18);
        pdf.setTextColor(34, 150, 70);
        pdf.text("ProvaScan - Diagnostico Pedagogico", 15, y);
        y += 8;
        pdf.setFontSize(10);
        pdf.setTextColor(120, 120, 120);
        pdf.text(`${nome}  |  ${DADOS_GLOBAL.num_alunos} alunos analisados`, 15, y);
        y += 6;
        pdf.setDrawColor(34, 197, 94);
        pdf.line(15, y, largura - 15, y);
        y += 10;

        // Texto do diagnostico
        pdf.setFontSize(11);
        pdf.setTextColor(40, 40, 40);
        const linhas = pdf.splitTextToSize(DADOS_GLOBAL.diagnostico, largura - 30);
        linhas.forEach(linha => {
            if (y > 280) { pdf.addPage(); y = 20; }
            pdf.text(linha, 15, y);
            y += 6;
        });

        pdf.save(`diagnostico_${nome.replace(/[^a-zA-Z0-9]/g, "_")}.pdf`);
    } catch (e) {
        alert("Erro ao gerar PDF: " + e.message);
    }
}
