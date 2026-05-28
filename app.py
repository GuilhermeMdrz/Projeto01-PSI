from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'chave_secreta'
tarefas = []
usuarios = []

""" 
FALTA:
Adequar o sistema para criar as tarefas usando o db.
Modificar os dados no banco ao editar, excluir ou concluir uma tarefa.
"""

@app.route('/')
def index():
    if session.get('user'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if session.get('user'):
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

        for user in usuarios:
            if user['email'] == email:
                flash('Esse email já foi registrado!')
                return redirect(url_for('registro'))

        usuarios.append({
            'nome': username,
            'email': email,
            'password': password,
            'curso': curso,
            'periodo': periodo
        })

        flash('Registro foi realizado com sucesso!')
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if session.get('user'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        for user in usuarios:  
            if user['email'] == username and user['password'] == password:
                session['user'] = user
                flash('Seu login foi realizado com sucesso!')
                return redirect(url_for('dashboard'))

        flash('Email ou senha incorretos!')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():

    session.pop('user', None)
    flash('Você saiu do sistema!')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():

    if not session.get('user'):
        return redirect(url_for('login'))

    pesquisa = request.args.get('pesquisa', '')
    tarefas_filtradas = []
     
    for tarefa in tarefas:
          if tarefa['usuario'] == session['user']['email'] and not tarefa.get('concluida', False):

            if not pesquisa:
                tarefas_filtradas.append(tarefa)

            elif (
                pesquisa in tarefa['titulo'].lower()
                or pesquisa in tarefa['disciplina'].lower()
                ):
                tarefas_filtradas.append(tarefa)

    return render_template('dashboard.html',user=session.get('user'),tarefas=tarefas_filtradas,pesquisa=pesquisa)

@app.route('/adicionar_tarefa', methods=['GET', 'POST'])
def adicionar_tarefa():

    if not session.get('user'):
        return redirect(url_for('login'))

    if request.method == 'POST':

        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        disciplina = request.form.get('disciplina')
        data_entrega = request.form.get('data_entrega')
        
        if not titulo or not descricao:
            flash('Preencha todos os campos da tarefa!')
            return redirect(url_for('adicionar_tarefa'))
        
        for tarefa in tarefas:
            if (
                tarefa['usuario'] == session['user']['email'] and
                tarefa['titulo'].strip().lower() == titulo.strip().lower()
            ):
                flash('Você já tem uma tarefa com esse título!')
                return redirect(url_for('adicionar_tarefa'))
       
        tarefas.append({
            'titulo': titulo,
            'descricao': descricao,
            'disciplina': disciplina,
            'data_entrega': data_entrega,
            'usuario': session['user']['email'],
            'concluida': False
        })
        
        flash('Sua tarefa foi adicionada com sucesso!')
        return redirect(url_for('dashboard'))

    return render_template('form_tarefa.html', user=session.get('user'), curso=session.get('user').get('curso'),periodo=session.get('user').get('periodo'))

@app.route('/excluir/<int:id>')
def excluir(id):

    if id < len(tarefas) and tarefas[id]['usuario'] == session['user']['email']:
        tarefas.pop(id)
        flash('Sua tarefa foi excluída com sucesso!')
    else:
        flash('A tarefa não foi encontrada!')
    return redirect(url_for('dashboard'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if id >= len(tarefas) or tarefas[id]['usuario'] != session['user']['email']:
        flash('A tarefa não foi encontrada!')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':

        tarefas[id]['titulo'] = request.form.get('titulo')
        tarefas[id]['descricao'] = request.form.get('descricao')
        tarefas[id]['disciplina'] = request.form.get('disciplina')
        tarefas[id]['data_entrega'] = request.form.get('data_entrega')
        tarefas[id]['concluida'] = tarefas[id].get('concluida', False)

        flash('Sua tarefa foi editada com sucesso!')
        return redirect(url_for('dashboard'))

    tarefa = tarefas[id]

    return render_template(
        'form_tarefa.html',
        tarefa=tarefa,
        id=id,
        curso=session.get('user').get('curso'),
        periodo=session.get('user').get('periodo')
    )

@app.route('/concluir/<int:id>')
def concluir(id):
    if id < len(tarefas) and tarefas[id]['usuario'] == session['user']['email']:
        tarefas[id]['concluida'] = True
        flash('Tarefa marcada como concluída!')
    else:
        flash('Erro ao concluir tarefa!')

    return redirect(url_for('dashboard'))
    
if __name__ == '__main__':
    app.run(debug=True)