from .schemas import review_schema, reviews_schema, review_users_schema
from app.blueprints.book_reviews import reviews_bp
from app.utils.auth import token_required
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import db, Users, Reviews, Book_descriptions
from app.blueprints.book_descriptions.schemas import book_description_schema

@reviews_bp.route('/<int:book_description_id>', methods={'POST'})
@token_required
def create_review(book_description_id):
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    book = db.session.get(Book_descriptions, book_description_id)
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    if not book:
        return jsonify({"error" : f"Book not found."}), 404
    try:
        review_data = review_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error_message" : e.messages}), 400
    # Each user can add only one review for each book 
    existed_review = db.session.query(Reviews).where((Reviews.user_id == user_id) & (Reviews.book_description_id == book_description_id)).first()
    if existed_review:
        return jsonify({"error" : f"You've already added a review for this book."}), 400
    review_data["user_id"] = user_id
    review_data["book_description_id"] = book_description_id
    new_review = Reviews(**review_data)
    db.session.add(new_review)
    db.session.commit()
    return review_schema.jsonify(new_review), 201

@reviews_bp.route('/book/<int:book_description_id>', methods={'GET'})
def get_reviews(book_description_id):
    book = db.session.get(Book_descriptions, book_description_id)
    if not book:
        return jsonify({"error" : f"Book not found."}), 404
    response = {
        "book_info" : book_description_schema.dump(book),
        "reviews" : review_users_schema.dump(book.reviews)
    }
    return jsonify(response), 200

@reviews_bp.route('/all')
def get_all_reviews():
    reviews = db.session.query(Reviews).all()
    return reviews_schema.jsonify(reviews), 200

@reviews_bp.route('/<int:review_id>')
def get_review(review_id):
    review = db.session.get(Reviews, review_id)
    return reviews_schema.jsonify(review), 200

@reviews_bp.route('<int:review_id>', methods={'PUT'})
@token_required
def update_review(review_id):
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    review = db.session.get(Reviews, review_id)
    if not review:
        return jsonify({"error" : f"Review not found."}), 404
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    if review not in user.reviews:
        return jsonify({"error" : f"You can not update this review."}), 404
    try:
        review_data = review_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error_message" : e.messages}), 400
    for key, value in review_data.items():
        setattr(review, key, value)
    db.session.commit()
    return jsonify({"message" : "Your review successfully updated"}), 200

@reviews_bp.route('<int:review_id>', methods={'DELETE'})
@token_required
def delete_payment(review_id):
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    review = db.session.get(Reviews, review_id)
    if not review:
        return jsonify({"error" : f"Review not found."}), 404
    if not user:
        return jsonify({"error" : f"User not found."}), 404
    if review in user.reviews:
        user.reviews.remove(review)
        db.session.delete(review)
        db.session.commit()
        return jsonify({"message" : "Your review successfully deleted"}), 200
    else:
        return jsonify({"message": "This review in not in your reviews"}), 200