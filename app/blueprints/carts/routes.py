from app.blueprints.carts import carts_bp
from .schemas import cart_schema
from app.utils.auth import token_required
from flask import request, jsonify
from app.models import db,Users, Carts, Cart_books, Book_descriptions
from app.blueprints.book_descriptions.schemas import book_description_schema

@carts_bp.route('',methods={'GET'})
@token_required
def get_cart_books():
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    cart = db.session.query(Carts).where(Carts.user_id == user_id).first()
    if not cart:
        return ({"message" : "There is no cart for you"}), 200
    if len(cart.cart_books) == 0:
        return ({"message" : "Your cart is empty"}), 200
    response = {
        "cart_info": cart_schema.dump(cart),
        "cart_books": [
            {
                "book": book_description_schema.dump(book.book_description),
                "quantity": book.quantity
            }
            for book in cart.cart_books
        ]
    }
    return jsonify(response), 200

@carts_bp.route('/add_book/<int:book_description_id>',methods={'PUT'})
@token_required
def add_book_to_cart(book_description_id):
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    book = db.session.get(Book_descriptions, book_description_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    if not book:
        return jsonify({"error" : f"Book Description not found."}), 404
    existed_cart = db.session.query(Carts).where(Carts.user_id == user_id).first()
    if not existed_cart:
        new_cart = Carts(user_id=user_id)
        db.session.add(new_cart)
        db.session.commit()
        data = {
            "cart_id" : new_cart.id,
            "book_description_id" : book_description_id,
            "quantity" : 1
        }
        new_cart_book = Cart_books(**data)
        db.session.add(new_cart_book)
        new_cart.cart_books.append(new_cart_book)
        db.session.commit()
        return ({"message" : "The book added to your cart"}), 200
    existing_book_in_cart = db.session.query(Cart_books).where((Cart_books.cart_id == existed_cart.id) & (Cart_books.book_description_id == book_description_id)).first()
    if existing_book_in_cart:
        existing_book_in_cart.quantity += 1
        db.session.commit()
        return ({"message" : "The book quantity added"}), 200
    data = {
            "cart_id" : existed_cart.id,
            "book_description_id" : book_description_id,
            "quantity" : 1
        }
    new_cart_book = Cart_books(**data)
    db.session.add(new_cart_book)
    existed_cart.cart_books.append(new_cart_book)
    db.session.commit()
    return ({"message" : "The book added to your cart"}), 200

@carts_bp.route('/remove_book/<int:book_description_id>',methods={'PUT'})
@token_required
def remove_book_from_cart(book_description_id):
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    book = db.session.get(Book_descriptions, book_description_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    if not book:
        return jsonify({"error" : f"Book Description not found."}), 404
    cart = db.session.query(Carts).where(Carts.user_id == user_id).first()
    if not cart:
        return jsonify({"error" : f"Cart not found."}), 404
    existing_book = db.session.query(Cart_books).where((Cart_books.cart_id == cart.id) & (Cart_books.book_description_id == book_description_id)).first()
    if not existing_book:
        return jsonify({"error" : f"Book is not in your cart."}), 404
    if existing_book.quantity > 1:
        existing_book.quantity -= 1
        db.session.commit()
        return ({"message" : "The book quantity decreased"}), 200
    cart.cart_books.remove(existing_book)
    db.session.delete(existing_book)
    db.session.commit()
    return ({"message" : "The book removed from your cart"}), 200


