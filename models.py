from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

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

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    subtitulo = db.Column(db.String(300))
    conteudo = db.Column(db.Text, nullable=False)
    imagem_url = db.Column(db.Text)
    # Slug é a URL amigável, ex: kitpc.com.br/blog/melhor-pc-gamer
    slug = db.Column(db.String(200), unique=True, nullable=False)
    data_postagem = db.Column(db.DateTime, default=db.func.current_timestamp())