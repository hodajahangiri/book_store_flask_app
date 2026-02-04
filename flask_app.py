from app import create_app
from app.models import db


# Create app
app = create_app('DevelopmentConfig')

# Allow flask to access configurations and db
with app.app_context():
    # db.drop_all()
    # Create all tables from models
    db.create_all()

# Run the app
app.run()