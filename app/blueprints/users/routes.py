from app.blueprints.users import users_bp
from .schemas import user_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import db, Users
from werkzeug.security import generate_password_hash
from app.utils.auth import encode_token


# Create a User 
@users_bp.route('', methods={'POST'})
def create_user():
    try:
        data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    # Check if email exist or not because email is unique attribute
    exist_user_email = db.session.query(Users).where(Users.email == data["email"]).first()
    if exist_user_email:
        return jsonify({"error" : f"{data["email"]} is already associated with an account."}), 400
    data["password"] = generate_password_hash(data["password"])
    new_user = Users(**data)
    db.session.add(new_user)
    db.session.commit()
    new_user_token = encode_token(new_user.id)
    response = {"user_data" : data,
                "token" : new_user_token}
    return jsonify(response), 201