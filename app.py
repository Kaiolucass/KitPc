from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

# 1. Configuração de Logging (Melhorado para produção)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app)

# 2. Tratamento Robusto da DATABASE_URL
def get_cleaned_db_uri():
    uri = os.getenv("DATABASE_URL")
    if not uri:
        logger.error("DATABASE_URL não está definida nas variáveis de ambiente!")
        return None
    
    # O Aiven fornece 'mysql://', mas o SQLAlchemy precisa de 'mysql+pymysql://'
    if uri.startswith("mysql://"):
        uri = uri.replace("mysql://", "mysql+pymysql://", 1)
    
    return uri.strip()

db_uri = get_cleaned_db_uri()

if not db_uri:
    # Se estiver local e sem .env, ele tenta um sqlite básico para não crashar o VS Code
    db_uri = "sqlite:///local_test.db"
    logger.warning("Usando SQLite local porque DATABASE_URL não foi encontrada.")

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Inicialização do Banco
# Importante: Importar os modelos ANTES do db.create_all()
from models import db, Processador, PlacaMae, MemoriaRAM, PlacaVideo, Armazenamento, Fonte, Gabinete
db.init_app(app)

# Criar tabelas automaticamente (Funciona no Render com Gunicorn)
with app.app_context():
    try:
        db.create_all()
        logger.info("Banco de dados verificado/criado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco: {e}")

# --- ROTAS ---

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

# --- LÓGICA DE NEGÓCIO ---

def get_total(preco_label):
    precos = {
        "Um PC OK": 2000,
        "Um PC BOM": 3000,
        "Um PC MUITO BOM": 5000,
        "Até a NASA quer": 10000
    }
    return precos.get(preco_label, 2000)

def distribuir_orcamento(total, quer_gpu):
    if quer_gpu:
        return {
            "cpu": total * 0.22,
            "placa_mae": total * 0.12,
            "ram": total * 0.12,
            "gpu": total * 0.30,
            "ssd": total * 0.10,
            "fonte": total * 0.08,
            "gabinete": total * 0.06
        }
    return {
        "cpu": total * 0.40,
        "placa_mae": total * 0.15,
        "ram": total * 0.15,
        "gpu": 0,
        "ssd": total * 0.15,
        "fonte": total * 0.10,
        "gabinete": total * 0.05
    }

def definir_pecas_basicas(processador, quer_gpu, total):
    # Lógica simplificada para busca
    if processador == "AMD":
        cpu_busca = "Ryzen 5 5600G" if not quer_gpu else "Ryzen 5 5600"
        placa_mae_busca = "B450"
    else:
        cpu_busca = "i5 10400" if not quer_gpu else "i5 11400F"
        placa_mae_busca = "B460"

    return {
        "cpu": cpu_busca,
        "placa_mae": placa_mae_busca,
        "ram": "DDR4",
        "gpu": "RTX" if quer_gpu else "Vídeo Integrado",
        "ssd": "SSD",
        "fonte": "600W" if quer_gpu else "450W",
        "gabinete": "Gabinete"
    }

def comparar_precos(termo, preco_max):
    tabelas = [Processador, PlacaMae, MemoriaRAM, PlacaVideo, Armazenamento, Fonte, Gabinete]
    
    for tabela in tabelas:
        # Busca case-insensitive no MySQL do Aiven
        resultado = (
            tabela.query
            .filter(tabela.nome.ilike(f"%{termo}%"))
            .filter(tabela.preco <= preco_max)
            .order_by(tabela.preco.desc()) # Pega o melhor dentro do orçamento
            .first()
        )
        if resultado:
            return {
                "nome": resultado.nome,
                "imagem": resultado.imagem_url,
                "preco": float(resultado.preco),
                "link": resultado.link_loja,
                "componente": tabela.__tablename__.upper()
            }
    return None

@app.route("/montar-setup", methods=["POST"])
def montar_setup():
    try:
        dados = request.get_json(force=True)
        
        preco_label = dados.get("preco")
        processador = dados.get("processador")
        gpu = dados.get("gpu") == "Sim"
        
        total = get_total(preco_label)
        orcamento = distribuir_orcamento(total, gpu)
        termos = definir_pecas_basicas(processador, gpu, total)

        resultado = []
        for componente, termo in termos.items():
            if componente == "gpu" and not gpu: continue
            
            preco_max = orcamento.get(componente, 0)
            produto = comparar_precos(termo, preco_max)
            
            if produto:
                resultado.append(produto)
            else:
                resultado.append({
                    "nome": f"{termo} (Não encontrado no orçamento)",
                    "imagem": None,
                    "preco": preco_max,
                    "link": "#",
                    "componente": componente.upper(),
                    "aviso": "Tente aumentar o orçamento"
                })

        return jsonify(resultado)

    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/setup-db-kaio")
def setup_db_kaio():
    try:
        # 1. Garantir que as tabelas existam
        db.create_all()

        # 2. Verificar se já existem dados (evita duplicar no Aiven)
        if Processador.query.first():
            return jsonify({"status": "Aviso", "mensagem": "O banco já possui dados."}), 200

        # 3. Criar uma lista de peças iniciais (O recheio do site!)
        pecas = [
            # PROCESSADORES
            Processador(nome="AMD Ryzen 5 5600", preco=850.00, imagem_url="https://m.media-amazon.com/images/I/51uU8pIeLGL._AC_SX679_.jpg", link_loja="https://amzn.to/exemplo1"),
            Processador(nome="AMD Ryzen i5 10400", preco=600.00, imagem_url="https://m.media-amazon.com/images/I/41-i2N8lYkL._AC_SX679_.jpg", link_loja="https://amzn.to/exemplo2"),
            
            # PLACAS MÃE
            PlacaMae(nome="Placa Mãe B450M", preco=450.00, imagem_url="https://m.media-amazon.com/images/I/71R2oI8pGLL._AC_SX679_.jpg", link_loja="https://amzn.to/exemplo3"),
            PlacaMae(nome="Placa Mãe B460M", preco=550.00, imagem_url="https://m.media-amazon.com/images/I/71R2oI8pGLL._AC_SX679_.jpg", link_loja="https://amzn.to/exemplo4"),

            # MEMÓRIA RAM (DDR4)
            MemoriaRAM(nome="Memória RAM DDR4 8GB 3200MHz", preco=150.00, imagem_url="https://m.media-amazon.com/images/I/61k47n558xL._AC_SX679_.jpg", link_loja="https://amzn.to/exemplo5"),

            # PLACA DE VÍDEO
            PlacaVideo(nome="Placa de Vídeo RTX 3060", preco=1800.00, imagem_url="https://m.media-amazon.com/images/I/71f-n0pP0FL._AC_SX679_.jpg", link_loja="https://amzn.to/exemplo6"),

            # ARMAZENAMENTO (SSD)
            Armazenamento(nome="SSD Kingston 480GB", preco=200.00, imagem_url="https://m.media-amazon.com/images/I/51IUn6L-fVL._AC_SX679_.jpg", link_loja="https://amzn.to/exemplo7"),

            # FONTE
            Fonte(nome="Fonte 600W 80 Plus", preco=300.00, imagem_url="https://m.media-amazon.com/images/I/61k47n558xL._AC_SX679_.jpg", link_loja="https://amzn.to/exemplo8"),

            # GABINETE
            Gabinete(nome="Gabinete Gamer RGB", preco=250.00, imagem_url="https://m.media-amazon.com/images/I/61k47n558xL._AC_SX679_.jpg", link_loja="https://amzn.to/exemplo9"),
        ]

        # 4. Adicionar tudo ao banco Aiven
        db.session.add_all(pecas)
        db.session.commit()

        logger.info("Setup concluído: Banco de dados populado com sucesso!")
        return jsonify({"status": "Sucesso", "mensagem": "Banco Aiven populado para o 8º semestre!"}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro no setup: {e}")
        return jsonify({"status": "Erro", "detalhes": str(e)}), 500

# Rota de Saúde para o Render/Cloudflare
@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    # Localmente rodamos com debug
    app.run(host="0.0.0.0", port=5000, debug=True)