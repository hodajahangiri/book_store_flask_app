from app.blueprints.payments import payments_bp
from app.utils.auth import token_required
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import db, Users, Payments
from .schemas import payment_schema, payments_schema
from app.blueprints.users.schemas import users_schema

@payments_bp.route('', methods={'POST'})
@token_required
def create_payment():
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    try:
        payment_data = payment_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error_message" : e.messages}), 400
    # Check if payment exist or not.
    existed_payment = db.session.query(Payments).where((Payments.user_id == user_id) & (Payments.card_number == payment_data["card_number"])).first()
    if existed_payment:
        return jsonify({"error" : f"{payment_data["card_number"]} added before in your payments methods."}), 400
    payment_data["user_id"] = user_id
    new_payment = Payments(**payment_data)
    db.session.add(new_payment)
    db.session.commit()
    return payment_schema.jsonify(new_payment), 201

@payments_bp.route('', methods={'GET'})
@token_required
def get_payments():
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    return payments_schema.jsonify(user.payments), 200

@payments_bp.route('/all')
def get_all_payments():
    payments = db.session.query(Payments).all()
    return payments_schema.jsonify(payments), 200

@payments_bp.route('/all_with_users')
def get_all_payments_with_users():
    payments = db.session.query(Payments).all()
    response = [{
        "users" : users_schema.dump(payment.users),
        "address" : payment_schema.dump(peyment)
    }
     for payment in payments   
    ]
    return jsonify(response), 200


@payments_bp.route('<int:payment_id>', methods={'PUT'})
@token_required
def update_payment(payment_id):
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    payment = db.session.get(Payments, payment_id)
    if not payment:
        return jsonify({"error" : f"Payment not found."}), 404
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    if payment not in user.payments:
        return jsonify({"error" : f"You can not update this payment method."}), 404
    try:
        payment_data = payment_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error_message" : e.messages}), 400
    # Check if payment exist or not.
    existed_payment = db.session.query(Payments).where((Payments.user_id == user_id) & (Payments.card_number == payment_data["card_number"]) & (Payments.id != payment_id)).first()
    if existed_payment:
        return jsonify({"error" : f"{payment_data["card_number"]} is duplicated."}), 400
    payment_data["user_id"] = user_id
    for key, value in payment_data.items():
        setattr(payment, key, value)
    db.session.commit()
    return jsonify({"message" : "Your card data successfully updated"}), 200

@payments_bp.route('<int:payment_id>', methods={'DELETE'})
@token_required
def delete_payment(payment_id):
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    payment = db.session.get(Payments, payment_id)
    if not payment:
        return jsonify({"error" : f"Payment not found."}), 404
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    if payment in user.payments:
        print("payment in user.payments")
        user.payments.remove(payment)
        if len(payment.orders) == 0:
            print("len(payment.orders) == 0")
            db.session.delete(payment)
        db.session.commit()
        return jsonify({"message" : "Your card information successfully deleted from payments methods"}), 200
    else:
        return jsonify({"message": "This payments in not in your payments method"}), 200