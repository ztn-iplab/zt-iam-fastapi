from flask import Flask, render_template, jsonify, redirect, url_for, send_from_directory
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

from flask_mail import Message
from extensions import mail
import os


app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)
mail.init_app(app) 

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"error": "Invalid token"}), 422

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"error": "Missing access token"}), 401

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp)
app.register_blueprint(wallet_bp, url_prefix='/api')
app.register_blueprint(transaction_bp, url_prefix='/api')
app.register_blueprint(settings_bp, url_prefix='/api')
app.register_blueprint(roles_bp, url_prefix='/api')
app.register_blueprint(admin_bp)
app.register_blueprint(agent_bp)
app.register_blueprint(webauthn_bp)


db.init_app(app)
migrate = Migrate(app, db)

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# Fav Icon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

#Login Error handler
@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({"error": "Unauthorized access. Please login first."}), 401

#Recource not error handler
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found."}), 404

# flask Mail
@app.route('/send-test-email')
def send_test_email():
    msg = Message(subject="🚀 Flask Mail Test",
                  recipients=["patrick.mutabazi.pj1@g.ext.naist.jp"],
                  body="Hey buddy! This is a test email from your Flask app.")
    mail.send(msg)
    return jsonify({"message": "Test email sent successfully!"})

@app.route('/debug-jwt')
def debug_jwt():
    print("🍪 Cookies in request:", request.cookies)
    return "Check your terminal!"


# App Main Function
if __name__ == '__main__':
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print("✅ Database connected successfully!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    app.run(debug=True, host='0.0.0.0', port=5000)
