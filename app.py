from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import db, Usuario, Tarefa

app = Flask(__name__)
app.secret_key = 'chave_secreta'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///banco.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()

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
        
        usuario_existe = Usuario.query.filter_by(email=email).first()

        if usuario_existe:
            flash("Esse email já foi registrado!")
            return redirect(url_for("registro"))

        novo_usuario = Usuario(
            nome=username,
            email=email,
            senha=password,
            curso=curso,
            periodo=periodo
        )

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Registro realizado com sucesso!")
        return redirect(url_for("login"))

@app.route('/login', methods=['GET', 'POST'])
def login():

    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(
            email=username,
            senha=password
        ).first()

        if usuario:
            session['user_id'] = usuario.id
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

    usuario = Usuario.query.get(session['user_id'])

    pesquisa = request.args.get('pesquisa', '').lower()

    if pesquisa:
        tarefas = Tarefa.query.filter(
            Tarefa.usuario_id == session['user_id'],
            Tarefa.concluida == False,
            (
                Tarefa.titulo.ilike(f'%{pesquisa}%') |
                Tarefa.disciplina.ilike(f'%{pesquisa}%')
            )
        ).all()
    else:
        tarefas = Tarefa.query.filter_by(
            usuario_id=session['user_id'],
            concluida=False
        ).all()

    return render_template(
        'dashboard.html',
        user=usuario,
        tarefas=tarefas,
        pesquisa=pesquisa
    )

@app.route('/adicionar_tarefa', methods=['GET', 'POST'])
def adicionar_tarefa():

    if not session.get('user_id'):
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['user_id'])

    if request.method == 'POST':

        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        disciplina = request.form.get('disciplina')
        data_entrega = request.form.get('data_entrega')

        if not titulo or not descricao:
            flash('Preencha todos os campos da tarefa!')
            return redirect(url_for('adicionar_tarefa'))

        tarefa_existe = Tarefa.query.filter(
            Tarefa.usuario_id == session['user_id'],
            Tarefa.titulo.ilike(titulo)
        ).first()

        if tarefa_existe:
            flash('Você já tem uma tarefa com esse título!')
            return redirect(url_for('adicionar_tarefa'))

        nova_tarefa = Tarefa(
            titulo=titulo,
            descricao=descricao,
            disciplina=disciplina,
            data_entrega=data_entrega if data_entrega else None,
            concluida=False,
            usuario_id=session['user_id']
        )

        db.session.add(nova_tarefa)
        db.session.commit()

        flash('Sua tarefa foi adicionada com sucesso!')
        return redirect(url_for('dashboard'))

    return render_template(
        'form_tarefa.html',
        user=usuario,
        curso=usuario.curso,
        periodo=usuario.periodo
    )

@app.route('/excluir/<int:id>')
def excluir(id):

    if not session.get('user_id'):
        return redirect(url_for('login'))

    tarefa = Tarefa.query.filter_by(
        id=id,
        usuario_id=session['user_id']
    ).first()

    if tarefa:
        db.session.delete(tarefa)
        db.session.commit()
        flash('Sua tarefa foi excluída com sucesso!')
    else:
        flash('A tarefa não foi encontrada!')

    return redirect(url_for('dashboard'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):

    if not session.get('user_id'):
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['user_id'])

    tarefa = Tarefa.query.filter_by(
        id=id,
        usuario_id=session['user_id']
    ).first()

    if not tarefa:
        flash('A tarefa não foi encontrada!')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':

        tarefa.titulo = request.form.get('titulo')
        tarefa.descricao = request.form.get('descricao')
        tarefa.disciplina = request.form.get('disciplina')

        data_entrega = request.form.get('data_entrega')
        tarefa.data_entrega = data_entrega if data_entrega else None

        db.session.commit()

        flash('Sua tarefa foi editada com sucesso!')
        return redirect(url_for('dashboard'))

    return render_template(
        'form_tarefa.html',
        tarefa=tarefa,
        id=id,
        curso=usuario.curso,
        periodo=usuario.periodo
    )


@app.route('/concluir/<int:id>')
def concluir(id):

    if not session.get('user_id'):
        return redirect(url_for('login'))

    tarefa = Tarefa.query.filter_by(
        id=id,
        usuario_id=session['user_id']
    ).first()

    if tarefa:
        tarefa.concluida = True
        db.session.commit()
        flash('Tarefa marcada como concluída!')
    else:
        flash('Erro ao concluir tarefa!')

    return redirect(url_for('dashboard'))
    
if __name__ == '__main__':
    app.run(debug=True)