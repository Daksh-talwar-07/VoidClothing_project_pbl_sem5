from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.order import Order

customer = Blueprint("customer", __name__)


@customer.app_context_processor
def customer_data():
    if not current_user.is_authenticated:
        return {}
    return {"order_count": Order.query.filter_by(customer_id=current_user.id).count()}


@customer.route("/customer/orders")
@login_required
def customer_orders():
    orders = Order.query.filter_by(
        customer_id=current_user.id
    ).order_by(Order.id.desc()).all()
    return render_template("customer/orders.html", orders=orders)
