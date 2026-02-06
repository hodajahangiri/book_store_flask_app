from app.models import Book_descriptions
from app.extensions import ma


class BookDescriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book_descriptions

book_description_schema = BookDescriptionSchema()
book_descriptions_schema = BookDescriptionSchema(many=True)