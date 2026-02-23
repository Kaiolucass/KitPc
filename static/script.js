const respostas = {};

function setAnswer(campo, valor, event) {
    event.preventDefault();
    respostas[campo] = valor;

    const span = document.getElementById(campo);
    if (span) span.textContent = valor;

    // Estilo visual nos botões
    const botoes = event.target.parentElement.querySelectorAll('button');
    botoes.forEach(btn => btn.classList.remove('btn-info', 'text-dark'));
    event.target.classList.add('btn-info', 'text-dark');
}

function finalizar() {
    const camposObrigatorios = ["preco", "tipo", "uso", "gpu", "processador", "laptop"];
    const faltando = camposObrigatorios.find(campo => !respostas[campo]);

    if (faltando) {
        alert("⚠️ Por favor, responda todas as perguntas para a IA trabalhar!");
        return;
    }

    // Efeito de carregamento
    document.getElementById("resultado").innerHTML = `
        <div class="text-center p-5 border border-info rounded bg-dark shadow-lg mt-4">
            <div class="spinner-grow text-info" role="status"></div>
            <p class="mt-3 fs-5 text-info animate-pulse">🤖 A IA está analisando peças e preços para 2026...</p>
        </div>
    `;

    fetch("/consultoria-ia", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(respostas)
    })
    .then(res => res.json())
    .then(data => {
        if (data.erro) {
            document.getElementById("resultado").innerHTML = `<div class="alert alert-danger">❌ ${data.erro}</div>`;
            return;
        }

        // SALVA OS DADOS PARA O PDF PODER USAR DEPOIS
        localStorage.setItem('ia_last_response_data', JSON.stringify(data));

        // MONTA O HTML DAS PEÇAS
        let htmlComponentes = "";
        data.setup.forEach(comp => {
            htmlComponentes += `
            <div class="card mb-3 bg-dark border-secondary text-white shadow-sm animate-fade-in">
                <div class="row g-0 align-items-center">
                    <div class="col-md-2 text-center p-2">
                        <img src="${comp.imagem_url}" class="img-fluid rounded" 
                             onerror="this.src='/static/Imagens/placeholder.png'" 
                             style="max-height: 80px; object-fit: contain;">
                    </div>
                    <div class="col-md-10">
                        <div class="card-body py-2">
                            <h6 class="text-info mb-1">${comp.componente}</h6>
                            <p class="mb-0"><strong>${comp.nome}</strong> - <span class="text-success">${comp.preco_estimado}</span></p>
                            <p class="small text-muted mb-0">${comp.descricao_leiga}</p>
                        </div>
                    </div>
                </div>
            </div>`;
        });

        document.getElementById("resultado").innerHTML = `
            <div class="card bg-dark border-info shadow-lg mt-4 animate-fade-in">
                <div class="card-header border-info text-center py-3">
                    <h3 class='mb-0 text-info'><i class='fas fa-robot'></i> Seu PC Personalizado</h3>
                </div>
                <div class="card-body p-4">
                    ${htmlComponentes}
                    <div class="ai-response mt-4 p-3 border-start border-info bg-black text-light">
                        <h5 class="text-info">Por que esse PC?</h5>
                        <p style="white-space: pre-line;">${data.justificativa_geral}</p>
                    </div>
                    <div class="text-center mt-4">
                        <button class="btn btn-outline-info" onclick="gerarPDF()">
                            <i class="fas fa-file-pdf"></i> Baixar Relatório para Leigos (PDF)
                        </button>
                    </div>
                </div>
            </div>
        `;
    })
    .catch(error => {
        document.getElementById("resultado").innerHTML = `<div class="alert alert-danger">❌ Erro ao conectar com o Flask.</div>`;
    });
}

// FUNÇÃO PARA GERAR O PDF
async function gerarPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const data = JSON.parse(localStorage.getItem('ia_last_response_data'));

    if (!data) return alert("Erro ao carregar dados do PDF.");

    // Estilo do PDF
    doc.setFillColor(20, 20, 20); // Fundo escuro
    doc.rect(0, 0, 210, 297, 'F');
    
    doc.setTextColor(0, 242, 255); // Ciano
    doc.setFontSize(22);
    doc.text("KITPC - CONSULTORIA TÉCNICA", 10, 20);
    
    doc.setDrawColor(0, 242, 255);
    doc.line(10, 25, 200, 25);

    let y = 40;
    doc.setFontSize(14);
    doc.text("Configuração Recomendada:", 10, y);
    y += 10;

    data.setup.forEach(comp => {
        doc.setTextColor(0, 242, 255);
        doc.setFontSize(11);
        doc.text(`${comp.componente}: ${comp.nome}`, 10, y);
        y += 6;
        doc.setTextColor(200, 200, 200);
        const desc = doc.splitTextToSize(`Explicação: ${comp.descricao_leiga}`, 180);
        doc.text(desc, 15, y);
        y += (desc.length * 5) + 5;
    });

    doc.setTextColor(0, 242, 255);
    doc.text("Justificativa do Especialista:", 10, y);
    y += 7;
    doc.setTextColor(255, 255, 255);
    const justificativa = doc.splitTextToSize(data.justificativa_geral, 180);
    doc.text(justificativa, 10, y);

    doc.save("Meu_PC_KitPC.pdf");
}

// 1. Assim que a página abre, verifica o estado do sino
document.addEventListener("DOMContentLoaded", function() {
    const jaInscrito = localStorage.getItem('userEmail');
    const bellContainer = document.getElementById("notification-bell");
    
    if (jaInscrito) {
        bellContainer.classList.add("bell-active");
    }
});

// 2. Lógica do Clique no Sino
function handleBellClick() {
    const notifyBox = document.getElementById("notify-box");
    const jaInscrito = localStorage.getItem('userEmail');

    if (jaInscrito) {
        alert("🔔 Notificações ativas para: " + jaInscrito);
    } else {
        notifyBox.style.display = (notifyBox.style.display === "none") ? "block" : "none";
    }
}

// 3. Função para salvar o e-mail quando clicar no botão do formulário
function salvarEEnviar(event) {
    // Pegamos o e-mail que o utilizador digitou
    const emailInput = document.querySelector('#notify-box input[name="email"]').value;
    
    if (emailInput && emailInput.includes('@')) {
        localStorage.setItem('userEmail', emailInput); // Guarda no navegador
        // O formulário seguirá o envio normal para o Flask
    }
}