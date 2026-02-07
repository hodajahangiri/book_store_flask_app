from app.models import Categories
from app.extensions import ma


class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Categories

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)