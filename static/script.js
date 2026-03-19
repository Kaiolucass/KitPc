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
        alert("⚠️ Por favor, responda todas as perguntas!");
        return;
    }

    document.getElementById("resultado").innerHTML = `
        <div class="text-center p-5 border border-info rounded bg-dark shadow-lg mt-4">
            <div class="spinner-grow text-info" role="status"></div>
            <p class="mt-3 fs-5 text-info animate-pulse"> Estamos Calculando melhor custo-benefício...</p>
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

        setupAtual = data.setup;
        let somaTotal = 0;
        let htmlComponentes = "";

        // Percorre as peças, limpa o preço e soma
        data.setup.forEach(comp => {
            // Transforma "R$ 1.200,50" em 1200.50
            const precoLimpo = comp.preco_estimado
                .replace(/[R$\s.]/g, "") // Remove R$, espaços e pontos de milhar
                .replace(",", ".");      // Troca vírgula por ponto decimal
            
            somaTotal += parseFloat(precoLimpo) || 0;

            htmlComponentes += `
            <div class="card mb-3 bg-dark border-secondary text-white shadow-sm">
                <div class="row g-0 align-items-center">
                    <div class="col-md-2 text-center p-2">
                        <img src="${comp.imagem_url}" class="img-fluid rounded" onerror="this.src='/static/Imagens/placeholder.png'" style="max-height: 70px;">
                    </div>
                    <div class="col-md-10">
                        <div class="card-body py-2">
                            <h6 class="text-info mb-1">${comp.componente}</h6>
                            <p class="mb-0"><strong>${comp.nome}</strong> - <span class="text-success">${comp.preco_estimado}</span></p>
                        </div>
                    </div>
                </div>
            </div>`;
        });

        // Formata o total para exibir na tela
        const totalFormatado = somaTotal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

        document.getElementById("resultado").innerHTML = `
            <div class="card bg-dark border-info shadow-lg mt-4 animate-fade-in">
                <div class="card-header border-info text-center py-3">
                    <h3 class='mb-0 text-info'><i class='fas fa-robot'></i> Seu PC Personalizado</h3>
                </div>
                <div class="card-body p-4">
                    ${htmlComponentes}
                    
                    <div class="text-end my-4 p-3 bg-black rounded border border-secondary">
                        <h4 class="text-white mb-0">Total Estimado: <span class="text-success" id="preco-total-calculado">${totalFormatado}</span></h4>
                    </div>

                    <div class="ai-response mt-4 p-3 border-start border-info bg-black text-light">
                        <h5 class="text-info">Por que esse PC?</h5>
                        <p style="white-space: pre-line;">${data.justificativa_geral}</p>
                    </div>
                    <div class="text-center mt-4">
                        <button class="btn btn-info btn-lg fw-bold text-dark" onclick="gerarPDF()">
                            <i class="fas fa-file-pdf"></i> BAIXAR GUIA DE MONTAGEM (PDF)
                        </button>
                    </div>
                </div>
            </div>
            <div class="mt-4 p-4 text-center" 
                         style="border: 2px solid #3CC9E4; border-radius: 15px; background: rgba(60, 201, 228, 0.05);">
                        <h2 class="h4 mb-3 text-info">Ficou com alguma dúvida?</h2>
                        <p class="text-light opacity-75">Clique em saiba mais para aprender mais sobre cada componente do seu computador!</p>
                        <a href="/guia-pecas" class="btn btn-outline-info fw-bold">SAIBA MAIS</a>
                    </div>
                </div>
            </div>
        `;
    })
    .catch(error => {
        document.getElementById("resultado").innerHTML = `<div class="alert alert-danger">❌ Erro na conexão.</div>`;
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
    if (!setupAtual || setupAtual.length === 0) {
        alert("⚠️ Monte seu PC primeiro!");
        return;
    }

    // Pega o valor calcula e exibir na tela
    const totalCalculado = document.getElementById("preco-total-calculado")?.innerText || "R$ 0,00";

    const dadosSetup = {
        setup: setupAtual,
        total_estimado: totalCalculado, // Envia o total somado pelo JS
        objetivo: respostas["uso"] || "Uso Geral",
        conselho_mestre: "Mantenha a calma e organize os parafusos!"
    };

    const btnPdf = document.querySelector("button[onclick='gerarPDF()']");
    const textoOriginal = btnPdf.innerHTML;
    btnPdf.innerHTML = `<i class="fas fa-spinner fa-spin"></i> GERANDO...`;
    btnPdf.disabled = true;

    fetch("/gerar-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dadosSetup)
    })
    .then(response => {
        if (!response.ok) throw new Error();
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "Guia_Montagem_KitPC.pdf";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(() => alert("Erro ao gerar PDF no servidor."))
    .finally(() => {
        btnPdf.innerHTML = textoOriginal;
        btnPdf.disabled = false;
    });
}