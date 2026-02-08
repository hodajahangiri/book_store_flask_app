from app.models import Carts, Cart_books
from app.extensions import ma


class CartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Carts

cart_schema = CartSchema()

