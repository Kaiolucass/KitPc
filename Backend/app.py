from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/montar-setup", methods=["POST"])
def montar_setup(): 
    dados = request.json
    preco = dados.get("preco")
    uso = dados.get("uso")
    gpu = dados.get("gpu")
    processador = dados.get("processador")
    tipo = dados.get("tipo")
    laptop = dados.get("laptop")

    if not all([preco, uso, gpu, processador, tipo, laptop]):
        return jsonify({"erro": "Preencha todas as respostas"}), 400

    # Exemplo simples de lógica
    if preco == "Um PC OK" and uso == "Estudos":
        setup = {
            "CPU": "Ryzen 5 5600G",
            "RAM": "16GB DDR4",
            "SSD": "480GB",
            "GPU": "Integrada Vega 7",
            "Fonte": "500W",
            "Placa-mãe": "A320M",
            "Gabinete": "Simples"
        }
    else:
        setup = {
            "mensagem": "Ainda estamos montando uma sugestão para essa combinação!"
        }

    return jsonify(setup)

if __name__ == "__main__":
    app.run(debug=True)
