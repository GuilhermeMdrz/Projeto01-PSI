from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import criar_conexao, inicializar_banco

app = Flask(__name__)
app.secret_key = 'chave_secreta'

inicializar_banco()

@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        curso = request.form.get('curso')
        periodo = request.form.get('periodo')
        
        if not username or not email or not password:
            flash('Preencha todos os campos!')
            return redirect(url_for('registro'))
        
        conexao = criar_conexao()
        usuario_existe = conexao.execute( "SELECT * FROM usuarios WHERE email = ?", (email,) ).fetchone()

        if usuario_existe:
            conexao.close()
            flash('Esse email já foi registrado!')
            return redirect(url_for('registro'))

        conexao.execute("""
            INSERT INTO usuarios (nome, email, senha, curso, periodo)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, password, curso, periodo))
        conexao.commit()
        conexao.close()

        flash('Registro foi realizado com sucesso!')
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conexao = criar_conexao()
        usuario = conexao.execute( "SELECT * FROM usuarios WHERE email = ? AND senha = ?", (username, password) ).fetchone()
        conexao.close()
        
        if usuario:
            session['user_id'] = usuario['id']
            flash('Seu login foi realizado com sucesso!')
            return redirect(url_for('dashboard'))

        flash('Email ou senha incorretos!')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():

    session.pop('user_id', None)
    flash('Você saiu do sistema!')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():

    if not session.get('user_id'):
        return redirect(url_for('login'))

    conexao = criar_conexao()
    usuario = conexao.execute("SELECT * FROM usuarios WHERE id = ?",(session['user_id'],)).fetchone()
    pesquisa = request.args.get('pesquisa', '').lower()

    if pesquisa:
        tarefas = conexao.execute("""SELECT * FROM tarefas WHERE usuario_id = ? AND concluida = 0 AND (LOWER(titulo) LIKE ? OR LOWER(disciplina) LIKE ?) """,(session['user_id'],f'%{pesquisa}%',f'%{pesquisa}%')).fetchall()

    else:
        tarefas = conexao.execute("""SELECT * FROM tarefas WHERE usuario_id = ? AND concluida = 0 """,(session['user_id'],)).fetchall()

    conexao.close()

    return render_template('dashboard.html',user=usuario,tarefas=tarefas,pesquisa=pesquisa)

@app.route('/adicionar_tarefa', methods=['GET', 'POST'])
def adicionar_tarefa():

    if not session.get('user_id'):
        return redirect(url_for('login'))

    conexao = criar_conexao()
    usuario = conexao.execute("SELECT * FROM usuarios WHERE id = ?",(session['user_id'],)).fetchone()

    if request.method == 'POST':

        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        disciplina = request.form.get('disciplina')
        data_entrega = request.form.get('data_entrega')

        if not titulo or not descricao:
            conexao.close()
            flash('Preencha todos os campos da tarefa!')
            return redirect(url_for('adicionar_tarefa'))

        tarefa_existe = conexao.execute("""SELECT * FROM tarefas WHERE usuario_id = ? AND LOWER(titulo) = LOWER(?) """,(session['user_id'], titulo)).fetchone()

        if tarefa_existe:
            conexao.close()
            flash('Você já tem uma tarefa com esse título!')
            return redirect(url_for('adicionar_tarefa'))

        conexao.execute('INSERT INTO tarefas (titulo, descricao, disciplina, data_entrega, concluida, usuario_id) VALUES (?, ?, ?, ?, ?, ?)',
         (titulo, descricao, disciplina, data_entrega, 0, session['user_id'])
        )

        conexao.commit()
        conexao.close()

        flash('Sua tarefa foi adicionada com sucesso!')
        return redirect(url_for('dashboard'))

    conexao.close()
    return render_template('form_tarefa.html',user=usuario,curso=usuario['curso'],periodo=usuario['periodo'])

@app.route('/excluir/<int:id>')
def excluir(id):

    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    conexao = criar_conexao()

    tarefa = conexao.execute(''' SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?''',(id, session['user_id'])).fetchone()

    if tarefa:
        conexao.execute('''DELETE FROM tarefas WHERE id = ? ''',(id,))
        conexao.commit()
        flash('Sua tarefa foi excluída com sucesso!')

    else:
        flash('A tarefa não foi encontrada!')

    conexao.close()

    return redirect(url_for('dashboard'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):

    if not session.get('user_id'):
        return redirect(url_for('login'))

    conexao = criar_conexao()

    usuario = conexao.execute('SELECT * FROM usuarios WHERE id = ?', (session['user_id'],)).fetchone()

    tarefa = conexao.execute('SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?',(id, session['user_id'])).fetchone()

    if not tarefa:
        conexao.close()

        flash('A tarefa não foi encontrada!')

        return redirect(url_for('dashboard'))

    if request.method == 'POST':

        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        disciplina = request.form.get('disciplina')
        data_entrega = request.form.get('data_entrega')

        conexao.execute('UPDATE tarefas SET titulo = ?, descricao = ?, disciplina = ?, data_entrega = ? WHERE id = ?',
            (titulo, descricao, disciplina, data_entrega, id)
            )

        conexao.commit()
        conexao.close()

        flash('Sua tarefa foi editada com sucesso!')

        return redirect(url_for('dashboard'))

    conexao.close()

    return render_template('form_tarefa.html',tarefa=tarefa, id=id, curso=usuario['curso'], periodo=usuario['periodo'])


@app.route('/concluir/<int:id>')
def concluir(id):

    if not session.get('user_id'):
        return redirect(url_for('login'))

    conexao = criar_conexao()

    tarefa = conexao.execute('SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?',(id, session['user_id'])).fetchone()

    if tarefa:
        conexao.execute('UPDATE tarefas SET concluida = 1 WHERE id = ?',(id,))

        conexao.commit()

        flash('Tarefa marcada como concluída!')

    else:
        flash('Erro ao concluir tarefa!')

    conexao.close()

    return redirect(url_for('dashboard'))
    
if __name__ == '__main__':
    app.run(debug=True)