const respostas = {};
let setupAtual = [];

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
        setupAtual = data.setup;
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
    // 1. Captura os dados da tela
    const precoTexto = document.getElementById("total-preco")?.innerText || "R$ 0,00";
    const objetivoTexto = document.getElementById("objetivo-selecionado")?.value || "Uso Geral";
    const conselhoTexto = document.getElementById("conselho-mestre")?.innerText || "Boa montagem!";

    const dadosSetup = {
        setup: setupAtual, // Certifique-se que esta variável global foi preenchida na função de montar
        total_estimado: precoTexto,
        objetivo: objetivoTexto,
        conselho_mestre: conselhoTexto
    };

    // Mensagem visual para o usuário saber que está gerando
    const btnPdf = document.querySelector(".btn-pdf");
    if(btnPdf) btnPdf.innerText = "⏳ Gerando PDF...";

    fetch("/gerar-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dadosSetup)
    })
    .then(response => {
        if (!response.ok) throw new Error("Erro no servidor ao gerar PDF");
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = "Guia_Montagem_KitPC.pdf";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        if(btnPdf) btnPdf.innerText = "📄 Gerar Relatório PDF";
    })
    .catch(error => {
        console.error("Erro:", error);
        alert("Ops! Houve um erro ao gerar o seu manual.");
        document.getElementById("area-acoes-pos-montagem").style.display = "block";
    });
}
