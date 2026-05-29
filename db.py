import sqlite3

def criar_conexao():
    conexao = sqlite3.connect('banco.db')
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        curso TEXT,
        periodo TEXT,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT NOT NULL,
        disciplina TEXT,
        data_entrega DATE,
        concluida INTEGER DEFAULT 0,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usuario_id INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) 
    )
""")

    conexao.commit()
    conexao.close()