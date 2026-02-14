from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import re # Para limpar o slug

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

# 3. Inicialização do Banco
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
        # Buscamos 4 posts: 1 para o destaque e 3 para a grade inferior
        posts = Post.query.order_by(Post.data_postagem.desc()).limit(4).all()
    except Exception as e:
        logger.error(f"Erro na home: {e}")
        posts = []
    return render_template("index.html", posts=posts)

# Rota para abrir o post completo
@app.route("/blog/<slug>")
def exibir_post(slug):
    try:
        post = Post.query.filter_by(slug=slug).first_or_404()
        return render_template("blog_post.html", post=post)
    except Exception as e:
        logger.error(f"Erro ao carregar post {slug}: {e}")
        return redirect(url_for('home'))

@app.route("/admin")
def pagina_admin():
    return render_template("admin.html")

@app.route("/admin/salvar-post", methods=["POST"])
def salvar_post():
    try:
        titulo = request.form.get("titulo")
        subtitulo = request.form.get("subtitulo")
        conteudo = request.form.get("conteudo")
        imagem_url = request.form.get("imagem_url")
        
        # Gerador de Slug mais robusto (remove acentos e símbolos)
        slug = titulo.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug).strip('-')

        novo_post = Post(
            titulo=titulo,
            subtitulo=subtitulo,
            conteudo=conteudo,
            imagem_url=imagem_url,
            slug=slug
        )

        db.session.add(novo_post)
        db.session.commit()
        return "✅ Post publicado com sucesso! <a href='/'>Voltar para Home</a>"
    
    except Exception as e:
        db.session.rollback()
        return f"❌ Erro ao salvar: {e}"

@app.route("/seuPc")
def montagem():
    return render_template("seupc.html")

@app.route("/educacao")
def educacao():
    return render_template("educacao.html")

@app.route("/sobre")
def sobre_nos():
    return render_template("sobre.html")

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
        resultado = []
        for comp, valor in orcamento.items():
            if valor > 0:
                p = comparar_precos("", valor)
                if p: resultado.append(p)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# --- SETUP DO BANCO ---

@app.route("/setup-db-kaio")
def setup_db_kaio():
    try:
        db.create_all()
        if not Post.query.first():
            post = Post(
                titulo="Como escolher as peças do seu PC em 2026",
                subtitulo="Um guia prático para não errar na montagem.",
                conteudo="Montar um PC exige atenção aos detalhes...",
                imagem_url="https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?q=80&w=1000&auto=format&fit=crop",
                slug="guia-montagem-2026"
            )
            db.session.add(post)
        db.session.commit()
        return jsonify({"status": "Sucesso", "mensagem": "Sistema de Blog pronto!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500

@app.route("/health")
def health(): return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)