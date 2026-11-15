from datetime import datetime
from extensions import db

class Order(db.Model):

    __tablename__ = "orders"

    id = db.Column(db.Integer,primary_key = True)

    customer_id = db.Column(db.Integer,db.ForeignKey("customers.id"),nullable = False)
    total_price = db.Column(db.Integer,nullable=False)

    discount = db.Column(db.Integer,default=0)
    final_price = db.Column(db.Integer,nullable=False)

    status = db.Column(db.String(30),default="pending")
    source = db.Column(db.String(30),default="whatsapp")
    
    created_at = db.Column(db.DateTime,default = datetime.utcnow)


