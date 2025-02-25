from flask import Flask, render_template, jsonify
from config import Config
from sqlalchemy import text
from flask_migrate import Migrate
from models.models import db, Wallet, User, Transaction
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from routes.auth import auth_bp
from routes.user_routes import user_bp
from routes.wallet_routes import wallet_bp
from routes.transaction_routes import transaction_bp
from routes.settings_routes import settings_bp
from routes.roles_routes import roles_bp
from routes.admin_routes import admin_bp
from utils.decorators import role_required

app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(wallet_bp, url_prefix='/api')
app.register_blueprint(transaction_bp, url_prefix='/api')
app.register_blueprint(settings_bp, url_prefix='/api')
app.register_blueprint(roles_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

db.init_app(app)
migrate = Migrate(app, db)

# Dashboard Routes
@app.route('/admin/dashboard')
@jwt_required()
@role_required(['admin'])
def admin_dashboard():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    return render_template('admin_dashboard.html', user=user)

@app.route('/agent/dashboard')
@jwt_required()
@role_required(['agent'])
def agent_dashboard():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return render_template('agent_dashboard.html', user=user)

@app.route('/user/dashboard')
@jwt_required()
@role_required(['user'])
def user_dashboard():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return render_template('user_dashboard.html', user=user)

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({"error": "Unauthorized access. Please login first."}), 401

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found."}), 404

if __name__ == '__main__':
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print("✅ Database connected successfully!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    app.run(debug=True, host='0.0.0.0', port=5000)
