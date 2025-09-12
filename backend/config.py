from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

# Config usando variáveis de ambiente com valores padrão
DB_USER = os.environ.get("DB_USER", "elvis")
DB_PASS = os.environ.get("DB_PASS", "8531")
DB_NAME = os.environ.get("DB_NAME", "northwind")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------- MODELS ----------
class Usuario(db.Model):
    __tablename__ = "usuarios"
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    tarefas = db.relationship("Tarefa", backref="usuario", lazy=True)

class Categoria(db.Model):
    __tablename__ = "categorias"
    id_categoria = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    tarefas = db.relationship("Tarefa", backref="categoria", lazy=True)

class Tarefa(db.Model):
    __tablename__ = "tarefas"
    id_tarefa = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    prioridade = db.Column(db.String(50), default="Média")
    status = db.Column(db.String(50), default="Pendente")
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_prazo = db.Column(db.DateTime, nullable=True)

    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey("categorias.id_categoria"), nullable=False)

class Comentario(db.Model):
    __tablename__ = "comentarios"
    id_comentario = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    data_comentario = db.Column(db.DateTime, default=datetime.utcnow)
    id_tarefa = db.Column(db.Integer, db.ForeignKey("tarefas.id_tarefa"), nullable=False)

# ---------- CRIAR TABELAS ----------
with app.app_context():
    try:
        db.create_all()
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        print("Erro ao criar tabelas:", e)

# ---------- ROTA TESTE ----------
@app.route("/")
def home():
    return "Flask conectado com sucesso!"

if __name__ == "__main__":
    app.run(debug=True)
