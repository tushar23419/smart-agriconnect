from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///agriconnect.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'super-secret-key')
app.config['PROPAGATE_EXCEPTIONS'] = True

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

# Import and register blueprints
from routes.auth import auth_bp
from routes.farmers import farmers_bp
from routes.dealers import dealers_bp
from routes.products import products_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(farmers_bp, url_prefix='/api/farmers')
app.register_blueprint(dealers_bp, url_prefix='/api/dealers')
app.register_blueprint(products_bp, url_prefix='/api/products')  # Fixed missing parenthesis

# Add this block for Gunicorn compatibility
if __name__ == '__main__':
    app.run()