from extensions import db

class OrderItem(db.Model):

    __tablename__ = "order_items"
    id = db.Column(db.Integer,primary_key = True)

    order_id = db.Column(db.Integer,db.ForeignKey("orders.id"),nullable=False)
    product_id = db.Column(db.Integer,nullable=False)

    product_name = db.Column(db.String(200),nullable =False)
    size = db.Column(db.String(20),nullable=False)

    quantity = db.Column(db.Integer,nullable=False)

    price = db.Column(db.Integer,nullable = False)
    