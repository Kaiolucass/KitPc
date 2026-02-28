from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import re 
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from flask import send_from_directory
import google.generativeai as genai
import json
import unicodedata
from flask import make_response
from datetime import datetime
from authlib.integrations.flask_client import OAuth
import firebase_admin
from firebase_admin import credentials
import firebase_admin.firestore as firestore
import threading

# 1. Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()



app = Flask(__name__)

@app.context_processor
def inject_firebase():
    return {
        'fb': {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID"),
            "vapidKey": os.getenv("FIREBASE_VAPID_KEY")
        }
    }

import google.generativeai as genai

# Força o uso da API v1 (Estável) em vez da v1beta
from google.generativeai.types import RequestOptions

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Configuramos o modelo
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config={"response_mime_type": "application/json"}
)


# Secret Key para sessões (Login) - Tente definir SECRET_KEY no seu .env ou Render
app.secret_key = os.getenv("SECRET_KEY", "cyber-kit-pc-token-2026")
CORS(app)

# --- CONFIGURAÇÕES DE E-MAIL---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'seu-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'sua-senha-de-app-aqui' # 16 caracteres
mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

def enviar_confirmacao(usuario_email, token):
    link = f"https://kitpc.com.br/confirmar-email/{token}"
    msg = Message('Confirme sua conta no KitPC! 🚀',
                  sender='seu-email@gmail.com',
                  recipients=[usuario_email])
    msg.body = f'Olá! Clique no link para ativar sua conta e começar a montar seu PC: {link}'
    # Se quiser deixar "profissional", use html em vez de body:
    msg.html = render_template('email_confirmacao.html', link=link)
    mail.send(msg)

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
from models import db, Processador, PlacaMae, MemoriaRAM, PlacaVideo, Armazenamento, Fonte, Gabinete, Post, Usuario, MontagemSalva, Comentario
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
        # Carrega os posts
        posts = Post.query.order_by(Post.data_postagem.desc()).limit(4).all()
        
        # Coleta os dados do .env para passar ao template
        firebase_data = {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID"),
            "vapidKey": os.getenv("FIREBASE_VAPID_KEY")
        }
    except Exception as e:
        logger.error(f"Erro na home: {e}")
        posts = []
        firebase_data = {}

    return render_template("index.html", posts=posts, fb=firebase_data)

@app.route("/seuPc")
def montagem():
    return render_template("seupc.html")

@app.route("/educacao")
def educacao():
    return render_template("educacao.html")

@app.route('/educacao/guia-de-pecas')
def guia_pecas():
    return render_template('guia_pecas.html')

@app.route('/educacao/trilha')
def trilha_montagem():
    return render_template('trilha.html')

@app.route("/sobre")
def sobre_nos():
    return render_template("sobre.html")


    # --- CONFIGURAÇÃO FIREBASE (NOTIFICAÇÕES) ---
if not firebase_admin._apps:
    try:
        # Certifique-se de que o nome do arquivo abaixo é IGUAL ao que você renomeou
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred)
        logger.info("Firebase inicializado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao carregar chave do Firebase: {e}")

db_firestore = firestore.client() 


@app.route("/inscrever", methods=["POST"])
def inscrever():
    email = request.form.get("email")
    
    if not email or "@" not in email:
        flash("Por favor, insira um e-mail válido.")
        return redirect(url_for('home'))

    try:
        # Salva na coleção 'inscritos' no Firebase
        db_firestore.collection('inscritos').add({
            'email': email,
            'data_inscricao': datetime.now(),
            'origem': 'newsletter_site'
        })
        flash("🚀 Conectado com sucesso! Você receberá as próximas notícias do nosso site.")
    except Exception as e:
        logger.error(f"Erro ao salvar e-mail no Firebase: {e}")
        flash("Erro técnico ao se inscrever. Tente novamente em instantes.")

    return redirect(url_for('home'))

 # Salva o token no Firestore para enviar notificações depois
@app.route("/salvar-token", methods=["POST"])
def salvar_token():
    try:
        dados = request.get_json()
        token = dados.get("token")
        
        if not token:
            return jsonify({"erro": "Token não fornecido"}), 400

       
        # Usamos o próprio token como ID do documento para evitar duplicatas
        db_firestore.collection('tokens_push').document(token).set({
            'token': token,
            'data_registro': datetime.now(),
            'plataforma': request.user_agent.platform or 'unknown'
        })
        
        logger.info(f"Novo token de push registrado: {token[:10]}...")
        return jsonify({"status": "sucesso", "mensagem": "Dispositivo pronto para notificações"}), 200
        
    except Exception as e:
        logger.error(f"Erro ao salvar token no Firebase: {e}")
        return jsonify({"erro": "Falha interna ao salvar dispositivo"}), 500
    
def enviar_notificacoes_async(app, post_titulo, post_slug):
    with app.app_context():
        try:
            # Pega todos os usuários que confirmaram o e-mail
            usuarios = Usuario.query.filter_by(confirmado=True).all()
            with mail.connect() as conn:
                for usuario in usuarios:
                    msg = Message(
                        f"Novo Post: {post_titulo}",
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[usuario.email]
                    )
                    msg.body = f"Confira nossa nova matéria: https://kitpc.com.br/blog/{post_slug}"
                    conn.send(msg)
            print("Notificações enviadas com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar notificações: {e}")

# --- SISTEMA DE LOGIN E CADASTRO ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        
        user = Usuario.query.filter_by(email=email).first()
        
        # 1. Verifica se o usuário existe e se a senha está correta
        if user and check_password_hash(user.senha, senha):
            
            # 2. NOVA TRAVA: Verifica se o e-mail foi confirmado
            if not user.confirmado:
                logger.warning(f"Tentativa de login: Usuário {user.email} ainda não confirmou o e-mail.")
                return render_template("login.html", erro="Sua conta ainda não foi ativada. Verifique seu e-mail!")

            # 3. Se passou em tudo, cria a sessão
            session['usuario_id'] = user.id
            session['nome'] = user.nome
            session['is_admin'] = user.is_admin
            logger.info(f"Usuário {user.nome} logado com sucesso.")
            return redirect(url_for('home'))
        
        # Se a senha estiver errada ou e-mail não existir
        return render_template("login.html", erro="E-mail ou senha incorretos!")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

 # # --- FUNÇÃO SENHA FORTE ---

def senha_forte(senha):
    if len(senha) < 8:
        return False
    if not re.search(r"[A-Z]", senha):
        return False
    if not re.search(r"[0-9]", senha):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        return False
    return True

# No config do Google:
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/login/google')
def login_google():
    # Esse é o link que o botão do Google vai chamar
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize/google')
def authorize_google():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            email_google = user_info['email']
            nome_google = user_info['name']
            
            # 1. Verifica se o usuário já existe no seu banco
            user = Usuario.query.filter_by(email=email_google).first()
            
            if not user:
                # 2. Se não existe, cria um novo (já confirmado!)
                user = Usuario(
                    nome=nome_google,
                    email=email_google,
                    senha="LOGIN_SOCIAL_GOOGLE", 
                    confirmado=True 
                )
                db.session.add(user)
                db.session.commit()
            
            # 3. Alimenta a sessão com os dados do banco
            session['usuario_id'] = user.id
            session['nome'] = user.nome
            session['is_admin'] = user.is_admin
            
            return redirect(url_for('home'))
            
    except Exception as e:
        logger.error(f"Erro no login Google: {e}")
        flash("Erro ao autenticar com o Google.")
        
    return redirect(url_for('login'))

# --- ROTAS DE CADASTRO COM VALIDAÇÃO E E-MAIL ---

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar_senha")

        # 1. Validação de senha forte
        if not senha_forte(senha):
            flash("Senha fraca! Use 8+ caracteres, maiúscula, número e símbolo.")
            return redirect(url_for('register'))

        if senha != confirmar:
            flash("As senhas não coincidem!")
            return redirect(url_for('register'))

        user_exists = Usuario.query.filter_by(email=email).first()
        if user_exists:
            flash("Este e-mail já está cadastrado.")
            return redirect(url_for('register'))

        # 2. Criando o usuário (confirmado=False por padrão)
        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(
            nome=nome, 
            email=email, 
            senha=senha_hash, 
            is_admin=False 
        )

        db.session.add(novo_usuario)
        db.session.commit()

        # 3. Gerar Token e enviar E-mail
        token = s.dumps(email, salt='email-confirm')
        link = url_for('confirmar_email', token=token, _external=True)
        
        msg = Message('Confirme seu E-mail - KitPC', recipients=[email])
        msg.body = f'Olá {nome}! Clique no link para ativar sua conta no KitPC: {link}'
        
        try:
            mail.send(msg)
            flash("Conta criada! Verifique seu e-mail para ativar.")
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
            flash("Conta criada, mas houve erro ao enviar e-mail de ativação.")

        return redirect(url_for('login'))

    return render_template("register.html")

@app.route("/confirmar-email/<token>")
def confirmar_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        user = Usuario.query.filter_by(email=email).first_or_404()
        
        user.confirmado = True 
        db.session.commit()
        
        flash("E-mail confirmado com sucesso! Agora você pode logar.")
        return redirect(url_for('login'))
    except SignatureExpired:
        return "<h1>O link expirou! Peça um novo cadastro.</h1>"
    except Exception:
        return "<h1>Token inválido ou corrompido!</h1>"
    


def enviar_notificacoes_thread(app_obj, titulo, slug):
    with app_obj.app_context():
        try:
            # Sua lógica de buscar inscritos no Firestore e enviar o e-mail aqui
            leitores = db_firestore.collection('inscritos').stream()
            lista_emails = [doc.to_dict()['email'] for doc in leitores]
            
            if lista_emails:
                with mail.connect() as conn:
                    for email_leitor in lista_emails:
                        msg = Message(
                            subject=f"📰 Matéria Nova no KitPC: {titulo}",
                            sender=app_obj.config['MAIL_USERNAME'],
                            recipients=[email_leitor]
                        )
                        url_post = f"https://kitpc.com.br/blog/{slug}"
                        msg.body = f"Olá! Acabamos de publicar uma nova matéria: {titulo}\n\nLeia em: {url_post}"
                        conn.send(msg)
        except Exception as e:
            print(f"Erro no envio background: {e}")


# --- ÁREA ADMINISTRATIVA ---

@app.route("/admin")
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    # Busca usuários e posts para alimentar as tabelas do admin.html
    usuarios_lista = Usuario.query.all()
    posts_lista = Post.query.order_by(Post.data_postagem.desc()).all()
    
    # Importante: enviamos edit_post=None para o formulário saber que é uma NOVA postagem
    return render_template("admin.html", usuarios=usuarios_lista, posts=posts_lista, edit_post=None)

@app.route("/admin/editar-post/<int:id>")
def editar_post(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    post = Post.query.get_or_404(id)
    usuarios_lista = Usuario.query.all()
    posts_lista = Post.query.order_by(Post.data_postagem.desc()).all()
    
    # Enviamos o post encontrado para o campo 'edit_post' para preencher o formulário
    return render_template("admin.html", usuarios=usuarios_lista, posts=posts_lista, edit_post=post)
@app.route("/admin/salvar-post", methods=["POST"])
@app.route("/admin/salvar-post/<int:id>", methods=["POST"])
def salvar_post(id=None):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    try:
        titulo = request.form.get("titulo")
        subtitulo = request.form.get("subtitulo")
        conteudo = request.form.get("conteudo") 
        
        if id:
            post = Post.query.get_or_404(id)
            post.titulo = titulo
            post.subtitulo = subtitulo
            post.conteudo = conteudo
        else:
            post = Post(titulo=titulo, subtitulo=subtitulo, conteudo=conteudo, views=0)
            db.session.add(post)

        file = request.files.get('arquivo_imagem') 
        if file and file.filename != '':
            upload_result = cloudinary.uploader.upload(file, folder="kitpc_blog")
            post.imagem_url = upload_result.get('secure_url')

        # Gerar Slug
        slug = unicodedata.normalize('NFKD', titulo).encode('ascii', 'ignore').decode('ascii').lower()
        slug = re.sub(r'[^\w\s-]', '', slug).strip()
        post.slug = re.sub(r'[-\s]+', '-', slug)

        db.session.commit()
        
        # --- DISPARO DE NOTIFICAÇÃO (EM SEGUNDO PLANO) ---
        if id is None: # Só envia se for post novo
            thread = threading.Thread(
                target=enviar_notificacoes_thread, 
                args=(app._get_current_object(), post.titulo, post.slug)
            )
            thread.start()

        flash("✅ Postagem publicada! As notificações estão sendo enviadas em segundo plano.")
        return redirect(url_for('admin')) 

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar post: {e}")
        flash(f"❌ Erro ao salvar: {e}")
        return redirect(url_for('admin'))
    

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar: {e}")
        return f"Erro ao salvar: {e}"

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar: {e}")
        return f"Erro ao salvar: {e}"
    
if id is None: # Post Novo
    # 1. Enviar E-mails (você já tem)
    # ... seu código de e-mail aqui ...

    # 2. ENVIAR NOTIFICAÇÃO PUSH REAL
    try:
        from firebase_admin import messaging
        
        # Busca todos os tokens salvos
        tokens_docs = db_firestore.collection('tokens_push').stream()
        lista_tokens = [doc.to_dict()['token'] for doc in tokens_docs]

        if lista_tokens:
            # Criamos a mensagem
            notificacao = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=f"📰 Novo Post: {titulo}",
                    body=subtitulo or "Confira a nova matéria no KitPC!"
                ),
                tokens=lista_tokens,
                data={"slug": post.slug} # Link para o JS abrir o post certo
            )
            # Envia para todo mundo de uma vez
            response = messaging.send_multicast(notificacao)
            logger.info(f"Push enviado para {response.success_count} dispositivos.")
    except Exception as e:
        logger.error(f"Falha ao enviar push: {e}")
    
#admin arquivar-post/
@app.route("/admin/arquivar-post/<int:id>", methods=["POST"])
def arquivar_post(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    post = Post.query.get_or_404(id)
    # Garante que a coluna arquivado existe (evita erro caso o banco não tenha sido resetado)
    post.arquivado = not getattr(post, 'arquivado', False) 
    
    db.session.commit()
    flash("Status do post atualizado!")
    return redirect(url_for('admin'))

@app.route("/admin/upload-imagem-corpo", methods=["POST"])
def upload_imagem_corpo():
    if not session.get('is_admin'):
        return jsonify({"error": "Acesso negado"}), 403
    
    file = request.files.get('image')
    if file:
        upload_result = cloudinary.uploader.upload(file, folder="kitpc_corpo_posts")
        return jsonify({"url": upload_result.get('secure_url')})
    return jsonify({"error": "Falha no upload"}), 400

@app.route("/admin/deletar-post/<int:id>", methods=["POST"])
def deletar_post(id):
    if not session.get('is_admin'):
        return "Acesso negado", 403
    
    post = Post.query.get_or_404(id)
    try:
        db.session.delete(post)
        db.session.commit()
        flash("Post removido!")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro: {e}")
    return redirect(url_for('admin'))

@app.route("/admin/confirmar-usuario/<int:id>", methods=["POST"])
def confirmar_usuario_admin(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get_or_404(id)
    usuario.confirmado = True 
    
    try:
        db.session.commit()
        flash(f"Usuário {usuario.nome} ativado manualmente!")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao ativar: {e}")
        
    return redirect(url_for('admin'))

@app.route("/admin/deletar-usuario/<int:id>", methods=["POST"])
def deletar_usuario_admin(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get_or_404(id)
    
    try:
        db.session.delete(usuario)
        db.session.commit()
        flash(f"Usuário {usuario.nome} removido!")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao deletar: {e}")
        
    return redirect(url_for('admin'))

# ---  ARQUIVOS DO BLOG ---

@app.route("/arquivo")
def arquivo():
    posts = Post.query.order_by(Post.data_postagem.desc()).all()
    return render_template("arquivo.html", posts=posts)
@app.route("/blog/<slug>")
def exibir_post(slug):
    # 1. Busca o post principal pelo slug
    post = Post.query.filter_by(slug=slug).first_or_404()
    
    # 2. Busca os 3 posts MAIS VISTOS (Populares)
    sugestoes = Post.query.filter(Post.slug != slug, Post.arquivado == False)\
                          .order_by(Post.views.desc())\
                          .limit(3).all()

    # 3. Busca os COMENTÁRIOS (Do mais novo para o mais antigo)
    # Importamos o modelo dentro da função para evitar erros de importação circular
    from models import Comentario
    comentarios = Comentario.query.filter_by(post_id=post.id)\
                                  .order_by(Comentario.data_postagem.desc())\
                                  .all()
    
    # 4. Lógica de contagem de visualizações
    if not post.views:
        post.views = 0
    post.views += 1
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Se o seu logger não estiver configurado, pode usar print(e) para testar
        print(f"Erro ao atualizar views: {e}")
        
    # 5. Enviamos tudo para o HTML (agora com a variável 'comentarios')
    return render_template("blog_post.html", 
                           post=post, 
                           sugestoes=sugestoes, 
                           comentarios=comentarios)

@app.route("/blog/comentar/<int:post_id>", methods=["POST"])
def comentar(post_id):
    # 1. Trava de segurança: Só comenta se estiver logado
    if 'usuario_id' not in session:
        flash("Você precisa estar logado para comentar!")
        return redirect(url_for('login'))
    
    conteudo = request.form.get("conteudo_comentario")
    
    # 2. Verifica se o comentário não está vazio
    if conteudo and conteudo.strip():
        try:
            novo_comentario = Comentario(
                conteudo=conteudo.strip(),
                post_id=post_id,
                usuario_id=session['usuario_id']
            )
            db.session.add(novo_comentario)
            db.session.commit()
            flash("Comentário postado com sucesso!")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao salvar comentário: {e}")
            flash("Erro ao salvar comentário. Tente novamente.")
    
    # 3. Redireciona de volta para o post (usando o slug do post)
    post = Post.query.get_or_404(post_id)
    return redirect(url_for('exibir_post', slug=post.slug))

@app.route("/excluir-comentario/<int:id>")
def excluir_comentario(id):
    if not session.get('is_admin'):
        return "Acesso negado", 403
    
    from models import Comentario
    comentario = Comentario.query.get_or_404(id)
    post_slug = comentario.post_rel.slug # Pega o slug para voltar para a mesma página
    
    db.session.delete(comentario)
    db.session.commit()
    return redirect(url_for('exibir_post', slug=post_slug))

# --- LÓGICA DO MONTADOR E SETUP BANCO MANTIDOS COMO ESTÃO ---

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
        # O db.create_all() APENAS cria o que não existe. 
        # Como as outras tabelas já existem, ele vai criar só a de Comentario.
        db.create_all()
        
        return "✅ Sucesso: Novas tabelas (Comentários) criadas sem apagar os dados antigos!"
    except Exception as e:
        db.session.rollback()
        return f"❌ Erro ao atualizar banco: {e}"
    
@app.route("/consultoria-ia", methods=["POST"])
def consultoria_ia():
    dados = request.json
    
    # 1. Pegamos todas as peças do seu banco para a IA não inventar modelos que você não tem
    cpus = [p.nome for p in Processador.query.all()]
    gpus = [g.nome for g in PlacaVideo.query.all()]
    mobos = [m.nome for m in PlacaMae.query.all()]
    
    # 2. Criamos um "Contexto" para a IA
    prompt = f"""
    Você é o Engenheiro de Hardware do KitPC. 
    OBJETIVO: Montar o melhor PC possível para o usuário.
    
    DADOS DO USUÁRIO:
    - Orçamento: R$ {dados['preco']}
    - Uso: {dados['uso']} (Estilo: {dados['tipo']})
    - Precisa de GPU: {dados['gpu']}
    
    PEÇAS DISPONÍVEIS NO MEU BANCO (Escolha APENAS desta lista):
    - Processadores: {", ".join(cpus)}
    - Placas-mãe: {", ".join(mobos)}
    - Placas de Vídeo: {", ".join(gpus)}
    
    REGRAS DE OURO:
    1. O socket do Processador DEVE ser compatível com a Placa-mãe.
    2. O valor total somado das peças deve respeitar o orçamento.
    3. Se o usuário quer jogar, foque mais orçamento na GPU.
    
    RETORNE ESTRITAMENTE UM JSON:
    {{
        "setup": [
            {{"componente": "Processador", "nome": "NOME_EXATO_DA_LISTA", "justificativa": "Por que escolheu essa?"}},
            {{"componente": "Placa-mãe", "nome": "NOME_EXATO_DA_LISTA", "justificativa": "Compatibilidade com o socket"}},
            {{"componente": "Placa de Vídeo", "nome": "NOME_EXATO_DA_LISTA", "justificativa": "Performance em jogos"}}
        ],
        "total_estimado": "R$ X.XXX",
        "conselho_mestre": "Dica rápida de upgrade futuro."
    }}
    """

    try:
        response = model.generate_content(prompt)
        ia_data = json.loads(re.search(r'\{.*\}', response.text, re.DOTALL).group())

        # 3. Agora buscamos as imagens e links REAIS no banco para cada peça que a IA escolheu
        for item in ia_data['setup']:
            peca_real = None
            if item['componente'] == "Processador":
                peca_real = Processador.query.filter_by(nome=item['nome']).first()
            elif item['componente'] == "Placa-mãe":
                peca_real = PlacaMae.query.filter_by(nome=item['nome']).first()
            elif item['componente'] == "Placa de Vídeo":
                peca_real = PlacaVideo.query.filter_by(nome=item['nome']).first()
            
            if peca_real:
                item['imagem_url'] = peca_real.imagem_url
                item['link_loja'] = peca_real.link_loja
                item['preco'] = float(peca_real.preco)

        return jsonify(ia_data)

    except Exception as e:
        logger.error(f"Erro na Consultoria IA: {e}")
        return jsonify({"erro": "A IA se confundiu nos cabos. Tente novamente!"}), 500
    
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    try:
        pages = []
        now = datetime.now().strftime('%Y-%m-%d')
        
        # Lista de rotas que o Google NÃO deve indexar
        rotas_bloqueadas = [
            '/admin', 
            '/logout', 
            '/setup-db-kaio', 
            '/login', 
            '/register', 
            '/confirmar-email',
            '/health',
            '/sitemap.xml'
        ]

        # 1. Páginas Estáticas (Filtradas)
        for rule in app.url_map.iter_rules():
            # Filtra apenas métodos GET, sem argumentos extras e que não estejam na lista de bloqueio
            if "GET" in rule.methods and len(rule.arguments) == 0:
                url_path = str(rule.rule)
                
                # Verifica se a URL começa com algum item da lista de bloqueados
                if not any(url_path.startswith(bloqueada) for bloqueada in rotas_bloqueadas):
                    pages.append([f"https://kitpc.com.br{url_path}", now])

        # 2. Páginas Dinâmicas (Posts do Blog)
        posts = Post.query.filter_by(arquivado=False).all() # Só adiciona o que não estiver arquivado
        for post in posts:
            url = f"https://kitpc.com.br/blog/{post.slug}"
            pages.append([url, now])

        sitemap_xml = render_template('sitemap_template.xml', pages=pages)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
    except Exception as e:
        logger.error(f"Erro ao gerar sitemap: {e}")
        return str(e)
    

@app.route("/privacidade")
def privacidade():
    return render_template("privacidade.html")

@app.route("/termos")
def termos():
    return render_template("termos.html")

@app.route('/robots.txt')
def robots_txt():
    conteudo = "User-agent: *\nDisallow: /admin\nDisallow: /setup-db-kaio\nSitemap: https://kitpc.com.br/sitemap.xml"
    return conteudo, 200, {'Content-Type': 'text/plain'}

@app.route("/health")
def health(): return "OK", 200

@app.route('/ping')
def ping():
    return "KitPC Online!", 200

@app.route('/ads.txt')
def ads_txt():
    conteudo = "google.com, pub-3396569889908907, DIRECT, f08c47fec0942fa0"
    return conteudo, 200, {'Content-Type': 'text/plain'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)