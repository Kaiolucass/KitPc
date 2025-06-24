from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_total(preco_label):
    return {
        "Um PC OK": 2000,
        "Um PC BOM": 3000,
        "Um PC MUITO BOM": 5000,
        "Até a NASA quer": 10000
    }.get(preco_label, 2000)

def distribuir_orcamento(total, quer_gpu):
    return {
        "cpu": total * 0.25,
        "placa_mae": total * 0.15,
        "ram": total * 0.15,
        "gpu": total * 0.25 if quer_gpu else 0,
        "ssd": total * 0.10,
        "fonte": total * 0.07,
        "gabinete": total * 0.03
    }

def definir_pecas_basicas(processador, quer_gpu, total):
    if processador == "AMD":
        cpu_busca = "Ryzen 5 5600G" if not quer_gpu else "Ryzen 5 5600"
        placa_mae_busca = "Placa mãe B450"
    else:
        cpu_busca = "Intel i5 10400" if not quer_gpu else "Intel i5 11400F"
        placa_mae_busca = "Placa mãe B460"

    ram_busca = (
        "Memória RAM DDR4 32GB" if total >= 5000 else
        "Memória RAM DDR4 16GB" if total >= 3000 else
        "Memória RAM DDR4 8GB"
    )

    ssd_busca = (
        "SSD 1TB" if total >= 5000 else
        "SSD 480GB" if total >= 2500 else
        "SSD 240GB"
    )

    if quer_gpu:
        if total >= 6000:
            gpu_busca = "RTX 3060"
        elif total >= 4000:
            gpu_busca = "RX 6600"
        else:
            gpu_busca = "RX 580"
    else:
        gpu_busca = "Processador com vídeo integrado"

    fonte_busca = "Fonte 600W" if quer_gpu else "Fonte 450W"
    gabinete = "Gabinete gamer ATX"

    return {
        "cpu": cpu_busca,
        "placa_mae": placa_mae_busca,
        "ram": ram_busca,
        "gpu": gpu_busca,
        "ssd": ssd_busca,
        "fonte": fonte_busca,
        "gabinete": gabinete
    }

def buscar_na_amazon(termo, preco_max):
    url = "https://amazon-data.p.rapidapi.com/search"
    querystring = {"country": "BR", "query": termo}
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": os.getenv("RAPIDAPI_HOST")
    }

    if not headers["X-RapidAPI-Key"]:
        return {"nome": termo, "erro": "❌ Chave da API não encontrada no .env"}

    try:
        r = requests.get(url, headers=headers, params=querystring)
        if r.status_code != 200:
            return {"nome": termo, "erro": f"Erro na API (status {r.status_code})"}

        for item in r.json().get("search_results", []):
            preco_str = item.get("price_str", "").replace("R$", "").replace(".", "").replace(",", ".")
            try:
                preco_float = float(preco_str)
                if preco_float <= preco_max:
                    return {
                        "nome": item.get("title"),
                        "imagem": item.get("image"),
                        "preco": item.get("price_str"),
                        "link": item.get("url") + "?tag=SEU_ID_AFILIADO"
                    }
            except:
                continue

        return {"nome": termo, "erro": f"Nenhum produto até R${preco_max:.2f}"}

    except Exception as e:
        return {"nome": termo, "erro": f"Erro: {str(e)}"}

@app.route("/montar-setup", methods=["POST"])
def montar_setup():
    dados = request.json
    preco = dados.get("preco")
    processador = dados.get("processador")
    gpu = dados.get("gpu")
    laptop = dados.get("laptop")

    if not preco or not processador or not gpu or not laptop:
        return jsonify({"erro": "Faltam dados obrigatórios"}), 400

    quer_gpu = gpu == "Sim"
    quer_laptop = "sim" in laptop.lower()
    total = get_total(preco)

    if quer_laptop:
        # 👇 Apenas notebook sugerido
        termo_busca = "Notebook gamer Ryzen 5" if processador == "AMD" else "Notebook Intel i5"
        produto = buscar_na_amazon(termo_busca, total)
        produto["componente"] = "LAPTOP"
        return jsonify([produto])

    # Monta setup com peças
    orcamento = distribuir_orcamento(total, quer_gpu)
    termos = definir_pecas_basicas(processador, quer_gpu, total)

    resultado = []
    for componente, termo in termos.items():
        preco_max = orcamento.get(componente, 0)
        produto = buscar_na_amazon(termo, preco_max)
        produto["componente"] = componente.upper()
        resultado.append(produto)

    return jsonify(resultado)

if __name__ == "__main__":
    app.run(debug=True)
