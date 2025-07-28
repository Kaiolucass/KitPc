from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

# Logger configurado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis do .env
load_dotenv()

# Inicializa o app
app = Flask(__name__)
CORS(app)

# Verificar e limpar variáveis de ambiente para garantir que não tenham espaços ou caracteres estranhos
def get_env_var(key):
    value = os.getenv(key)
    if value:
        return value.strip()
    else:
        logger.warning(f"Variável de ambiente {key} não encontrada!")
        return ""

db_uri = os.getenv("DATABASE_URL")

db_uri = os.getenv("DATABASE_URL")

if not db_uri:
    logger.error("DATABASE_URL não está definida!")
    raise RuntimeError("DATABASE_URL ausente.")

logger.info(f"DB URI usada: {db_uri}")


app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importa os modelos e inicializa o SQLAlchemy
from models import db, Processador, PlacaMae, MemoriaRAM, PlacaVideo, Armazenamento, Fonte, Gabinete
db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/seuPc")
def montagem():
    return render_template("seupc.html")

@app.route("/educacao")
def educacao():
    return render_template("educacao.html")

@app.route("/sobre")
def sobre_nos():
    return render_template("sobre.html")

def get_total(preco_label):
    return {
        "Um PC OK": 2000,
        "Um PC BOM": 3000,
        "Um PC MUITO BOM": 5000,
        "Até a NASA quer": 99999
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

def comparar_precos(termo, preco_max):
    tabelas = [Processador, PlacaMae, MemoriaRAM, PlacaVideo, Armazenamento, Fonte, Gabinete]

    for tabela in tabelas:
        resultado = (
            tabela.query
            .filter(tabela.nome.ilike(f"%{termo}%"))
            .filter(tabela.preco <= preco_max)
            .order_by(tabela.preco.asc())
            .first()
        )
        if resultado:
            return {
                "nome": resultado.nome,
                "imagem": resultado.imagem_url,
                "preco": float(resultado.preco),
                "link": resultado.link_loja,
                "componente": tabela.__tablename__
            }

    return None

@app.route("/montar-setup", methods=["POST"])
def montar_setup():
    try:
        dados = request.get_json(force=True)
    except Exception as e:
        logger.error(f"Erro ao ler JSON: {e}")
        return jsonify({"erro": "Requisição inválida."}), 400

    preco = dados.get("preco")
    processador = dados.get("processador")
    gpu = dados.get("gpu")
    laptop = dados.get("laptop")

    if not preco or not processador or not gpu or not laptop:
        return jsonify({"erro": "Faltam dados obrigatórios."}), 400

    quer_gpu = gpu == "Sim"
    quer_laptop = "sim" in laptop.lower()
    total = get_total(preco)

    if quer_laptop:
        termo_busca = "Notebook gamer Ryzen 5" if processador == "AMD" else "Notebook Intel i5"
        produto = comparar_precos(termo_busca, total)
        if produto is None:
            produto = {
                "nome": termo_busca,
                "imagem": None,
                "preco": None,
                "link": None,
                "loja": None,
                "erro": "Produto não encontrado"
            }
        produto["componente"] = "LAPTOP"
        return jsonify([produto])

    orcamento = distribuir_orcamento(total, quer_gpu)
    termos = definir_pecas_basicas(processador, quer_gpu, total)

    resultado = []
    for componente, termo in termos.items():
        preco_max = orcamento.get(componente, 0)
        produto = comparar_precos(termo, preco_max)
        if produto is None:
            produto = {
                "nome": termo,
                "imagem": None,
                "preco": None,
                "link": None,
                "loja": None,
                "erro": "Produto não encontrado dentro do orçamento"
            }
        produto["componente"] = componente.upper()
        resultado.append(produto)

    return jsonify(resultado)


if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            logger.info("Tabelas criadas com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
    app.run(host="0.0.0.0", port=5000, debug=False)
