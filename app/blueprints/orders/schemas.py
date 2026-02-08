from app.extensions import ma
from app.models import Orders, Order_books

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders

order_schema = OrderSchema()
