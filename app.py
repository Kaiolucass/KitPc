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

# --- Buscas em lojas ---

def buscar_na_amazon(termo, preco_max):
    url = "https://amazon-data.p.rapidapi.com/search"
    querystring = {"country": "BR", "query": termo}
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": os.getenv("RAPIDAPI_HOST")
    }

    try:
        r = requests.get(url, headers=headers, params=querystring)
        for item in r.json().get("search_results", []):
            preco_str = item.get("price_str", "").replace("R$", "").replace(".", "").replace(",", ".")
            preco = float(preco_str)
            if preco <= preco_max:
                return {
                    "nome": item.get("title"),
                    "imagem": item.get("image"),
                    "preco": item.get("price_str"),
                    "link": item.get("url"),
                    "loja": "Amazon"
                }
    except:
        pass
    return None

def buscar_no_mercado_livre(termo, preco_max):
    try:
        res = requests.get(f"https://api.mercadolibre.com/sites/MLB/search?q={termo}&limit=10")
        for item in res.json().get("results", []):
            preco = item.get("price")
            if preco <= preco_max:
                return {
                    "nome": item.get("title"),
                    "imagem": item.get("thumbnail"),
                    "preco": f"R$ {preco:.2f}",
                    "link": item.get("permalink"),
                    "loja": "Mercado Livre"
                }
    except:
        pass
    return None

def buscar_na_kabum(termo):
    termo_formatado = termo.replace(" ", "+")
    return {
        "nome": f"Buscar {termo} na Kabum",
        "imagem": "https://upload.wikimedia.org/wikipedia/commons/8/89/Logo_Kabum_2021.png",
        "preco": "Ver site",
        "link": f"https://www.kabum.com.br/busca/{termo_formatado}",
        "loja": "Kabum"
    }

def comparar_precos(termo, preco_max):
    resultados = []

    for func in [buscar_na_amazon, buscar_no_mercado_livre]:
        resultado = func(termo, preco_max)
        if resultado:
            resultados.append(resultado)

    if resultados:
        melhores = sorted(resultados, key=lambda x: float(x["preco"].replace("R$", "").replace(",", ".")))
        return melhores[0]

    return buscar_na_kabum(termo)

# --- Endpoint principal ---
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
        termo_busca = "Notebook gamer Ryzen 5" if processador == "AMD" else "Notebook Intel i5"
        produto = comparar_precos(termo_busca, total)
        produto["componente"] = "LAPTOP"
        return jsonify([produto])

    orcamento = distribuir_orcamento(total, quer_gpu)
    termos = definir_pecas_basicas(processador, quer_gpu, total)

    resultado = []
    for componente, termo in termos.items():
        preco_max = orcamento.get(componente, 0)
        produto = comparar_precos(termo, preco_max)
        produto["componente"] = componente.upper()
        resultado.append(produto)

    return jsonify(resultado)

if __name__ == "__main__":
    app.run(debug=True)