from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

# 1. Configuração de Logging
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
        logger.error("DATABASE_URL não está definida!")
        return None
    if uri.startswith("mysql://"):
        uri = uri.replace("mysql://", "mysql+pymysql://", 1)
    return uri.strip()

db_uri = get_cleaned_db_uri() or "sqlite:///local_test.db"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Inicialização do Banco (Importando Post)
from models import db, Processador, PlacaMae, MemoriaRAM, PlacaVideo, Armazenamento, Fonte, Gabinete, Post
db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        logger.info("Banco de dados sincronizado.")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e}")

# --- ROTAS DE PÁGINAS ---

@app.route("/")
def home():
    try:
        # Pega os 3 posts mais recentes para mostrar na Home
        posts = Post.query.order_by(Post.data_postagem.desc()).limit(3).all()
    except:
        posts = []
    return render_template("index.html", posts=posts)

@app.route("/seuPc")
def montagem():
    return render_template("seupc.html")

@app.route("/educacao")
def educacao():
    return render_template("educacao.html")

@app.route("/sobre")
def sobre_nos():
    return render_template("sobre.html")

@app.route("/blog")
def blog_lista():
    try:
        posts = Post.query.order_by(Post.data_postagem.desc()).all()
    except:
        posts = []
    return render_template("blog.html", posts=posts)

# --- LÓGICA DO MONTADOR ---

def get_total(preco_label):
    precos = {"Um PC OK": 2000, "Um PC BOM": 3000, "Um PC MUITO BOM": 5000, "Até a NASA quer": 10000}
    return precos.get(preco_label, 2000)

def distribuir_orcamento(total, quer_gpu):
    if quer_gpu:
        return {"cpu": total*0.22, "placa_mae": total*0.12, "ram": total*0.12, "gpu": total*0.30, "ssd": total*0.10, "fonte": total*0.08, "gabinete": total*0.06}
    return {"cpu": total*0.40, "placa_mae": total*0.15, "ram": total*0.15, "gpu": 0, "ssd": total*0.15, "fonte": total*0.10, "gabinete": total*0.05}

def comparar_precos(termo, preco_max):
    tabelas = [Processador, PlacaMae, MemoriaRAM, PlacaVideo, Armazenamento, Fonte, Gabinete]
    for tabela in tabelas:
        res = tabela.query.filter(tabela.nome.ilike(f"%{termo}%")).filter(tabela.preco <= preco_max).order_by(tabela.preco.desc()).first()
        if res:
            return {"nome": res.nome, "imagem": res.imagem_url, "preco": float(res.preco), "link": res.link_loja, "componente": tabela.__tablename__.upper()}
    return None

@app.route("/montar-setup", methods=["POST"])
def montar_setup():
    try:
        dados = request.get_json(force=True)
        total = get_total(dados.get("preco"))
        gpu = dados.get("gpu") == "Sim"
        orcamento = distribuir_orcamento(total, gpu)
        # Busca simplificada
        resultado = []
        for comp, valor in orcamento.items():
            if valor > 0:
                p = comparar_precos("", valor) # Busca o melhor que couber
                if p: resultado.append(p)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# --- SETUP DO BANCO (AIVEN) ---

@app.route("/setup-db-kaio")
def setup_db_kaio():
    try:
        db.create_all()
        
        # 1. Criar Post de Teste se não existir
        if not Post.query.first():
            post = Post(
                titulo="Como escolher as peças do seu PC em 2026",
                subtitulo="Um guia prático para não errar na montagem.",
                conteudo="Escreva aqui o seu artigo completo sobre hardware...",
                imagem_url="https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?q=80&w=1000&auto=format&fit=crop",
                slug="guia-montagem-2026"
            )
            db.session.add(post)

        # 2. Criar Peças se não existir
        if not Processador.query.first():
            pecas = [
                Processador(nome="AMD Ryzen 5 5600", preco=850.00, imagem_url="https://m.media-amazon.com/images/I/51uU8pIeLGL._AC_SX679_.jpg", link_loja="#"),
                PlacaMae(nome="Placa Mãe B450M", preco=450.00, imagem_url="https://m.media-amazon.com/images/I/71R2oI8pGLL._AC_SX679_.jpg", link_loja="#"),
                MemoriaRAM(nome="RAM DDR4 8GB", preco=150.00, imagem_url="https://m.media-amazon.com/images/I/61k47n558xL._AC_SX679_.jpg", link_loja="#"),
                PlacaVideo(nome="RTX 3060", preco=1800.00, imagem_url="https://m.media-amazon.com/images/I/71f-n0pP0FL._AC_SX679_.jpg", link_loja="#"),
                Armazenamento(nome="SSD 480GB", preco=200.00, imagem_url="https://m.media-amazon.com/images/I/51IUn6L-fVL._AC_SX679_.jpg", link_loja="#"),
                Fonte(nome="Fonte 600W", preco=300.00, imagem_url="https://m.media-amazon.com/images/I/61k47n558xL._AC_SX679_.jpg", link_loja="#"),
                Gabinete(nome="Gabinete RGB", preco=250.00, imagem_url="https://m.media-amazon.com/images/I/61k47n558xL._AC_SX679_.jpg", link_loja="#")
            ]
            db.session.add_all(pecas)
        
        db.session.commit()
        return jsonify({"status": "Sucesso", "mensagem": "Blog e Peças configurados!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500

@app.route("/health")
def health(): return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)