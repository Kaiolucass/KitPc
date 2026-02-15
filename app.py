from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import re 
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash

# 1. Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
# Secret Key para sessões (Login) - Tente definir SECRET_KEY no seu .env ou Render
app.secret_key = os.getenv("SECRET_KEY", "cyber-kit-pc-token-2026")
CORS(app)

# 2. Configuração do Banco de Dados
def get_cleaned_db_uri():
    uri = os.getenv("DATABASE_URL")
    if not uri:
        logger.error("DATABASE_URL não definida!")
        return None
    if uri.startswith("mysql://"):
        uri = uri.replace("mysql://", "mysql+pymysql://", 1)
    return uri.strip()

db_uri = get_cleaned_db_uri() or "sqlite:///local_test.db"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Inicialização do Banco (Importando todas as classes do models.py)
from models import db, Processador, PlacaMae, MemoriaRAM, PlacaVideo, Armazenamento, Fonte, Gabinete, Post, Usuario, MontagemSalva
db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        logger.info("Banco de dados sincronizado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e}")

# --- ROTAS DE NAVEGAÇÃO ---

@app.route("/")
def home():
    try:
        # Carrega os 4 posts mais recentes para a Home (Destaque + 3 cards)
        posts = Post.query.order_by(Post.data_postagem.desc()).limit(4).all()
    except Exception as e:
        logger.error(f"Erro na home: {e}")
        posts = []
    return render_template("index.html", posts=posts)

@app.route("/blog/<slug>")
def exibir_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template("blog_post.html", post=post)

@app.route("/seuPc")
def montagem():
    return render_template("seupc.html")

@app.route("/educacao")
def educacao():
    return render_template("educacao.html")

@app.route("/sobre")
def sobre_nos():
    return render_template("sobre.html")

# --- SISTEMA DE LOGIN E CADASTRO ---

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar_senha")

        # Verificações básicas
        if senha != confirmar:
            flash("As senhas não coincidem!")
            return redirect(url_for('register'))

        user_exists = Usuario.query.filter_by(email=email).first()
        if user_exists:
            flash("Este e-mail já está cadastrado.")
            return redirect(url_for('register'))

        # Criando o usuário comum
        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(
            nome=nome, 
            email=email, 
            senha=senha_hash, 
            is_admin=False # Usuário normal
        )

        db.session.add(novo_usuario)
        db.session.commit()
        
        flash("Conta criada com sucesso! Faça login.")
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        
        user = Usuario.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.senha, senha):
            session['usuario_id'] = user.id
            session['nome'] = user.nome
            session['is_admin'] = user.is_admin
            logger.info(f"Usuário {user.nome} logado.")
            return redirect(url_for('home'))
        
        return render_template("login.html", erro="Credenciais inválidas!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

# Rota Especial para Criar o seu Admin (Use uma única vez e apague se quiser)
@app.route("/registrar-kaio-admin", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        
        if Usuario.query.filter_by(email=email).first():
            return "Este email já existe!"
            
        senha_hash = generate_password_hash(senha)
        novo_admin = Usuario(nome=nome, email=email, senha=senha_hash, is_admin=True)
        
        db.session.add(novo_admin)
        db.session.commit()
        return "✅ Admin criado! Agora faça <a href='/login'>Login</a>."
    
    return '''
        <form method="post" style="padding:50px; background:#05001C; color:#3CC9E4;">
            <h2>Cadastro Admin Secreto</h2>
            <input name="nome" placeholder="Seu Nome" required><br><br>
            <input name="email" placeholder="Email" required><br><br>
            <input name="senha" type="password" placeholder="Senha Forte" required><br><br>
            <button type="submit">Cadastrar Admin</button>
        </form>
    '''

# --- ÁREA ADMINISTRATIVA ---

@app.route("/admin")
def pagina_admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    return render_template("admin.html")

@app.route("/admin/salvar-post", methods=["POST"])
def salvar_post():
    if not session.get('is_admin'): return "Acesso negado", 403
    try:
        titulo = request.form.get("titulo")
        subtitulo = request.form.get("subtitulo")
        conteudo = request.form.get("conteudo")
        imagem_url = request.form.get("imagem_url")
        
        # Gera slug limpo: "PC Gamer 2026!" -> "pc-gamer-2026"
        slug = titulo.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug).strip('-')

        novo_post = Post(titulo=titulo, subtitulo=subtitulo, conteudo=conteudo, imagem_url=imagem_url, slug=slug)
        db.session.add(novo_post)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        return f"Erro: {e}"


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