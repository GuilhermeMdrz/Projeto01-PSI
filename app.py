from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'chave_secreta'
tarefas = []

def carregar_tarefas():
    global tarefas

    try:
        with open('tarefas.json', 'r', encoding='utf-8') as arquivo:
            tarefas = json.load(arquivo)

    except FileNotFoundError:
        tarefas = []
def salvar_tarefas():
    with open('tarefas.json', 'w', encoding='utf-8') as arquivo:
        json.dump(
            tarefas,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

""" 
Falta implementar: 
Validar os dados do formulário de registro e login. 
Permitir o login somente se o usuário tiver se registrado previamente. 
Polir o código.
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

        session['user'] = {'nome': username,'email': email,'curso': curso,'periodo': periodo}

        return redirect(url_for('dashboard'))

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if session.get('user'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        session['user'] = {'nome': username,'email': username,'curso': 'informatica','periodo': '1ano'}

        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():

    session.pop('user', None)

    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():

    if not session.get('user'):
        return redirect(url_for('login'))

    pesquisa = request.args.get('pesquisa')

    tarefas_filtradas = tarefas

    if pesquisa:
        tarefas_filtradas = []

        for tarefa in tarefas:

            if (
                pesquisa.lower() in tarefa['titulo'].lower()
                or
                pesquisa.lower() in tarefa['disciplina'].lower()
            ):
                tarefas_filtradas.append(tarefa)

    return render_template(
        'dashboard.html',
        user=session.get('user'),
        tarefas=tarefas_filtradas,
        pesquisa=pesquisa)

@app.route('/adicionar_tarefa', methods=['GET', 'POST'])
def adicionar_tarefa():

    if not session.get('user'):
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
        salvar_tarefas()
        return redirect(url_for('dashboard'))

    return render_template('form_tarefa.html', user=session.get('user'), curso=session.get('user').get('curso'),periodo=session.get('user').get('periodo'))

@app.route('/excluir/<int:id>')
def excluir(id):

    if id < len(tarefas):
        tarefas.pop(id)
        salvar_tarefas()

    return redirect(url_for('dashboard'))
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):

    if request.method == 'POST':

        tarefas[id]['titulo'] = request.form.get('titulo')
        tarefas[id]['descricao'] = request.form.get('descricao')
        tarefas[id]['disciplina'] = request.form.get('disciplina')
        tarefas[id]['data_entrega'] = request.form.get('data_entrega')

        salvar_tarefas()

        return redirect(url_for('dashboard'))

    tarefa = tarefas[id]

    return render_template(
        'form_tarefa.html',
        tarefa=tarefa,
        id=id,
        curso=session.get('user').get('curso'),
        periodo=session.get('user').get('periodo')
    )
if __name__ == '__main__':
    carregar_tarefas()
    app.run(debug=True)