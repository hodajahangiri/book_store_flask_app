from .schemas import book_favorites_schema
from app.blueprints.favorites import favorites_bp
from app.utils.auth import token_required
from flask import request, jsonify
from app.models import db, Users, Favorites, Book_descriptions
from app.blueprints.book_descriptions.schemas import book_description_schema

# Add a book to favorites
@favorites_bp.route('/<int:book_description_id>', methods=['POST'])
@token_required
def add_favorite(book_description_id):
	user_id = int(request.user_id)
	user = db.session.get(Users, user_id)
	book = db.session.get(Book_descriptions, book_description_id)
	if not user:
		return jsonify({"error": "User not found."}), 404
	if not book:
		return jsonify({"error": "Book not found."}), 404
	existed_favorite = db.session.query(Favorites).where((Favorites.user_id == user_id) & (Favorites.book_description_id == book_description_id)).first()
	if existed_favorite:
		return jsonify({"error": "Book already in favorites."}), 400
	favorite = Favorites(user_id=user_id, book_description_id=book_description_id)
	db.session.add(favorite)
	db.session.commit()
	return jsonify({"message": f"{book.title} added to your favorites."}), 200

# Get all favorites for a book
@favorites_bp.route('/book/<int:book_description_id>', methods=['GET'])
def get_book_favorites(book_description_id):
	book = db.session.get(Book_descriptions, book_description_id)
	if not book:
		return jsonify({"error": "Book not found."}), 404
	response = {
        "book_info" : book_description_schema.dump(book),
        "favorites" : book_favorites_schema.dump(book.favorites)
    }
	return jsonify(response), 200

# Remove a book from favorites
@favorites_bp.route('/<int:favorite_id>', methods=['DELETE'])
@token_required
def delete_favorite(favorite_id):
	user_id = int(request.user_id)
	user = db.session.get(Users, user_id)
	favorite = db.session.get(Favorites, favorite_id)
	if not favorite:
		return jsonify({"error": "Favorite not found."}), 404
	if not user:
		return jsonify({"error": "User not found."}), 404
	if favorite.user_id != user_id:
		return jsonify({"error": "You can only delete your own favorites."}), 403
	db.session.delete(favorite)
	db.session.commit()
	return jsonify({"message": "Book removed from favorites successfully."}), 200


@favorites_bp.route('/<int:book_description_id>', methods=['PUT'])
@token_required
def toggle_favorite(book_description_id):
	user_id = int(request.user_id)
	user = db.session.get(Users, user_id)
	book = db.session.get(Book_descriptions, book_description_id)
	if not user:
		return jsonify({"error": "User not found."}), 404
	if not book:
		return jsonify({"error": "Book not found."}), 404
	existed_favorite = db.session.query(Favorites).where((Favorites.user_id == user_id) & (Favorites.book_description_id == book_description_id)).first()
	if existed_favorite:
		db.session.delete(existed_favorite)
		db.session.commit()
		return jsonify({"message": "Book removed from favorites successfully."}), 200
	favorite = Favorites(user_id=user_id, book_description_id=book_description_id)
	db.session.add(favorite)
	db.session.commit()
	return jsonify({"message": f"{book.title} added to your favorites."}), 200
