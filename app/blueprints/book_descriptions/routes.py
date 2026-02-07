from .schemas import book_description_schema, book_descriptions_schema
from app.blueprints.categories.schemas import categories_schema 
from app.blueprints.book_descriptions import book_descriptions_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import db, Book_descriptions, Categories

@book_descriptions_bp.route('', methods={'POST'})
def add_book_description():
    try:
        data = book_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error_message" : e.messages}), 400
    # Check if book description exist
    existed_book = db.session.query(Book_descriptions).where(Book_descriptions.isbn == data["isbn"]).first()
    if existed_book:
        return jsonify({"error" : f"This isbn is already associated with a book."}), 400
    new_book = Book_descriptions(**data)
    db.session.add(new_book)
    db.session.commit()
    return book_description_schema.jsonify(new_book), 201

@book_descriptions_bp.route('', methods={'GET'})
def get_book_descriptions():
    book_descriptions = db.session.query(Book_descriptions).all()
    return book_descriptions_schema.jsonify(book_descriptions)

@book_descriptions_bp.route('/<int:book_id>', methods={'PUT'})
def update_book_description(book_id):
    book_description = db.session.get(Book_descriptions, book_id)
    if not book_description:
        return jsonify({"error" : f"Book with id: {book_id} not found."}), 404
    try:
        book_description_data = book_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    # Check the isbn admin wants to change not be repeated
    existing_isbn = db.session.query(Book_descriptions).where(Book_descriptions.isbn == book_description_data["isbn"], Book_descriptions.id != book_id).first()
    if existing_isbn:
        return jsonify({"error" : f"isbn can not be repetitive."}), 400
    for key, value in book_description_data.items():
        setattr(book_description, key, value)
    db.session.commit()
    return jsonify({"message" : f"Successfully book description with id: {book_id} updated."}), 200

@book_descriptions_bp.route('/<int:book_id>', methods={'DELETE'})
def delete_book_description(book_id):
    book_description = db.session.get(Book_descriptions, book_id)
    if not book_description:
        return jsonify({"error" : f"Book with id: {book_id} not found."}), 404
    db.session.delete(book_description)
    db.session.commit()
    return jsonify({"message" : f"Successfully deleted book_description with id: {book_id}"}), 200

@book_descriptions_bp.route('/<int:book_id>/add_category/<int:category_id>', methods={'PUT'})
def add_category_to_book(book_id,category_id):
    book = db.session.get(Book_descriptions, book_id)
    category = db.session.get(Categories, category_id)
    if not book:
        return jsonify({"error" : f"Book description with id: {book_id} not found."}), 404
    if not category:
        return jsonify({"error" : f"Category with id: {category_id} not found."}), 404
    if category not in book.categories:
        book.categories.append(category)
        db.session.commit()
        return jsonify({"message" : f"Successfully category with id: {category_id} added to book_description with id:{book_id}."}), 200
    else:
        return jsonify({"message" : f"{category.title} is already added in book description with id:{book_id}."}),200

@book_descriptions_bp.route('/<int:book_id>/remove_category/<int:category_id>', methods={'PUT'})
def remove_category_from_book(book_id,category_id):
    book = db.session.get(Book_descriptions, book_id)
    category = db.session.get(Categories, category_id)
    if not book:
        return jsonify({"error" : f"Book description with id: {book_id} not found."}), 404
    if not category:
        return jsonify({"error" : f"Category with id: {category_id} not found."}), 404
    if category in book.categories:
        book.categories.remove(category)
        db.session.commit()
        return jsonify({"message" : f"Successfully category with id: {category_id} removed from book_description with id:{book_id}."}), 200
    else:
        return jsonify({"message" : f"{category.title} is not in book description with id:{book_id}."}),200
    
@book_descriptions_bp.route('/<int:book_id>', methods={'GET'})
def get_book_descriptions_info(book_id):
    book_description = db.session.get(Book_descriptions,book_id)
    response = {
        "data" : book_description_schema.dump(book_description),
        "categories" : categories_schema.dump(book_description.categories)
    }
    return jsonify(response), 200