from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy


# Create Base Class
class Base(DeclarativeBase):
    pass

# instantiate SQLAlchemy db
db = SQLAlchemy(model_class=Base)