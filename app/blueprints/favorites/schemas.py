from app.models import Favorites
from app.extensions import ma
from app.blueprints.book_descriptions.schemas import BookDescriptionSchema
from app.blueprints.users.schemas import UserSchema

class FavoriteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Favorites

favorite_schema = FavoriteSchema()
favorites_schema = FavoriteSchema(many=True)


class UserFavoriteSchema(ma.SQLAlchemyAutoSchema):
    book_description = ma.Nested(BookDescriptionSchema)
    class Meta:
        model = Favorites

user_favorites_schema = UserFavoriteSchema(many=True)

class BookFavoriteSchema(ma.SQLAlchemyAutoSchema):
    user = ma.Nested(UserSchema)
    class Meta:
        model = Favorites

book_favorites_schema = BookFavoriteSchema(many=True)