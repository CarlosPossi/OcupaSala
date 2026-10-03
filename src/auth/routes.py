from functools import wraps
from flask import render_template, request, redirect, url_for, session, flash
from . import auth_bp
from models.utils import USERS_FILE, load_json, save_json
from models.entidades import Usuario


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_email" not in session:
            flash("Por favor, faça login para acessar essa página.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = (request.form.get("nome") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""
        users = load_json(USERS_FILE)
        if len(nome) < 2:
            flash("Informe seu nome completo.", "error")
        elif len(senha) < 6:
            flash("A senha precisa ter pelo menos 6 caracteres.", "error")
        elif any(u["email"].lower() == email for u in users):
            flash("E-mail já cadastrado!", "error")
        else:
            users.append(Usuario(nome=nome, email=email, senha=senha).to_dict())
            save_json(USERS_FILE, users)
            flash("Cadastro realizado com sucesso! Faça login.", "success")
            return redirect(url_for("auth.login"))
    return render_template("cadastro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if "user_email" in session:
        return redirect(url_for("views.dashboard"))
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""
        d = next((u for u in load_json(USERS_FILE) if u["email"].lower() == email), None)
        if d:
            user = Usuario.from_dict(d)
            if user.verificar_senha(senha):
                session["user_email"] = user.email
                session["user_nome"] = user.nome
                return redirect(url_for("views.dashboard"))
        flash("E-mail ou senha incorretos.", "error")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
