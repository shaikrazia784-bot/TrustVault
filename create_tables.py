
from app import app
from extensions import db

with app.app_context():
    db.create_all()
    print("TrustVault tables checked/created successfully!")
