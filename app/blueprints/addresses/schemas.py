from app.models import Addresses
from app.extensions import ma


class AddressSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Addresses

address_schema = AddressSchema()
addresses_schema = AddressSchema(many=True)