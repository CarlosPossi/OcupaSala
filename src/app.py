import os
from flask import Flask
from auth import auth_bp
from views import views_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_fiap')

    # Registro de Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

