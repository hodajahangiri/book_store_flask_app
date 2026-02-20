from app.blueprints.users import users_bp
from .schemas import user_schema, user_credential_schema, users_schema
from app.blueprints.addresses.schemas import addresses_schema
from app.blueprints.payments.schemas import payments_schema
from app.blueprints.book_reviews.schemas import user_reviews_schema
from app.blueprints.favorites.schemas import user_favorites_schema
from app.blueprints.orders.schemas import order_schema
from app.blueprints.carts.schemas import cart_schema
from app.blueprints.book_descriptions.schemas import book_description_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import db, Users, user_addresses, Order_books, Cart_books, Payments, Orders, Carts, Reviews, Favorites
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import encode_token, token_required

import traceback


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
    try:
        user_id = request.user_id
        user = db.session.get(Users, user_id)
        if not user:
            return jsonify({"error" : f"User not found."}), 404
        if len(user.addresses) > 0:
            for address in user.addresses:
                if len(address.orders) > 0:
                    db.session.query(user_addresses).filter(user_addresses.c.user_id == user.id).delete()
                    db.session.commit()
                else:
                    db.session.delete(address)
                    db.session.commit()
        if user.cart:
            for item in user.cart.cart_books:
                db.session.delete(item)
            # db.session.query(Cart_books).filter(Cart_books.cart_id == user.cart.id).delete()
            db.session.commit()
            db.session.delete(user.cart)
            db.session.commit()
        if len(user.orders) > 0:
            for order in user.orders:
                for item in order.order_books:
                    db.session.delete(item)
                db.session.commit()
                db.session.delete(order)
                db.session.commit()
                # db.session.query(Order_books).filter(Order_books.order_id == order.id).delete()
            # db.session.commit()
        if len(user.reviews) > 0:
            db.session.query(Reviews).filter(Reviews.user_id == user.id).delete()
            db.session.commit()
        if len(user.favorites) > 0 :
            db.session.query(Favorites).filter(Favorites.user_id == user.id).delete()
            db.session.commit()
        if len(user.payments) > 0 :
            db.session.query(Payments).filter(Payments.user_id == user.id).delete()
            db.session.commit()
        # db.session.query(Orders).filter(Orders.user_id == user.id).delete()
        # db.session.commit()
        # db.session.query(Carts).filter(Carts.user_id == user.id).delete()
        # db.session.commit()

        # Delete the user after all related objects are removed
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Your account was successfully deleted."}), 200
    except Exception as e:
        print("Error in delete_user:", e)
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

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

@users_bp.route('/reviews', methods=["GET"])
@token_required
def get_user_reviews():
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    response = {
        "user" : user_schema.dump(user),
        "user_reviews" : user_reviews_schema.dump(user.reviews)
        }
    return jsonify(response), 200

# Get all favorites for a user
@users_bp.route('/favorites', methods=['GET'])
@token_required
def get_user_favorites():
	user_id = int(request.user_id)
	user = db.session.get(Users, user_id)
	if not user:
		return jsonify({"error": "User not found."}), 404
	response = {
            "user" : user_schema.dump(user),
            "user_favorites" : user_favorites_schema.dump(user.favorites)
        }
	return jsonify(response), 200

@users_bp.route('/orders', methods={'GET'})
@token_required
def get_user_orders():
    user_id = int(request.user_id)
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    response = {
        "user" : user_schema.dump(user),
        "user_orders" : [
            {
            "order_info": order_schema.dump(order),
            "order_books": [
                {
                    "book": book_description_schema.dump(book.book_description),
                    "quantity": book.quantity
                }
                for book in order.order_books
            ]} for order in user.orders ]
    }
    return jsonify(response), 200

@users_bp.route('/carts', methods={'GET'})
@token_required
def get_user_cart():
    user_id = int(request.user_id)
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    if not user.cart:
         return jsonify({"message": "There is no cart for you."}), 200
    if len(user.cart.cart_books) == 0:
        return jsonify({"message": "Your cart is empty."}), 200
    response = {
        "user" : user_schema.dump(user),
        "user_cart" :
            {
                "cart_info": cart_schema.dump(user.cart),
                "cart_books": [
                    {
                        "book": book_description_schema.dump(book.book_description),
                        "quantity": book.quantity
                    }
                    for book in user.cart.cart_books
                ]
            }
    }
    return jsonify(response), 200
