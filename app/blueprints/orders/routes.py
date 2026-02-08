from app.blueprints.orders import orders_bp
from .schemas import order_schema
from app.utils.auth import token_required
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import db, Users, Orders,Order_books, Carts, Cart_books, Addresses, Payments
from app.blueprints.book_descriptions.schemas import book_description_schema

# After checkout cart the order will be created 
@orders_bp.route('/<int:cart_id>/address/<int:address_id>/payment/<int:payment_id>',methods={'POST'})
@token_required
def create_order(cart_id,address_id,payment_id):
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    cart = db.session.get(Carts, cart_id)
    address = db.session.get(Addresses, address_id)
    payment = db.session.get(Payments, payment_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    if not cart:
        return jsonify({"error" : f"Cart not found."}), 404
    if not address:
        return jsonify({"error" : f"Address not found."}), 404
    if not payment:
        return jsonify({"error" : f"Payment Method not found."}), 404
    # check if cart belongs to user
    if cart.user_id != int(user_id):
        return jsonify({"error" : f"Cart does not belong to you."}), 400
    # check if payments belongs to user
    if payment.user_id != int(user_id):
        return jsonify({"error" : f"Payment method does not belong to you."}), 400
    if user not in address.users:
        return jsonify({"error" : f"Address does not belong to you."}), 400
    try:
        data = order_schema.load(request.json)
        print("datttttaaaaaaaaaaaaa",data)
    except ValidationError as e:
        return jsonify({"error_message" : e.messages}), 400
    data["user_id"] = user_id
    data["payment_id"] = payment_id
    data["address_id"] = address_id
    new_order = Orders(**data)
    db.session.add(new_order)
    db.session.commit()
    # Add books to order
    for book in cart.cart_books:
        order_book_data = {
            "order_id" : new_order.id,
            "book_description_id" : book.book_description_id,
            "quantity" : book.quantity
        }
        new_order_book = Order_books(**order_book_data)
        db.session.add(new_order_book)
        new_order.order_books.append(new_order_book)
    db.session.commit()
    response = {
        "order_info": order_schema.dump(new_order),
        "order_books" : [
            {
                "book": book_description_schema.dump(book.book_description),
                "quantity": book.quantity
            }
            for book in new_order.order_books
        ]
    }
    # clear cart and delete cart
    db.session.query(Cart_books).where(Cart_books.cart_id==cart.id).delete()
    db.session.query(Carts).where(Carts.id == cart.id).delete()
    db.session.commit()
    return jsonify(response), 201

@orders_bp.route('/<int:order_id>',methods={'DELETE'})
@token_required
def delete_order(order_id):
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    order = db.session.get(Orders, order_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    if not order:
        return jsonify({"error" : f"Order not found."}), 404
    if order.user_id != int(user_id):
        return jsonify({"error" : f"You can not cancel this order, because its not belongs to you."}), 400
    # clear order books and delete order
    if(order.status == "Pending"):   
        db.session.query(Order_books).where(Order_books.order_id==order.id).delete()
        db.session.query(Orders).where(Orders.id == order.id).delete()
        db.session.commit()
        return ({"message" : "Successfully, Your order deleted"}), 200
    elif(order.status == "Processing"):
        order.status = "Cancelled"
        return({"message" : "Your order status changed"})
    return jsonify({"error" : f"You can not cancel this order, because its already been shipped."}), 400

@orders_bp.route('',methods={'GET'})
def get_all_orders():
    orders = db.session.query(Orders).all()
    response = [
        {
            "order_info": order_schema.dump(order),
            "order_books": [
                {
                    "book": book_description_schema.dump(book.book_description),
                    "quantity": book.quantity
                }
                for book in order.order_books
            ]
        }
        for order in orders
    ]
    return jsonify(response), 200