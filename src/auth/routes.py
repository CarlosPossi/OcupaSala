from flask import render_template, request, redirect, url_for, session, flash
from functools import wraps
from . import auth_bp
from models.utils import USERS_FILE, load_json, save_json
from models.entidades import Usuario

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash("Por favor, faça login para acessar essa página.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        users_data = load_json(USERS_FILE)
        
        if any(u['email'] == email for u in users_data):
            flash("E-mail já cadastrado!", "error")
        else:
            # Usando a classe Usuario
            novo_usuario = Usuario(nome=nome, email=email, senha=senha)
            users_data.append(novo_usuario.to_dict())
            save_json(USERS_FILE, users_data)
            flash("Cadastro realizado com sucesso! Faça login.", "success")
            return redirect(url_for('auth.login'))
            
    return render_template('cadastro.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if 'user_email' in session:
        return redirect(url_for('views.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        users_data = load_json(USERS_FILE)
        user_dict = next((u for u in users_data if u['email'] == email), None)
        
        if user_dict:
            # Convertendo dict para objeto Usuario para usar o método verificar_senha
            user = Usuario.from_dict(user_dict)
            if user.verificar_senha(senha):
                session['user_email'] = user.email
                session['user_nome'] = user.nome
                return redirect(url_for('views.dashboard'))
        
        flash("E-mail ou senha incorretos.", "error")
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
