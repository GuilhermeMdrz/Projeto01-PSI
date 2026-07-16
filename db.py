from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    curso = db.Column(db.String(100))
    periodo = db.Column(db.String(50))
    criado_em = db.Column(db.DateTime, server_default=db.func.now())

    tarefas = db.relationship(
        "Tarefa",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )


class Tarefa(db.Model):
    __tablename__ = "tarefas"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    disciplina = db.Column(db.String(100))
    data_entrega = db.Column(db.Date)
    concluida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, server_default=db.func.now())

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    usuario = db.relationship("Usuario", back_populates="tarefas")