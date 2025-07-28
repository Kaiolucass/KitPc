const respostas = {};

function setAnswer(campo, valor, event) {
  event.preventDefault();
  respostas[campo] = valor;

  const span = document.getElementById(campo);
  if (span) {
    span.textContent = valor;
  }

  console.log("📤 Respostas até agora:", respostas);
}

function finalizar() {
  const camposObrigatorios = ["preco", "tipo", "uso", "gpu", "processador", "laptop"];
  const faltando = camposObrigatorios.find(campo => !respostas[campo]);

  if (faltando) {
    alert("⚠️ Por favor, responda todas as perguntas.");
    return;
  }

  document.getElementById("resultado").innerHTML = `
    <div class="text-center p-4">
      <div class="spinner-border text-info" role="status">
        <span class="visually-hidden">Carregando...</span>
      </div>
      <p class="mt-3 fs-5 text-info">🔧 Montando seu setup... Aguarde...</p>
    </div>
  `;

  fetch("/montar-setup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(respostas)
  })
    .then(res => res.json())
    .then(data => {
      if (data.erro) {
        document.getElementById("resultado").innerHTML = `
          <div class="alert alert-danger text-center">❌ ${data.erro}</div>
        `;
        return;
      }

      let html = "<h3 class='mb-4 text-info'><i class='fas fa-wrench'></i> Setup Recomendado:</h3>";
      data.forEach(produto => {
        html += `
        <div class="card mb-3 shadow-sm" style="max-width: 100%;">
          <div class="row g-0">
            <div class="col-md-2 d-flex align-items-center">
              <img src="${produto.imagem || '/static/Imagens/placeholder.png'}" 
                   class="img-fluid rounded-start" 
                   alt="Imagem da peça">
            </div>
            <div class="col-md-10">
              <div class="card-body">
                <h5 class="card-title">🔹 ${produto.componente}</h5>
                <p class="card-text"><strong>${produto.nome}</strong></p>
                <p class="card-text">💰 <strong>${produto.preco || "Preço indisponível"}</strong></p>
                ${produto.link 
                  ? `<a href="${produto.link}" target="_blank" class="btn btn-sm btn-success">Ver na loja</a>` 
                  : "<span class='text-muted'>Sem link disponível</span>"}
                ${produto.erro 
                  ? `<p class="text-danger mt-2">⚠️ ${produto.erro}</p>` 
                  : ""}
              </div>
            </div>
          </div>
        </div>`;
      });

      document.getElementById("resultado").innerHTML = html;
    })
    .catch(error => {
      document.getElementById("resultado").innerHTML = `
        <p class='text-danger'>❌ Erro ao conectar com o servidor Flask.</p>
      `;
      console.error("Erro na requisição:", error);
    });
}