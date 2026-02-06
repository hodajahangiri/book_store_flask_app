from app.blueprints.users import users_bp
from .schemas import user_schema, user_credential_schema, users_schema
from app.blueprints.addresses.schemas import addresses_schema
from app.blueprints.payments.schemas import payments_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import db, Users
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import encode_token, token_required


# Create a User 
@users_bp.route('', methods={'POST'})
def create_user():
    try:
        data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error_message" : e.messages}), 400
    # Check if email exist or not because email is unique attribute
    existed_user_email = db.session.query(Users).where(Users.email == data["email"]).first()
    if existed_user_email:
        return jsonify({"error" : f"{data["email"]} is already associated with an account."}), 400
    data["password"] = generate_password_hash(data["password"])
    new_user = Users(**data)
    db.session.add(new_user)
    db.session.commit()
    new_user_token = encode_token(new_user.id)
    response = {"user_data" : data,
                "token" : new_user_token}
    return jsonify(response), 201

# Login User
@users_bp.route('/login', methods={'POST'})
def login():
    try:
        credential_data = user_credential_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error_message" : e.messages}), 400
    existed_user = db.session.query(Users).where(Users.email == credential_data["email"]).first()
    if existed_user and check_password_hash(existed_user.password, credential_data["password"]):
        user_token = encode_token(existed_user.id)
        response = {
            "message" : f"Successfully logged in. Welcome {existed_user.first_name}",
            "user_data" : user_schema.dump(existed_user),
            "token" : user_token
        }
        return jsonify(response), 200
    else:
        return jsonify({"error message" : "Invalid email or password."}), 400

@users_bp.route('', methods=["GET"])
def get_all_users():
    users = db.session.query(Users).all()
    return users_schema.jsonify(users), 200


@users_bp.route('/profile', methods={'GET'})
@token_required
def get_user():
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    response = {
        "user_data" : user_schema.dump(user),
        "user_payments" : payments_schema.dump(user.payments),
        "user_addresses" : addresses_schema.dump(user.addresses)
    }
    return jsonify(response), 200

@users_bp.route('', methods={'DELETE'})
@token_required
def delete_user():
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message" : f"Successfully your account deleted."}), 200

@users_bp.route('', methods=["PUT"])
@token_required
def update_user_profile():
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    # Check the email User wants to update not be taken with another mechanic
    existing_email = db.session.query(Users).where(Users.email == user_data["email"], Users.id != user_id).first()
    if existing_email:
        return jsonify({"error" : f"{user_data["email"]} is already taken with another mechanic."}), 400
    user_data["password"] = generate_password_hash(user_data["password"])
    for key, value in user_data.items():
        setattr(user, key, value)
    db.session.commit()
    response = {
        "message" : f"Successfully your profile updated.",
        "user_data" : user_schema.dump(user),
        }
    return jsonify(response), 200
