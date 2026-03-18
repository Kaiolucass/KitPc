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


// Função para abrir/fechar ou mostrar o alerta
    function dispararSininho() {
        const box = document.getElementById("notify-box");
        const jaInscrito = localStorage.getItem('userEmail');

        if (jaInscrito) {
            alert("🔔 Notificações já estão ativadas para: " + jaInscrito);
        } else {
            // Alterna entre mostrar e esconder
            if (box.style.display === "none" || box.style.display === "") {
                box.style.display = "block";
            } else {
                box.style.display = "none";
            }
        }
    }

    // Função para salvar o email e mudar a cor
    function registrarInscricao() {
        const email = document.getElementById("email-notificacao").value;
        if (email && email.includes('@')) {
            localStorage.setItem('userEmail', email);
            // O formulário vai dar o submit sozinho por causa do type="submit"
        }
    }

    // Verifica ao carregar a página se deve mudar a cor do sino
    document.addEventListener("DOMContentLoaded", function() {
        const jaInscrito = localStorage.getItem('userEmail');
        const sino = document.getElementById("notification-bell");
        if (jaInscrito && sino) {
            sino.style.background = "#3CC9E4"; // Cor Ciano
            sino.style.boxShadow = "0 0 20px rgba(0, 242, 255, 0.6)";
        }
    });
// ... (mantenha suas funções setAnswer, finalizar e gerarPDF acima)

async function registerServiceWorkerAndGetToken() {
    // Verifica se o navegador suporta notificações
    if (!('serviceWorker' in navigator) || !('Notification' in window)) {
        console.warn('Este navegador não suporta notificações Push.');
        return;
    }

    try {
        const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
        
        // Pede permissão apenas se ainda não foi concedida ou negada
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            if (permission !== 'granted') return;
        }

        if (Notification.permission === 'granted') {
            const currentToken = await messaging.getToken({ 
                vapidKey: firebaseConfig.vapidKey, // Usa a variável definida no HTML
                serviceWorkerRegistration: registration 
            });

            if (currentToken) {
                sendTokenToServer(currentToken);
            }
        }
    } catch (error) {
        console.error('Erro no Firebase:', error);
    }
}

function sendTokenToServer(token) {
    fetch('/salvar-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token }),
    })
    .then(res => res.json())
    .then(data => console.log('Servidor respondeu:', data))
    .catch(err => console.error('Erro ao enviar token:', err));
}

// Inicia o processo
window.addEventListener('load', registerServiceWorkerAndGetToken);

// Listener para mensagens em primeiro plano
messaging.onMessage((payload) => {
    console.log('Notificação recebida:', payload);
    // Cria um alerta visual bonito ou usa o Notification API
    new Notification(payload.notification.title, {
        body: payload.notification.body,
        icon: '/static/Imagens/Logo KitPc.png'
    });
});

function gerarPDF() {
    // Pega os dados que já estão na tela (que o seu montador gerou)
    const dadosSetup = {
        setup: setupAtual, // Você deve salvar o JSON da resposta numa variável global
        total_estimado: document.getElementById("total-preco").innerText
    };

    fetch("/gerar-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dadosSetup)
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "meu_pc.pdf";
        a.click();
    });
}