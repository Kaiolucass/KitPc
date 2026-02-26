from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# --- TABELAS DE USUÁRIOS E SEGURANÇA ---

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    montagens = db.relationship('MontagemSalva', backref='dono', lazy=True)
    confirmado = db.Column(db.Boolean, default=False)

# --- TABELAS DO BLOG ---

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    subtitulo = db.Column(db.String(300))
    conteudo = db.Column(db.Text, nullable=False)
    imagem_url = db.Column(db.Text)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    data_postagem = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    arquivado = db.Column(db.Boolean, default=False)

# --- TABELAS DO MONTADOR (HARDWARE) ---

class SocketCPU(db.Model):
    __tablename__ = 'sockets_cpu'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

class Processador(db.Model):
    __tablename__ = 'processadores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)
    socket_id = db.Column(db.Integer, db.ForeignKey('sockets_cpu.id'))

class PlacaMae(db.Model):
    __tablename__ = 'placas_mae'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)
    socket_id = db.Column(db.Integer, db.ForeignKey('sockets_cpu.id'))

class MemoriaRAM(db.Model):
    __tablename__ = 'memorias_ram'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)
    tipo = db.Column(db.String(20))

class PlacaVideo(db.Model):
    __tablename__ = 'placas_video'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)

class Armazenamento(db.Model):
    __tablename__ = 'armazenamentos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)
    tipo = db.Column(db.String(10))

class Gabinete(db.Model):
    __tablename__ = 'gabinetes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)

class Fonte(db.Model):
    __tablename__ = 'fontes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)
    potencia = db.Column(db.Integer)

class Cooler(db.Model):
    __tablename__ = 'coolers'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)

class Monitor(db.Model):
    __tablename__ = 'monitores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)

class Mouse(db.Model):
    __tablename__ = 'mouses'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)

class Teclado(db.Model):
    __tablename__ = 'teclados'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)

class FoneOuvido(db.Model):
    __tablename__ = 'fones_ouvido'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)

class Microfone(db.Model):
    __tablename__ = 'microfones'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)

class Cadeira(db.Model):
    __tablename__ = 'cadeiras'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    imagem_url = db.Column(db.Text)
    link_loja = db.Column(db.Text)

# --- TABELA DE MONTAGENS SALVAS ---

class MontagemSalva(db.Model):
    __tablename__ = 'montagens_salvas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Detalhes do PC salvo
    nome_setup = db.Column(db.String(100), default="Meu Setup Gamer")
    processador = db.Column(db.String(100))
    placa_mae = db.Column(db.String(100))
    ram = db.Column(db.String(100))
    gpu = db.Column(db.String(100))
    armazenamento = db.Column(db.String(100))
    fonte = db.Column(db.String(100))
    gabinete = db.Column(db.String(100))
    preco_total = db.Column(db.Numeric(10, 2))
    
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

class Comentario(db.Model):
    __tablename__ = 'comentarios' # Coloquei no plural para seguir seu padrão
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_postagem = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    autor = db.relationship('Usuario', backref=db.backref('meus_comentarios', lazy=True))
    post_rel = db.relationship('Post', backref=db.backref('comentarios_do_post', lazy=True))