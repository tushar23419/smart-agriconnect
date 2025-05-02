from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash

# Updated imports using relative paths
from ..app import db
from ..models import User, Farmer, Dealer

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not all(k in data for k in ['username', 'email', 'password', 'role']):
        return jsonify({"error": "Missing required fields"}), 400
    
    if data['role'] not in ['farmer', 'dealer']:
        return jsonify({"error": "Invalid role"}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400
    
    # Create user
    user = User(
        username=data['username'],
        email=data['email'],
        role=data['role']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Create profile based on role
    if data['role'] == 'farmer':
        farmer = Farmer(user_id=user.id)
        db.session.add(farmer)
    else:
        dealer = Dealer(user_id=user.id)
        db.session.add(dealer)
    
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not user.check_password(data.get('password')):
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity={
        'id': user.id,
        'username': user.username,
        'role': user.role
    })
    
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    profile_data = None
    if user.role == 'farmer' and user.farmer_profile:
        profile = user.farmer_profile
        profile_data = {
            "full_name": profile.full_name,
            "contact_number": profile.contact_number,
            "address": profile.address,
            "location": {"lat": profile.location_lat, "long": profile.location_long},
            "farm_size": profile.farm_size,
            "crops_grown": profile.crops_grown
        }
    elif user.role == 'dealer' and user.dealer_profile:
        profile = user.dealer_profile
        profile_data = {
            "full_name": profile.full_name,
            "business_name": profile.business_name,
            "contact_number": profile.contact_number,
            "address": profile.address,
            "location": {"lat": profile.location_lat, "long": profile.location_long},
            "business_type": profile.business_type,
            "preferred_products": profile.preferred_products
        }
    
    return jsonify({
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "profile": profile_data
    }), 200