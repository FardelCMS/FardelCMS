from fardel.ext import db

__all__ = (
    "UserAddress", 
)

class UserAddress(db.Model):
    __tablename__ = "auth_users_address"
    id = db.Column(db.Integer, primary_key=True, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))

    country = db.Column(db.String(128))
    city = db.Column(db.String(256))
    phone = db.Column(db.String(64))
    postal_code = db.Column(db.String(64))
    street_address = db.Column(db.String(256))

    user = db.relationship("User", backref="addresses")

    def dict(self):
        pass