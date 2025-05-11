from flask import Flask, render_template, jsonify, redirect, url_for, send_from_directory, request
from config import Config
from sqlalchemy import text
from flask_migrate import Migrate
from models.models import db, Wallet, User, Transaction, UserAccessControl, UserRole, SIMCard
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from routes.auth import auth_bp
from routes.user_routes import user_bp
from routes.wallet_routes import wallet_bp
from routes.transaction_routes import transaction_bp
from routes.settings_routes import settings_bp
from routes.roles_routes import roles_bp
from routes.admin_routes import admin_bp
from utils.decorators import role_required
from routes.agent_routes import agent_bp
from routes.webauthn import webauthn_bp
from routes.iam_api import iam_api_bp
from flask_mail import Message
from extensions import mail
import os
from utils.logger import app_logger
from werkzeug.middleware.proxy_fix import ProxyFix


# ==========================
# 🔧 Flask App Setup
# ==========================
app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

jwt = JWTManager(app)
mail.init_app(app) 

use_proxy = os.getenv("USE_NGINX_PROXY", "True").lower() == "true"
cert_path = os.getenv("SSL_CERT_PATH")
key_path = os.getenv("SSL_KEY_PATH")

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"error": "Invalid token"}), 422

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"error": "Missing access token"}), 401

# ==========================
# 🔗 Register Blueprints
# ==========================
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp)
app.register_blueprint(wallet_bp, url_prefix='/api')
app.register_blueprint(transaction_bp, url_prefix='/api')
app.register_blueprint(settings_bp)
app.register_blueprint(roles_bp, url_prefix='/api')
app.register_blueprint(admin_bp)
app.register_blueprint(agent_bp)
app.register_blueprint(webauthn_bp)
app.register_blueprint(iam_api_bp)

db.init_app(app)
migrate = Migrate(app, db)

# ==========================
# 🌐 Routes
# ==========================
@app.route('/')
def index():
    app_logger.info("[WEB] Home page accessed.")
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(401)
def unauthorized_error(error):
    app_logger.warning(f"[401] Unauthorized access from {request.remote_addr}")
    return jsonify({"error": "Unauthorized access. Please login first."}), 401

@app.errorhandler(404)
def not_found_error(error):
    app_logger.warning(f"[404] Resource not found: {request.path}")
    return jsonify({"error": "Resource not found."}), 404

@app.route('/send-test-email')
def send_test_email():
    msg = Message(subject="🚀 Flask Mail Test",
                  recipients=["patrick.mutabazi.pj1@g.ext.naist.jp"],
                  body="Hey buddy! This is a test email from your Flask app.")
    mail.send(msg)
    app_logger.info("[MAIL] Test email sent to patrick.mutabazi.pj1@g.ext.naist.jp")
    return jsonify({"message": "Test email sent successfully!"})

@app.route('/debug-jwt')
def debug_jwt():
    app_logger.debug(f"[DEBUG] JWT Debug route hit. Cookies: {request.cookies}")
    return "Check your terminal!"

# ==========================
# 🚀 App Main Function
# ==========================
if __name__ == '__main__':
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            app_logger.info("✅ Database connected successfully!")
        except Exception as e:
            app_logger.error(f"❌ Database connection failed: {e}")

    if use_proxy:
        app_logger.info("🚀 Running behind NGINX reverse proxy (SSL externally handled).")
        app.run(
            debug=False,
            host='127.0.0.1',
            port=5000
        )
    else:
        if not os.path.exists(cert_path) or not os.path.exists(key_path):
            raise RuntimeError("❌ SSL certificates not found at the paths defined in .env")

        app_logger.info("🧪 Running Flask with internal SSL (dev mode).")
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            ssl_context=(cert_path, key_path)
        )
