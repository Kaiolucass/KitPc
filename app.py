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
from fpdf import FPDF
from flask import send_file, request, jsonify
import io
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect


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
# Ativa a armadura de cabeçalhos (Talisman)
Talisman(
    app,
    force_https=is_prod,
    content_security_policy={
        'default-src': '\'self\'',
        'script-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            '\'unsafe-eval\'', # ALGUNS EDITORES PRECISAM DISSO
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
            'https://code.jquery.com',
            'https://pagead2.googlesyndication.com',
            'https://www.gstatic.com',
            'https://vlibras.gov.br'
        ],
        'style-src': [
            '\'self\'',
            '\'unsafe-inline\'', 
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
            'https://fonts.googleapis.com'
        ],
        'img-src': [
            '\'self\'', 
            'data:',  # PERMITE IMAGENS EM BASE64
            'blob:',  # PERMITE PRÉVIAS DE EDITORES (BLOB)
            'https://*', 
            'https://res.cloudinary.com'
        ],
        'font-src': ['\'self\'', 'https://fonts.gstatic.com', 'https://cdnjs.cloudflare.com'],
        'connect-src': [
            '\'self\'', 
            'https://fcmregistrations.googleapis.com',
            'https://firebaseinstallations.googleapis.com',
            'https://*.firebaseio.com',
            'https://res.cloudinary.com' # Importante caso você use upload via JS
        ],
        'frame-src': ['\'self\'', 'https://googleads.g.doubleclick.net', 'https://www.google.com'],
    }
)

# Ativa a proteção contra sequestro de formulários (SeaSurf)
csrf = CSRFProtect(app)

# IA do gemini para ajudar no montador
import google.generativeai as genai

# Força o uso da API v1 (Estável) em vez da v1beta
from google.generativeai.types import RequestOptions

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Configuramos o modelo
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash'
)


# Secret Key para sessões (Login) - Tente definir SECRET_KEY no seu .env ou Render
app.secret_key = os.getenv("SECRET_KEY", "cyber-kit-pc-token-2026")
CORS(app)

# --- CONFIGURAÇÕES DE E-MAIL---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

# email de confirmaçao
def send_async_email(app_obj, msg):
    with app_obj.app_context():
        try:
            mail.send(msg)
            logger.info("E-mail de confirmação enviado com sucesso!")
        except Exception as e:
            logger.error(f"Erro no envio de e-mail background: {e}")

def enviar_confirmacao(usuario_email, token, usuario_nome):
    # Geramos o link
    link = url_for('confirmar_email', token=token, _external=True)
    
    # Criamos a mensagem
    msg = Message('Confirme sua conta no KitPC! 🚀',
                  sender=app.config['MAIL_USERNAME'], 
                  recipients=[usuario_email])
    
    msg.body = f'Olá {usuario_nome}! Clique no link para ativar sua conta: {link}'
    msg.html = render_template('email_confirmacao.html', link=link, nome=usuario_nome)
    
    # DISPARO ASSÍNCRONO
    thread = threading.Thread(target=send_async_email, args=(app._get_current_object(), msg))
    thread.start()


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
from models import MensagemContato, db, Processador, PlacaMae, MemoriaRAM, PlacaVideo, Armazenamento, Fonte, Gabinete, Post, Usuario, MontagemSalva, Comentario,Notebook
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
        token_recebido = dados.get("token")
        
        if not token_recebido:
            return jsonify({"erro": "Token não fornecido"}), 400

        # --- 1. SALVAR NO SQL (Banco de Dados local/Render) ---
        from models import PushToken
        try:
            existe_sql = PushToken.query.filter_by(token_valor=token_recebido).first()
            if not existe_sql:
                # Tenta pegar o ID do usuário da sessão se estiver logado
                u_id = session.get('usuario_id') 
                novo_token_sql = PushToken(token_valor=token_recebido, usuario_id=u_id)
                db.session.add(novo_token_sql)
                db.session.commit()
                logger.info("✅ Token registrado no SQL.")
        except Exception as sql_err:
            logger.error(f"Erro ao salvar no SQL (talvez tabela não exista): {sql_err}")
            # Não paramos o código aqui para tentar salvar no Firebase ao menos

        # --- 2. SALVAR NO FIRESTORE (Firebase Cloud) ---
        db_firestore.collection('tokens_push').document(token_recebido).set({
            'token': token_recebido,
            'data_registro': datetime.now(),
            'plataforma': request.user_agent.platform or 'unknown'
        })
        
        logger.info(f"🚀 Token registrado no Firestore: {token_recebido[:10]}...")
        return jsonify({"status": "sucesso", "mensagem": "Dispositivo pronto!"}), 200
        
    except Exception as e:
        logger.error(f"Erro geral no salvar_token: {e}")
        return jsonify({"erro": "Falha interna"}), 500
    
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

#       3. Gerar Token e enviar E-mail
        token = s.dumps(email, salt='email-confirm')
        
        try:
            # Chamamos a nossa nova função assíncrona
            enviar_confirmacao(email, token, nome)
            flash("Conta criada! Verifique seu e-mail para ativar.")
        except Exception as e:
            logger.error(f"Erro ao disparar thread de e-mail: {e}")
            flash("Conta criada, mas houve um erro ao processar o envio do e-mail.")

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
            print(f"Erro no envio background (email): {e}")

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
                        body="Confira a nova matéria no KitPC!"
                    ),
                    tokens=lista_tokens,
                    data={"slug": slug} # Link para o JS abrir o post certo
                )
                # Envia para todo mundo de uma vez
                response = messaging.send_multicast(notificacao)
                logger.info(f"Push enviado para {response.success_count} dispositivos.")
        except Exception as e:
            logger.error(f"Falha ao enviar push: {e}")

# --- ÁREA ADMINISTRATIVA ---

@app.route("/admin")
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    # 1. Busca usuários e posts
    usuarios_lista = Usuario.query.all()
    posts_lista = Post.query.order_by(Post.data_postagem.desc()).all()
    
    # 2. BUSCA AS MENSAGENS (O que estava faltando aqui!)
    mensagens_lista = MensagemContato.query.order_by(MensagemContato.data_envio.desc()).all()
    
    # 3. Envia TUDO para o admin.html
    return render_template("admin.html", 
                           usuarios=usuarios_lista, 
                           posts=posts_lista, 
                           mensagens=mensagens_lista, # Variável que o HTML espera
                           edit_post=None)

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
           # No def register():
            thread = threading.Thread(
    target=enviar_notificacoes_thread, 
    args=(app, post.titulo, post.slug) # Passando 'app' em vez de '_get_current_object()'
)
            thread.start()

        flash("✅ Postagem publicada! As notificações estão sendo enviadas em segundo plano.")
        return redirect(url_for('admin')) 

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar post: {e}")
        flash(f"❌ Erro ao salvar: {e}")
        return redirect(url_for('admin'))
    


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

# ROTA PARA DELETAR MENSAGEM DE CONTATO (ADICIONADA PARA COMPLETAR A TABELA DE MENSAGENS NO ADMIN)

@app.route("/admin/deletar-mensagem/<int:id>", methods=["POST"])
def deletar_mensagem(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    mensagem = MensagemContato.query.get_or_404(id)
    
    try:
        db.session.delete(mensagem)
        db.session.commit()
        flash("Mensagem removida com sucesso!")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao deletar mensagem: {e}")
        
    return redirect(url_for('admin'))

@app.route('/admin/limpar-todas-mensagens', methods=['POST'])
def limpar_todas_mensagens():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    try:
        # Apaga todos os registros da tabela MensagemContato de uma vez
        MensagemContato.query.delete()
        db.session.commit()
        flash("Todas as mensagens foram removidas com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao limpar mensagens: {e}", "danger")
        
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

    # 3. Busca os COMENTÁRIOS
    from models import Comentario
    comentarios = Comentario.query.filter_by(post_id=post.id)\
                                  .order_by(Comentario.data_postagem.desc())\
                                  .all()
    
    # --- LOGICA DE VISUALIZAÇÕES COM TRAVA DE ADMIN ---
    # Só conta visualização se o usuário NÃO for admin
    if not session.get('is_admin'):
        if post.views is None:
            post.views = 0
        
        post.views += 1
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar views: {e}")
    else:
        # Log apenas para você saber que a trava funcionou no console
        logger.info(f"Visualização de Admin detectada para '{post.titulo}'. Contador ignorado.")
        
    # 5. Enviamos tudo para o HTML
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

@app.route("/post/<slug>")
def redirecionar_post_legado(slug):
    # O código 301 avisa o Google: "Mudei de endereço para sempre, atualize seu índice"
    return redirect(url_for('exibir_post', slug=slug), code=301)

@app.route("/blog")
def redirecionar_blog():
    # O 'arquivo' aqui deve ser o nome da FUNÇÃO que abre a sua página de lista de posts
    # O '301' avisa ao Google que essa mudança é permanente (bom para o SEO)
    return redirect(url_for('arquivo')), 301

# --- LÓGICA DO MONTADOR E SETUP BANCO MANTIDOS COMO ESTÃO ---

def get_total(preco_label):
    precos = {"Um PC OK": 2000, "Um PC BOM": 3000, "Um PC MUITO BOM": 5000, "Até a NASA quer": 10000}
    return precos.get(preco_label, 2000)

def distribuir_orcamento(total, quer_gpu):
    if quer_gpu:
        return {"cpu": total*0.22, "placa_mae": total*0.12, "ram": total*0.12, "gpu": total*0.30, "ssd": total*0.10, "fonte": total*0.08, "gabinete": total*0.06}
    return {"cpu": total*0.40, "placa_mae": total*0.15, "ram": total*0.15, "gpu": 0, "ssd": total*0.15, "fonte": total*0.10, "gabinete": total*0.05}

@app.route("/montar-setup", methods=["POST"])
def montar_setup():
    try:
        dados = request.get_json(force=True)
        total = get_total(dados.get("preco"))

# VERIFICAÇÃO DE NOTEBOOK 
        quer_laptop = dados.get("laptop") == "Sim"
        
        if quer_laptop:
            # Busca o notebook mais caro que ainda cabe no orçamento total
            note = Notebook.query.filter(Notebook.preco <= total).order_by(Notebook.preco.desc()).first()
            
            # Se não achar nenhum no preço, pega o mais barato da loja pra não vir vazio
            if not note:
                note = Notebook.query.order_by(Notebook.preco.asc()).first()
            
            if note:
                return jsonify({
                    "setup": [{
                        "nome": note.nome,
                        "imagem_url": note.imagem_url,
                        "preco_estimado": f"R$ {note.preco:,.2f}",
                        "link_loja": note.link_loja,
                        "componente": "NOTEBOOK",
                        "justificativa": f"Ótima opção de mobilidade. {note.especificacoes}"
                    }],
                    "conselho_mestre": "Como você precisa de mobilidade, escolhemos um notebook que entrega o melhor desempenho para o seu orçamento!"
                })

        gpu = dados.get("gpu") == "Sim"
        orcamento = distribuir_orcamento(total, gpu)
        
        resultado = []
        socket_escolhido = None
        
        # 1. Escolher CPU
        if orcamento.get("cpu", 0) > 0:
            cpu = Processador.query.filter(Processador.preco <= orcamento["cpu"]).order_by(Processador.preco.desc()).first()
            if not cpu:
                cpu = Processador.query.order_by(Processador.preco.asc()).first()
            
            if cpu:
                socket_escolhido = cpu.socket_id
                resultado.append({
                    "nome": cpu.nome, "imagem": cpu.imagem_url, "preco": float(cpu.preco), 
                    "link": cpu.link_loja, "componente": "PROCESSADOR"
                })

        # 2. Escolher Placa-mãe (Compatível com o Socket da CPU)
        if orcamento.get("placa_mae", 0) > 0 and socket_escolhido:
            mobo = PlacaMae.query.filter(PlacaMae.preco <= orcamento["placa_mae"], PlacaMae.socket_id == socket_escolhido).order_by(PlacaMae.preco.desc()).first()
            if not mobo:
                mobo = PlacaMae.query.filter(PlacaMae.socket_id == socket_escolhido).order_by(PlacaMae.preco.asc()).first()
            
            if mobo:
                resultado.append({
                    "nome": mobo.nome, "imagem": mobo.imagem_url, "preco": float(mobo.preco), 
                    "link": mobo.link_loja, "componente": "PLACA MAE"
                })

        # 3. Escolher Memória RAM
        if orcamento.get("ram", 0) > 0:
            ram = MemoriaRAM.query.filter(MemoriaRAM.preco <= orcamento["ram"]).order_by(MemoriaRAM.preco.desc()).first()
            if not ram:
                ram = MemoriaRAM.query.order_by(MemoriaRAM.preco.asc()).first()
            if ram:
                 resultado.append({
                    "nome": ram.nome, "imagem": ram.imagem_url, "preco": float(ram.preco), 
                    "link": ram.link_loja, "componente": "MEMORIA RAM"
                })

        # 4. Escolher Placa de Vídeo (se houver)
        if orcamento.get("gpu", 0) > 0:
            gpu_item = PlacaVideo.query.filter(PlacaVideo.preco <= orcamento["gpu"]).order_by(PlacaVideo.preco.desc()).first()
            if not gpu_item:
                gpu_item = PlacaVideo.query.order_by(PlacaVideo.preco.asc()).first()
            if gpu_item:
                 resultado.append({
                    "nome": gpu_item.nome, "imagem": gpu_item.imagem_url, "preco": float(gpu_item.preco), 
                    "link": gpu_item.link_loja, "componente": "PLACA DE VIDEO"
                })
        
        # 5. Escolher Armazenamento (SSD)
        if orcamento.get("ssd", 0) > 0:
            ssd = Armazenamento.query.filter(Armazenamento.preco <= orcamento["ssd"]).order_by(Armazenamento.preco.desc()).first()
            if not ssd:
                ssd = Armazenamento.query.order_by(Armazenamento.preco.asc()).first()
            if ssd:
                 resultado.append({
                    "nome": ssd.nome, "imagem": ssd.imagem_url, "preco": float(ssd.preco), 
                    "link": ssd.link_loja, "componente": "ARMAZENAMENTO"
                })
        
        # 6. Escolher Fonte
        if orcamento.get("fonte", 0) > 0:
            fonte = Fonte.query.filter(Fonte.preco <= orcamento["fonte"]).order_by(Fonte.preco.desc()).first()
            if not fonte:
                fonte = Fonte.query.order_by(Fonte.preco.asc()).first()
            if fonte:
                 resultado.append({
                    "nome": fonte.nome, "imagem": fonte.imagem_url, "preco": float(fonte.preco), 
                    "link": fonte.link_loja, "componente": "FONTE"
                })

        # 7. Escolher Gabinete
        if orcamento.get("gabinete", 0) > 0:
            gab = Gabinete.query.filter(Gabinete.preco <= orcamento["gabinete"]).order_by(Gabinete.preco.desc()).first()
            if not gab:
                gab = Gabinete.query.order_by(Gabinete.preco.asc()).first()
            if gab:
                 resultado.append({
                    "nome": gab.nome, "imagem": gab.imagem_url, "preco": float(gab.preco), 
                    "link": gab.link_loja, "componente": "GABINETE"
                })

        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
    #-- ROTA PARA GERAR PDF DO SETUP (COM O TOQUE ESPECIAL DO MANUAL DE MONTAGEM) ---
class KitPC_PDF(FPDF):
    def header(self):
        # 1. MARCA D'ÁGUA (Texto inclinado no fundo)
        self.set_font('Arial', 'B', 60)
        self.set_text_color(245, 245, 245) # Cinza quase invisível
        self.rotate(45, 105, 148)
        self.text(40, 190, "KITPC - MANUAL")
        self.rotate(0) # Reseta a rotação para o resto do PDF
        
        # 2. LOGO NO TOPO
        caminho_logo = os.path.join('static', 'Imagens', 'Logo KitPc.png')
        if os.path.exists(caminho_logo):
            self.image(caminho_logo, 10, 8, 25)
        
        # 3. TÍTULO ESTILIZADO
        self.set_font('Arial', 'B', 16)
        self.set_text_color(60, 201, 228) # Azul KitPC (#3CC9E4)
        self.cell(0, 15, "GUIA DE MONTAGEM PERSONALIZADO", ln=True, align='R')
        self.set_draw_color(60, 201, 228)
        self.line(10, 35, 200, 35) # Linha decorativa
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()} | Gerado por KitPC - 2026', align='C')

    def secao_fase(self, numero, titulo):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(60, 201, 228) # Fundo azul
        self.set_text_color(255, 255, 255) # Texto branco
        self.cell(0, 8, f"  FASE {numero}: {titulo}", ln=True, fill=True)
        self.ln(2)
        self.set_text_color(0, 0, 0) # Volta para preto

@app.route("/gerar-pdf", methods=["POST"])
def gerar_pdf():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Dados nao recebidos"}), 400

        setup = dados.get("setup", [])
        total = dados.get("total_estimado", "R$ 0,00")
        objetivo = dados.get("objetivo", "Uso Geral")
        
        # Detecta peças para o manual inteligente
        tem_gpu = any(item.get('componente') == 'Placa de Video' for item in setup)
        tem_ssd = any(item.get('componente') in ['Armazenamento', 'SSD', 'SSD M.2'] for item in setup)
        tem_cooler = any('Cooler' in str(item.get('nome', '')) for item in setup)

        # Inicializa o PDF com nossa classe customizada
        pdf = KitPC_PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # --- 1. RESUMO INICIAL ---
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, "OBJETIVO DO SETUP:", ln=True)
        pdf.set_font("Arial", size=11)
        resumo = f"Este computador foi otimizado para {objetivo}. Com foco em performance e durabilidade."
        pdf.multi_cell(0, 6, resumo)
        pdf.ln(5)

        # --- 2. TABELA DE PEÇAS (MAIS LIMPA) ---
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(146, 22, 253) # Roxo KitPC (#9216FD)
        pdf.cell(0, 8, "LISTA DE COMPONENTES", ln=True)
        pdf.ln(2)
        
        pdf.set_text_color(0, 0, 0)
        for item in setup:
            comp = item.get('componente', 'Item')
            nome = item.get('nome', 'Nao informado')
            preco = item.get('preco_estimado', 'R$ 0,00')
            
            pdf.set_font("Arial", 'B', 9)
            pdf.cell(40, 6, f" {comp.upper()}:", ln=False)
            pdf.set_font("Arial", size=9)
            pdf.cell(0, 6, f"{nome} - {preco}", ln=True)
        
        pdf.ln(4)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, f"INVESTIMENTO TOTAL ESTIMADO: {total} ", ln=True, align='R')
        pdf.ln(5)

        # --- 3. PASSO A PASSO POR FASES (MASTIGADINHO) ---
        
        # FASE 1
        pdf.secao_fase(1, "PREPARACAO DA PLACA-MAE")
        
        pdf.set_font("Arial", 'B', 10)
        pdf.multi_cell(0, 6, "Antes de colocar no gabinete, vamos montar as pecas principais com calma.")
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, "Use a caixa da placa-mae como base para evitar danos estaticos.")
        pdf.ln(2)

        # Passos da Fase 1
        passos1 = (
            "1. Coloque a placa-mae sobre a caixa.\n"
            "2. Instale o processador (alinhe o triangulo e nao force).\n"
            "3. Encaixe a memoria RAM ate ouvir o clique."
        )
        if tem_ssd:
            passos1 += "\n4. Instale o SSD M.2 na diagonal e parafuse."
        
        pdf.multi_cell(0, 6, passos1)
        pdf.ln(2)

        # Alerta e Dica Fase 1
        pdf.set_text_color(200, 0, 0)
        pdf.set_font("Arial", 'B', 9)
        pdf.multi_cell(0, 5, "ATENCAO: Nunca force o processador. Se nao encaixar facil, esta errado.")
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'I', 9)
        pdf.multi_cell(0, 5, "DICA: Evite montar em tapetes e toque em algo metalico antes para descarregar a estatica.")
        pdf.ln(4)

        # FASE 2
        pdf.secao_fase(2, "INSTALACAO NO GABINETE")
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, "Agora vamos colocar a placa-mae dentro do gabinete com seguranca.")
        pdf.ln(2)

        passos2 = (
            "1. Encaixe o espelho traseiro no gabinete.\n"
            "2. Verifique os espacadores (pezinhos dourados).\n"
            "3. Posicione a placa-mae sobre os espacadores.\n"
            "4. Parafuse sem apertar excessivamente."
        )
        if tem_cooler:
            passos2 += "\n5. Instale o cooler e conecte o cabo no CPU_FAN."
        
        pdf.multi_cell(0, 6, passos2)
        pdf.ln(2)
        
        pdf.set_text_color(200, 0, 0)
        pdf.set_font("Arial", 'B', 9)
        pdf.multi_cell(0, 5, "ATENCAO: Nunca monte sem os espacadores - isso pode queimar sua placa!")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

        # FASE 3
        pdf.secao_fase(3, "ENERGIA E CABOS")
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, "Momento de conectar a energia e os fios do painel.")
        pdf.ln(2)

        passos3 = (
            "1. Conecte o cabo de 24 pinos (Energia Geral).\n"
            "2. Conecte o cabo do processador (4/8 pinos no topo)."
        )
        if tem_gpu:
            passos3 += (
                "\n3. Encaixe a placa de video no slot PCIe.\n"
                "4. Parafuse e conecte os cabos de energia da GPU (PCI-E)."
            )
        passos3 += "\n5. Conecte os cabos do painel frontal (Power, Reset, USB, Audio)."
        
        pdf.multi_cell(0, 6, passos3)
        pdf.ln(4)

        # FASE 4
        pdf.secao_fase(4, "PRIMEIRA INICIALIZACAO")
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, "Hora do 'VRAU'! Vamos ligar a maquina.")
        pdf.ln(2)

        passos4 = (
            "1. Ligue o computador e pressione DEL ou F2 repetidamente.\n"
            "2. Na BIOS, ative o perfil XMP ou DOCP para a memoria RAM.\n"
            "3. Verifique se as temperaturas estao normais (entre 30C e 50C)."
        )
        pdf.multi_cell(0, 6, passos4)
        pdf.ln(3)

        pdf.set_text_color(200, 0, 0)
        pdf.set_font("Arial", 'B', 9)
        pdf.multi_cell(0, 5, "SE NAO LIGAR: Verifique os cabos de energia, tente trocar a RAM de slot e confira os cabos do botao Power.")
        pdf.set_text_color(0, 0, 0)

        # --- FINALIZAÇÃO E ENVIO ---
        output = io.BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
        output.write(pdf_output)
        output.seek(0)

        return send_file(output, as_attachment=True, download_name="Manual_Montagem_KitPC.pdf", mimetype="application/pdf")

    except Exception as e:
        print(f"ERRO NO PDF: {str(e)}")
        return jsonify({"error": str(e)}), 500
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
    try:
        dados = request.get_json(force=True)
        
        # 1. Variáveis Base
        is_laptop = dados.get("laptop") == "Sim"
        preco_label = dados.get("preco", "Um PC OK")
        uso = dados.get("uso", "Uso geral")
        gpu_escolhida = dados.get("gpu") == "Sim"
        marca_cpu = dados.get("processador", "Qualquer")
        
        total_maximo = get_total(preco_label)

        # --- FLUXO NOTEBOOK ---
        if is_laptop:
            notebook = Notebook.query.filter(Notebook.preco <= total_maximo)\
                                     .order_by(Notebook.preco.desc()).first()
            
            if not notebook:
                notebook = Notebook.query.order_by(Notebook.preco.asc()).first()

            if notebook:
                preco_formatado = f"R$ {float(notebook.preco):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return jsonify({
                    "setup": [{
                        "componente": "Notebook",
                        "nome": notebook.nome,
                        "imagem_url": notebook.imagem_url,
                        "link_loja": notebook.link_loja,
                        "preco": float(notebook.preco),
                        "preco_estimado": preco_formatado,
                        "justificativa": f"Para quem precisa de mobilidade. Este modelo é ideal para {uso}."
                    }],
                    "total_estimado": preco_formatado,
                    "conselho_mestre": "Notebooks são práticos, mas lembre-se: upgrades futuros são limitados geralmente a RAM e SSD!"
                })
        
        # 1. Obter Total e distribuir o orçamento para as peças
        total = get_total(preco_label)
        orcamento = distribuir_orcamento(total, gpu_escolhida)
        
        setup = []
        custo_total = 0
        total_tdp = 150 # Margem Base (Placa-mãe, fans, disco, periféricos)
        
        # Variáveis globais de compatibilidade
        socket_escolhido = None
        tipo_memoria_escolhida = None
        tamanho_mobo = None
        
        # --- 1. Processador ---
        query_cpu = Processador.query.filter(Processador.preco <= orcamento.get("cpu", 0))
        if marca_cpu in ["AMD", "Intel"]:
            query_cpu = query_cpu.filter(Processador.nome.ilike(f"%{marca_cpu}%"))
            
        cpu = query_cpu.order_by(Processador.preco.desc()).first()
        if not cpu: # Fallback genérico caso orçamento seja baixo demais
            cpu = Processador.query.order_by(Processador.preco.asc()).first()
            
        if cpu:
            socket_escolhido = cpu.socket_id
            total_tdp += cpu.tdp if getattr(cpu, 'tdp', None) else 65
            custo_total += float(cpu.preco)
            setup.append({
                "componente": "Processador",
                "nome": cpu.nome,
                "imagem_url": cpu.imagem_url,
                "link_loja": cpu.link_loja,
                "preco": float(cpu.preco),
                "preco_estimado": f"R$ {float(cpu.preco):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "justificativa": f"A base do seu computador. Escolhido para ter o melhor desempenho na categoria {uso}."
            })
            
        # --- 2. Placa-Mãe ---
        mobo = None
        if socket_escolhido:
            mobo = PlacaMae.query.filter(PlacaMae.preco <= orcamento.get("placa_mae", 0), PlacaMae.socket_id == socket_escolhido).order_by(PlacaMae.preco.desc()).first()
            if not mobo:
                mobo = PlacaMae.query.filter(PlacaMae.socket_id == socket_escolhido).order_by(PlacaMae.preco.asc()).first()
                
        if mobo:
            tipo_memoria_escolhida = getattr(mobo, 'tipo_memoria', 'DDR4')
            tamanho_mobo = getattr(mobo, 'tamanho', 'Micro-ATX')
            custo_total += float(mobo.preco)
            setup.append({
                "componente": "Placa-Mãe",
                "nome": mobo.nome,
                "imagem_url": mobo.imagem_url,
                "link_loja": mobo.link_loja,
                "preco": float(mobo.preco),
                "preco_estimado": f"R$ {float(mobo.preco):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "justificativa": f"O corpo do PC! Garantida 100% de compatibilidade com o processador escolhendo padrão {tipo_memoria_escolhida}."
            })
            
        # --- 3. Memória RAM ---
        ram = None
        if tipo_memoria_escolhida:
            ram = MemoriaRAM.query.filter(MemoriaRAM.preco <= orcamento.get("ram", 0), MemoriaRAM.tipo == tipo_memoria_escolhida).order_by(MemoriaRAM.preco.desc()).first()
            if not ram:
                ram = MemoriaRAM.query.filter(MemoriaRAM.tipo == tipo_memoria_escolhida).order_by(MemoriaRAM.preco.asc()).first()
                
        if not ram: # Fallback de contorno
            ram = MemoriaRAM.query.filter(MemoriaRAM.preco <= orcamento.get("ram", 0)).order_by(MemoriaRAM.preco.desc()).first()
            if not ram:
                ram = MemoriaRAM.query.order_by(MemoriaRAM.preco.asc()).first()
        
        if ram:
            custo_total += float(ram.preco)
            setup.append({
                "componente": "Memória RAM",
                "nome": ram.nome,
                "imagem_url": ram.imagem_url,
                "link_loja": ram.link_loja,
                "preco": float(ram.preco),
                "preco_estimado": f"R$ {float(ram.preco):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "justificativa": f"É aqui que os programas abertos ficam. Esta {tipo_memoria_escolhida} garante agilidade."
            })
            
        # --- 4. Placa de Vídeo ---
        if gpu_escolhida:
            gpu_item = PlacaVideo.query.filter(PlacaVideo.preco <= orcamento.get("gpu", 0)).order_by(PlacaVideo.preco.desc()).first()
            if not gpu_item:
                gpu_item = PlacaVideo.query.order_by(PlacaVideo.preco.asc()).first()
                
            if gpu_item:
                total_tdp += gpu_item.tdp if getattr(gpu_item, 'tdp', None) else 150
                custo_total += float(gpu_item.preco)
                setup.append({
                    "componente": "Placa de Vídeo",
                    "nome": gpu_item.nome,
                    "imagem_url": gpu_item.imagem_url,
                    "link_loja": gpu_item.link_loja,
                    "preco": float(gpu_item.preco),
                    "preco_estimado": f"R$ {float(gpu_item.preco):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    "justificativa": "Esta é a peça principal pra dar muito FPS e qualidade nos jogos que você vai curtir!"
                })
                
        # --- 5. Armazenamento (SSD) ---
        ssd = Armazenamento.query.filter(Armazenamento.preco <= orcamento.get("ssd", 0)).order_by(Armazenamento.preco.desc()).first()
        if not ssd:
            ssd = Armazenamento.query.order_by(Armazenamento.preco.asc()).first()
            
        if ssd:
            custo_total += float(ssd.preco)
            setup.append({
                "componente": "Armazenamento",
                "nome": ssd.nome,
                "imagem_url": ssd.imagem_url,
                "link_loja": ssd.link_loja,
                "preco": float(ssd.preco),
                "preco_estimado": f"R$ {float(ssd.preco):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "justificativa": "Um SSD pra Windows ligar em poucos segundos e nada travar carregando."
            })
            
        # --- 6. Fonte de Alimentação ---
        tdp_necessario = total_tdp * 1.25 # Folga de 25% obrigatória para segurança
        fonte = Fonte.query.filter(Fonte.potencia >= tdp_necessario, Fonte.preco <= orcamento.get("fonte", 0)).order_by(Fonte.preco.desc()).first()
        if not fonte:
            fonte = Fonte.query.filter(Fonte.potencia >= tdp_necessario).order_by(Fonte.preco.asc()).first()
            if not fonte:
                fonte = Fonte.query.order_by(Fonte.preco.desc()).first()
                
        if fonte:
            custo_total += float(fonte.preco)
            potencia_fonte = getattr(fonte, 'potencia', '?')
            setup.append({
                "componente": "Fonte de Alimentação",
                "nome": fonte.nome,
                "imagem_url": fonte.imagem_url,
                "link_loja": fonte.link_loja,
                "preco": float(fonte.preco),
                "preco_estimado": f"R$ {float(fonte.preco):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "justificativa": f"O coração que bombeia energia pro PC. O seu exige ~{int(tdp_necessario)}W, esta envia {potencia_fonte}W com folga."
            })
            
        # --- 7. Gabinete ---
        query_gab = Gabinete.query.filter(Gabinete.preco <= orcamento.get("gabinete", 0))
        if tamanho_mobo:
            query_gab = query_gab.filter(Gabinete.tamanho_suportado.ilike(f"%{tamanho_mobo}%"))
            
        gab = query_gab.order_by(Gabinete.preco.desc()).first()
        if not gab:
            gab = Gabinete.query.filter(Gabinete.tamanho_suportado.ilike(f"%{tamanho_mobo}%")).order_by(Gabinete.preco.asc()).first()
            if not gab:
                gab = Gabinete.query.order_by(Gabinete.preco.asc()).first()
                
        if gab:
            custo_total += float(gab.preco)
            setup.append({
                "componente": "Gabinete",
                "nome": gab.nome,
                "imagem_url": gab.imagem_url,
                "link_loja": gab.link_loja,
                "preco": float(gab.preco),
                "preco_estimado": f"R$ {float(gab.preco):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "justificativa": f"As peças ficarão protegidas. Ele tem espaço suficiente para o modelo {tamanho_mobo} da placa-mãe."
            })
            
        # --- 8. Conselho Mestre Dinâmico e Seguro ---
        try:
            # Pede conselho usando nomes já formatados para a IA não retornar arrays bizarros
            nomes_pecas = ", ".join([str(s.get('nome', '')) for s in setup])
            prompt = f"Um usuário está montando um PC focado em '{uso}' com: {nomes_pecas}. Escreva uma ÚNICA dica prática, rápida (1 frase entusiástica) de cuidado na montagem usando essas tecnologias ou um upgrade sugerido para o futuro."
            resposta = model.generate_content(prompt)
            conselho_mestre = resposta.text.replace("*", "").strip() if resposta.text else "Tudo pronto! Seu setup é altamente compatível."
        except Exception as e_ia:
            logger.warning(f"IA Conselho falhou ({e_ia}), usando fallback.")
            conselho_mestre = "Seu setup foi montado com sucesso! Cuidado ao instalar o processador e garanta um bom fluxo de ar no gabinete."

        return jsonify({
            "setup": setup,
            "total_estimado": f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "conselho_mestre": conselho_mestre
        })
    
    

    except Exception as e:
        import traceback
        erro_str = traceback.format_exc()
        logger.error(f"Erro no Algoritmo do Montador:\n{erro_str}")
        return jsonify({"erro": f"Ops, ocorreu um erro! Detalhe técnico: {str(e)}"}), 500

  # --- SITEMAP DINÂMICO PARA GOOGLE ---  
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    try:
        pages = []

        now = datetime.now().strftime('%Y-%m-%d')
        
        # Lista EXATA de rotas que o Google NÃO deve indexar
        rotas_bloqueadas = [
            '/admin', 
            '/logout', 
            '/setup-db-kaio', 
            '/login', 
            '/register', 
            '/confirmar-email',
            '/health',
            '/sitemap.xml',
            '/authorize', 
            '/ping',      
            '/ads.txt',   
            '/robots.txt',
            '/fale-conosco' 
        ]

       # 1. Páginas Estáticas
        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and len(rule.arguments) == 0:
                url_path = str(rule.rule)
                
                # BLOQUEIO INTELIGENTE:
                # Se a URL for exatamente uma das bloqueadas...
                if url_path in rotas_bloqueadas:
                    continue
                
                # ...ou se ela começar com termos proibidos (como /admin/algo ou /login/algo)
                if any(url_path.startswith(prefix) for prefix in ['/admin', '/login', '/authorize', '/static', '/google']):
                    continue

                full_url = f"https://kitpc.com.br{url_path}"
                
                # Ajuste fino para a Home
                if url_path == '/':
                    full_url = "https://kitpc.com.br/"
                
                pages.append([full_url, now])

        # 2. Páginas Dinâmicas (Posts do Blog)
        # Verifique se o nome da classe é Post e se os campos estão corretos
        posts = Post.query.filter_by(arquivado=False).all() 
        for post in posts:
            # Garanta que o caminho aqui seja exatamente como o da sua rota de post
            url = f"https://kitpc.com.br/post/{post.slug}" # ou /blog/ dependendo da sua rota
            pages.append([url, now])

        # Remove duplicatas se houver
        pages = list(set(tuple(p) for p in pages))

        sitemap_xml = render_template('sitemap_template.xml', pages=pages)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
    except Exception as e:
        # Se der erro, ele mostra no log do Render
        print(f"Erro ao gerar sitemap: {e}") 
        return str(e), 500
    

    
    # --- Fale Conosco ---

@app.route('/fale-conosco', methods=['GET', 'POST'])
def fale_conosco():
    if request.method == 'POST':
        # 1. Pegar os dados (Certifique-se que o name no HTML é 'nome', 'email', 'assunto' e 'mensagem')
        nome = request.form.get('nome')
        email_usuario = request.form.get('email')
        assunto = request.form.get('assunto')
        texto = request.form.get('mensagem')

        # 2. Validação (Corrigi para renderizar o template certo: contato.html)
        if not nome or not email_usuario or not texto:
            return render_template('contato.html', erro="Por favor, preencha todos os campos obrigatórios.")

        try:
            # 3. Salvar no Banco (Aiven)
            # VERIFIQUE SE NO SEU MODELS.PY O CAMPO É 'mensagem' OU 'conteudo'
            nova_mensagem = MensagemContato(
                nome=nome,
                email=email_usuario,
                assunto=assunto,
                mensagem=texto # Se der erro aqui, mude para conteudo=texto
            )
            
            db.session.add(nova_mensagem)
            db.session.commit()
            
            print(f"✅ Mensagem de {nome} salva no banco!")
            return render_template('contato.html', sucesso=True)

        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro no Banco: {e}")
            # Mostra o erro real na tela para a gente parar de adivinhar
            return render_template('contato.html', erro=f"Erro técnico: {str(e)}")

    # Se for GET, apenas mostra a página limpa
    return render_template('contato.html')

    
@app.route("/privacidade")
def privacidade():
    return render_template("privacidade.html")

@app.route("/termos")
def termos():
    return render_template("termos.html")

@app.route('/cookies')
def cookies():
    return render_template('cookies.html')

@app.route('/contato')
def contato():
    return render_template('contato.html')

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
