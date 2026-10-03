import sys
from flask import Flask
from auth import auth_bp
from views import views_bp
from models.utils import get_secret_key
from models.seed import semear_demo


def create_app():
    app = Flask(__name__)
    app.secret_key = get_secret_key()
    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)
    semear_demo()  # só age se o sistema estiver vazio (primeira execução)
    return app


if __name__ == "__main__":
    import os
    if "--reset-demo" in sys.argv:
        semear_demo(forcar=True)
        print("Dados de demonstração recriados (datas relativas a hoje).")
        sys.exit(0)
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
