from app.blueprints.addresses import addresses_bp
from app.utils.auth import token_required
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import db, Addresses, Users
from .schemas import address_schema, addresses_schema
from app.blueprints.users.schemas import users_schema

@addresses_bp.route('', methods={'POST'})
@token_required
def create_address():
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    try:
        address_data = address_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error_message" : e.messages}), 400
    # Check if address exist or not.
    existed_address = db.session.query(Addresses).where(
        (Addresses.line1 == address_data["line1"]) &
        (Addresses.line2 == address_data["line2"]) &
        (Addresses.number == address_data["number"]) &
        (Addresses.city == address_data["city"]) &
        (Addresses.state == address_data["state"]) &
        (Addresses.country == address_data["country"]) &
        (Addresses.zipcode == address_data["zipcode"])
        ).first()
    if existed_address:
        if user not in existed_address.users:
            existed_address.users.append(user)
            db.session.commit()
            return jsonify({"message": "Address added to your address lists"}), 201
        else:
            return jsonify({"error" : f"This address is in your address list"}), 400
    else:
        new_address = Addresses(**address_data)
        new_address.users.append(user)
        db.session.add(new_address)
        db.session.commit()
        return jsonify({"message": "Address added to your address lists"}), 201

@addresses_bp.route('', methods={'GET'})
@token_required
def get_user_addresses():
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    return addresses_schema.jsonify(user.addresses), 200

@addresses_bp.route('/all')
def get_all_addresses():
    addresses = db.session.query(Addresses).all()
    return addresses_schema.jsonify(addresses), 200

@addresses_bp.route('<int:address_id>', methods={'PUT'})
@token_required
def update_address(address_id):
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    address = db.session.get(Addresses, address_id)
    if not address:
        return jsonify({"error" : "Address not found."}), 404
    if not user:
        return jsonify({"error" : "User not found."}), 404
    if user not in address.users:
        return jsonify({"error" : "You can not updated this address."}), 404
    try:
        address_data = address_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error_message" : e.messages}), 400
    # check if the address is in address table
    existed_address = db.session.query(Addresses).where(
        (Addresses.line1 == address_data["line1"]) &
        (Addresses.line2 == address_data["line2"]) &
        (Addresses.number == address_data["number"]) &
        (Addresses.city == address_data["city"]) &
        (Addresses.state == address_data["state"]) &
        (Addresses.country == address_data["country"]) &
        (Addresses.zipcode == address_data["zipcode"]) &
        (Addresses.id != address_id)
        ).first()
    if existed_address:
        print("--------existed_address")
        if user not in existed_address.users:
            existed_address.users.append(user)
            print("existed_address.users.append(user)")
            address.users.remove(user)
            if len(address.users) == 0:
                db.session.delete(address)
            print("address.users.remove(user)")
            db.session.commit()
            return jsonify({"message": "Address updated to your address lists"}), 200
        else:
            address.users.remove(user)
            if len(address.users) == 0:
                db.session.delete(address)
            db.session.commit()
            return jsonify({"message" : f"This address is in your address list"}), 200
    else:
        # Check if address has another user or not.
        if (len(address.users) > 1) and (user in address.users):
            # It means there is another users with this address so can't updated and has to create another address
            # remove user from this address
            address.users.remove(user)
            new_address = Addresses(**address_data)
            new_address.users.append(user)
            db.session.add(new_address)
            db.session.commit()
            return jsonify({"message": "Address updated in your address lists"}), 200
        elif (len(address.users) == 1) and (user in address.users):
            for key, value in address_data.items():
                setattr(address, key, value)
            db.session.commit()
            return jsonify({"message": "Address updated in your address lists"}), 200
        else:
            return jsonify({"error": "Something went wrong"}), 500

@addresses_bp.route('<int:address_id>', methods={'DELETE'})
@token_required
def delete_address(address_id):
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    address = db.session.get(Addresses, address_id)
    if not address:
        return jsonify({"error" : f"Address not found."}), 404
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    if address in user.addresses:
        user.addresses.remove(address)
        if user in address.users:
            address.users.remove(user)
        if len(address.users) == 0 and len(address.orders) == 0:
            db.session.delete(address)
        db.session.commit()
        return jsonify({"message" : "Your address successfully deleted from address list"}), 200
    else:
        return jsonify({"message": "This address is not in your address list"}), 200