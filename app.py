from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

"""
Falta implementar:
Um sistema de permanência de dados.
Pesquisa de tarefas.
Exibição de tarefas criadas, além de edição e exclusão de tarefas.
Validar os dados do formulário de registro e login.
Permitir o login somente se o usuário tiver se registrado previamente.
Polir o código.
"""

user = None
tarefas = []


@app.route('/')
def index():
    if user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    global user

    if user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Processar dados do formulário
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        curso = request.form.get('curso')
        periodo = request.form.get('periodo')

        # Salva os dados no user
        user = {
            'nome': username,
            'email': email,
            'curso': curso,
            'periodo': periodo
        }
        return redirect(url_for('dashboard'))

    return render_template('registro.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user

    if user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Salvar dados do usuário
        user = {
            'nome': username,
            'email': username,
            'curso': 'Informática para Internet',
            'periodo': '1º Ano'
        }
        return redirect(url_for('dashboard'))

    return render_template('login.html', user=user)


@app.route('/logout', methods=['POST'])
def logout():
    global user
    user = None
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if not user:
        return redirect(url_for('login'))

    # Implementar pesquisa de tarefas e exibição de tarefas criadas
    return render_template('dashboard.html', user=user, tarefas=[], pesquisa='')


@app.route('/adicionar_tarefa', methods=['GET', 'POST'])
def adicionar_tarefa():
    global tarefas

    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        disciplina = request.form.get('disciplina')
        data_entrega = request.form.get('data_entrega')

        tarefas.append({
            'titulo': titulo,
            'descricao': descricao,
            'disciplina': disciplina,
            'data_entrega': data_entrega
        })
        return redirect(url_for('dashboard'))

    return render_template('form_tarefa.html', user=user, curso=user.get('curso'), periodo=user.get('periodo'))


if __name__ == '__main__':
    app.run(debug=True)