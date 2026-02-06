from app.models import Payments
from app.extensions import ma


class PaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payments

payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)
