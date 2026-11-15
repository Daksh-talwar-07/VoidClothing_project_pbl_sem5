from datetime import datetime
from extensions import db
from flask_login import UserMixin


class Customer(UserMixin,db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key = True)
    full_name = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(120),unique=True, nullable=False)
    phone = db.Column(db.String(15),unique=True,nullable=False)
    password = db.Column(db.String(255),nullable=False)
    joined_at = db.Column(db.DateTime, default = datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    email_verified = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    email_verification_otp_hash = db.Column(
        db.String(255),
        nullable=True
    )

    email_verification_otp_expires = db.Column(
        db.DateTime,
        nullable=True
    )

    email_verification_attempts = db.Column(
        db.Integer, 
        default=0
    )

    password_reset_otp_hash = db.Column(
        db.String(255),
        nullable = True
    )

    password_reset_otp_expires = db.Column(
        db.DateTime,
        nullable = True
    )

    password_reset_attempts = db.Column(
        db.Integer,
        default=0
    )


    def __repr__(self):
        return f"<Customer { self.full_name }>"