from app.models import Users
from app.extensions import ma


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users

user_schema = UserSchema()
users_schema = UserSchema(many=True)
