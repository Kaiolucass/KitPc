const respostas = {};

function setAnswer(campo, valor, event) {
  event.preventDefault(); // Evita comportamento padrão
  respostas[campo] = valor;

  const span = document.getElementById(campo);
  if (span) {
    span.textContent = valor;
  }

  console.log("Respostas até agora:", respostas);
}

function finalizar() {
  // Verifica se todas as respostas foram preenchidas
  const campos = ["preco", "tipo", "uso", "gpu", "processador", "laptop"];
  for (let campo of campos) {
    if (!respostas[campo]) {
      alert("⚠️ Por favor, responda todas as perguntas.");
      return;
    }
  }

  fetch("http://localhost:5000/montar-setup", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(respostas)
  })
  .then(res => res.json())
  .then(data => {
    let html = "<h3>🔧 Setup Recomendado:</h3><ul class='list-group'>";
    for (const item in data) {
      html += `<li class='list-group-item'><strong>${item}:</strong> ${data[item]}</li>`;
    }
    html += "</ul>";
    document.getElementById("resultado").innerHTML = html;
  })
  .catch(error => {
    alert("❌ Erro ao conectar com o servidor Flask.");
    console.error(error);
  });
}
