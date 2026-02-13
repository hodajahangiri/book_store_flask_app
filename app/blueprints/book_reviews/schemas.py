from app.models import Reviews
from app.extensions import ma
from app.blueprints.book_descriptions.schemas import BookDescriptionSchema
from app.blueprints.users.schemas import UserSchema

class ReviewSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reviews

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)

class UserReviewSchema(ma.SQLAlchemyAutoSchema):
    book_description = ma.Nested(BookDescriptionSchema)
    class Meta:
        model = Reviews

user_reviews_schema = UserReviewSchema(many=True)

class ReviewUserSchema(ma.SQLAlchemyAutoSchema):
    user = ma.Nested(UserSchema(exclude=['created_at', 'email', 'password', 'phone']))
    class Meta:
        model = Reviews

review_users_schema = ReviewUserSchema(many=True)

