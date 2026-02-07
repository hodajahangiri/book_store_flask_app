from .schemas import category_schema, categories_schema
from app.blueprints.categories import categories_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import db, Categories

@categories_bp.route('', methods={'POST'})
def add_category():
    try:
        data = category_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error_message" : e.messages}), 400
    # Check if category exist
    existed_category = db.session.query(Categories).where(Categories.title == data["title"]).first()
    if existed_category:
        return jsonify({"error" : f"This title is already exist in category."}), 400
    new_category = Categories(**data)
    db.session.add(new_category)
    db.session.commit()
    return category_schema.jsonify(new_category), 201

@categories_bp.route('', methods={'GET'})
def get_categories():
    categories = db.session.query(Categories).all()
    return categories_schema.jsonify(categories)

@categories_bp.route('/<int:category_id>', methods={'PUT'})
def update_category(category_id):
    category = db.session.get(Categories, category_id)
    if not category:
        return jsonify({"error" : f"This Category with id: {category_id} not found."}), 404
    try:
        category_data = category_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    # Check the isbn admin wants to change not be repeated
    existing_category = db.session.query(Categories).where(Categories.title == category_data["title"], Categories.id != category_id).first()
    if existing_category:
        return jsonify({"error" : f"Title can not be repetitive."}), 400
    for key, value in category_data.items():
        setattr(category, key, value)
    db.session.commit()
    return jsonify({"message" : f"Successfully category with id: {category_id} updated."}), 200

@categories_bp.route('/<int:category_id>', methods={'DELETE'})
def delete_category(category_id):
    category = db.session.get(Categories, category_id)
    if not category:
        return jsonify({"error" : f"This Category with id: {category_id} not found."}), 404
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message" : f"Successfully deleted book_description with id: {category_id}"}), 200