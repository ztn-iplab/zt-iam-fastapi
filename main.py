from flask import Flask, request, jsonify, render_template, redirect, url_for
from config import Config
from sqlalchemy import text
from flask_migrate import Migrate
from models.models import db, Wallet, User, Transaction
from flask_jwt_extended import JWTManager
from routes.auth import auth_bp
from routes.user_routes import user_bp
from routes.wallet_routes import wallet_bp
from routes.transaction_routes import transaction_bp

app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from config.py

# Initialize JWT Manager
jwt = JWTManager(app)

# Register Blueprints for API routes
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(wallet_bp, url_prefix='/api')
app.register_blueprint(transaction_bp, url_prefix='/api')

# Initialize the database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Front-End Routes

@app.route('/')
def index():
    """
    Landing page displaying the combined login/registration form.
    """
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """
    A simple dashboard page. In a production scenario,
    we'll retrieve the actual user data (and require authentication).
    Here, we pass a dummy user for demonstration.
    """
    dummy_user = {
        'full_name': 'John Doe',
        'mobile_number': '123456789',
        'country': 'KEN',
        'trust_score': 0.85,
        'wallet': {
            'balance': 150.0,
            'currency': 'RWF'
        }
    }
    return render_template('dashboard.html', user=dummy_user)

# Global Error Handlers

@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({"error": "Unauthorized access. Please login first."}), 401

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found."}), 404

# Application Startup

if __name__ == '__main__':
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            print("✅ Database connected successfully!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")

    app.run(debug=True, host='0.0.0.0', port=5000)
