import cloudinary
import cloudinary.uploader
import urllib.parse
from flask import Response
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from extensions import db, login_manager, csrf, limiter
from models.order import Order
from models.order_item import OrderItem
from models.customer import Customer
from config import Config
from datetime import timedelta , datetime
from flask import Flask, render_template, request , redirect , session,flash,url_for
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash
import os
from flask_login import login_required,current_user
from routes.auth import auth
from routes.customer import customer

from utils.email_service import send_email



from multiprocessing import Process
from os_module.process_manager import generate_inventory_report
from flask import send_file
from os_module.task_manager import start_background_task

from os_module.inventory_lock import check_and_add_to_cart


from store_config import (
    STORE_NAME,
    STORE_LOGO,
    STORE_PHONE,
    STORE_INSTAGRAM,
    STORE_ADDRESS,
    CATEGORIES,
    BG_COLOR,
    BG_ALT_COLOR,
    SURFACE_COLOR,
    SURFACE_2_COLOR,
    SURFACE_3_COLOR,
    SURFACE_4_COLOR,
    TEXT_COLOR,
    TEXT_SECONDARY_COLOR,
    TEXT_SOFT_COLOR,
    MUTED_COLOR,
    BORDER_COLOR,
    BORDER_STRONG_COLOR,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR,
    ACCENT_2_COLOR,
    ACCENT_SOFT_COLOR,
    ACCENT_COLOR_RGB,
    SUCCESS_COLOR,
    SUCCESS_COLOR_RGB,
    DANGER_COLOR,
    DANGER_COLOR_RGB,
    WARNING_COLOR,
    WARNING_COLOR_RGB,
    INFO_COLOR,
    INFO_COLOR_RGB,
    HIGHLIGHT_COLOR,
    HIGHLIGHT_COLOR_RGB,
    SHADOW_COLOR,
)  

load_dotenv()
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)
app = Flask(__name__)
app.config.from_object(Config)



db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"

csrf.init_app(app)


limiter.init_app(app)

app.permanent_session_lifetime = timedelta(hours=10)

app.register_blueprint(auth)
app.register_blueprint(customer)



ALLOWED_EXTENSIONS = {"png" , "jpg" , "jpeg" , "webp"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_logged_in():
    if "admin" not in session or "admin_login_time" not in session:
        return False
    
    login_time = datetime.fromisoformat(session["admin_login_time"])

    if datetime.utcnow() - login_time > timedelta(minutes = 30):
        session.pop("admin",None)
        session.pop("admin_login_time", None)
        return False
    return True



@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))

ALLOWED_SIZES = ["S", "M", "L", "XL"]


class Product(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    price=db.Column(db.Integer,nullable=False)
    image=db.Column(db.Text,nullable=False)
    description = db.Column(db.Text)
    sizes = db.Column(db.String(100), nullable=False)   
    stock = db.Column(db.Integer, nullable=False,default=1)
    category = db.Column(db.String(100),nullable = False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    rating = db.Column(db.Integer, nullable = False)
    review = db.Column(db.Text, nullable = False)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable = False
    )

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable = False , unique = True)
    password = db.Column(db.String(255), nullable=False)



with app.app_context():
    db.create_all()

    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD")

    existing_admin = Admin.query.filter_by(username=admin_username).first()

    if not existing_admin and admin_password:
        admin = Admin(
            username=admin_username,
            password=generate_password_hash(admin_password)
        )
        db.session.add(admin)
        db.session.commit()

    elif existing_admin and admin_password:
        existing_admin.password = generate_password_hash(admin_password)
        db.session.commit()







@app.route("/")
def home():
    products = Product.query.all()
    return render_template("shop/home.html",products=products)

@app.route("/collection")
def collection():
    search = request.args.get("search")
    category = request.args.get("category")
    products = Product.query
    if category and category != "All":
        products = products.filter_by(category = category)
    
    if search:
        products = products.filter(
            Product.name.ilike(f"%{search}%")
        )
    products = products.all()
    return render_template(
        "shop/collection.html",
        products=products,
        search=search,
        category=category
    )

@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get(product_id)
    if not product :
        return render_template("customer/404.html"),404
    
    related_products = Product.query.filter(
        Product.id != product.id,
        Product.category == product.category
    ).limit(4).all()
    
    reviews = Review.query.filter_by(
        product_id = product.id
    ).all()

    return render_template("shop/product.html",product=product,related_products = related_products,reviews=reviews)

@app.route("/add-review/<int:id>",methods=["POST"])
@limiter.limit("10 per hour")
def add_review(id):
    if not Product.query.get(id):
        return render_template("customer/404.html"),404
    name = request.form.get("name","").strip()[:100]
    review = request.form.get("review","").strip()[:1000]
    try:
        rating = int(request.form.get("rating",""))
    except ValueError:
        rating = 0
    if not name or not review or not 1 <= rating <= 5:
        flash("Please enter your name, a rating (1-5) and a review ⚠️")
        return redirect(f"/product/{id}")

    new_review = Review(
        name = name,
        rating = rating,
        review = review,
        product_id = id
    )
    db.session.add(new_review)
    db.session.commit()
    flash("Review submitted ⭐")
    return redirect(f"/product/{id}")

@app.context_processor
def branding_context():
    cart = session.get("cart", {})
    count = sum(cart.values())

    return dict(
        cart_count=count,
        categories=CATEGORIES,
        store_name=STORE_NAME,
        store_logo=STORE_LOGO,
        store_phone=STORE_PHONE,
        store_instagram=STORE_INSTAGRAM,
        store_address=STORE_ADDRESS,
        bg_color=BG_COLOR,
        bg_alt_color=BG_ALT_COLOR,
        surface_color=SURFACE_COLOR,
        surface_2_color=SURFACE_2_COLOR,
        surface_3_color=SURFACE_3_COLOR,
        surface_4_color=SURFACE_4_COLOR,
        text_color=TEXT_COLOR,
        text_secondary_color=TEXT_SECONDARY_COLOR,
        text_soft_color=TEXT_SOFT_COLOR,
        muted_color=MUTED_COLOR,
        border_color=BORDER_COLOR,
        border_strong_color=BORDER_STRONG_COLOR,
        primary_color=PRIMARY_COLOR,
        secondary_color=SECONDARY_COLOR,
        accent_color=ACCENT_COLOR,
        accent_2_color=ACCENT_2_COLOR,
        accent_soft_color=ACCENT_SOFT_COLOR,
        accent_color_rgb=ACCENT_COLOR_RGB,
        success_color=SUCCESS_COLOR,
        success_color_rgb=SUCCESS_COLOR_RGB,
        danger_color=DANGER_COLOR,
        danger_color_rgb=DANGER_COLOR_RGB,
        warning_color=WARNING_COLOR,
        warning_color_rgb=WARNING_COLOR_RGB,
        info_color=INFO_COLOR,
        info_color_rgb=INFO_COLOR_RGB,
        highlight_color=HIGHLIGHT_COLOR,
        highlight_color_rgb=HIGHLIGHT_COLOR_RGB,
        shadow_color=SHADOW_COLOR,
    )

@app.route("/cart")
def cart():
    cart = session.get("cart", {})

    cart_items = []
    total = 0

    for key, qty in cart.items():
        try:
            product_id, size = key.split("_", 1)
            product = Product.query.get(int(product_id))
        except (ValueError, TypeError):
            continue

        if product:
            subtotal = product.price * qty
            total += subtotal

            cart_items.append({
                "product": product,
                "size": size,
                "qty": qty,
                "subtotal": subtotal,
                "key": key
            })

    return render_template("shop/cart.html", cart_items=cart_items, total=total)


@app.route("/add-to-cart/<int:id>",methods=["POST"])
def add_to_cart(id):
    product = Product.query.get(id)
    if not product:
        return "Product not found",404

    selected_size = request.form.get("size","")
    if selected_size not in product.sizes.split(","):
        flash("Please select a size ⚠️")
        return redirect(f"/product/{id}")

    cart = session.get("cart",{})
    key = f"{id}_{selected_size}"

    total_qty_for_product = sum(
        qty for cart_key, qty in cart.items()
        if cart_key.startswith(f"{id}_")
    )

    if check_and_add_to_cart(cart,key,product):
        flash("Product added to cart ✅")
    else:
        flash("Stock limit reached ⚠️")

    session["cart"] = cart
    return redirect("/cart")

@app.route("/remove-from-cart/<key>")
def remove_from_cart(key):
    cart = session.get("cart",{})
    if key in cart:
        del cart[key]
    session["cart"] = cart
    flash("Product removed ✅")
    return redirect("/cart")

@app.route("/cart/increase/<key>")
def increase_qty(key):
    cart = session.get("cart",{})
    if key in cart:
        product_id = key.split("_")[0]
        product = Product.query.get(int(product_id))
        total_for_product = sum(
            qty for k, qty in cart.items() if k.startswith(f"{product_id}_")
        )
        if product and total_for_product < product.stock:
            cart[key]+=1
        else:
            flash("Stock limit reached ⚠️")
    session["cart"] = cart
    return redirect("/cart")

@app.route("/cart/decrease/<key>")
def decrease_qty(key):
    cart = session.get("cart",{})
    if key in cart:
        if cart[key] > 1:
            cart[key]-=1
        else:
            del cart[key]
    session["cart"] = cart
    return redirect("/cart")


@app.route("/checkout", methods=["GET", "POST"])
@login_required
@limiter.limit("30 per hour")
def checkout():

    cart = session.get("cart", {})

    cart_items = []
    total = 0

    for key, qty in cart.items():
        try:
            product_id, size = key.split("_", 1)
            product = Product.query.get(int(product_id))
        except (ValueError, TypeError):
            continue

        if product:
            subtotal = product.price * qty
            total += subtotal

            cart_items.append({
                "product": product,
                "size": size,
                "qty": qty,
                "subtotal": subtotal,
                "key": key
            })

    if not cart_items:
        flash("Your cart is empty ⚠️")
        return redirect("/cart")

    if request.method == "POST":
        qty_by_product = {}
        for item in cart_items:
            p = item["product"]
            qty_by_product[p.id] = qty_by_product.get(p.id, 0) + item["qty"]
            if qty_by_product[p.id] > p.stock:
                flash(f"Only {p.stock} left of {p.name} ⚠️")
                return redirect("/cart")

        name = request.form.get("name","").strip()[:100]
        phone = request.form.get("phone","").strip()[:20]
        address = request.form.get("address","").strip()[:500]
        if not name or not phone or not address:
            flash("Please fill all the fields ⚠️")
            return redirect("/checkout")

        order = Order(
            customer_id = current_user.id,
            total_price = total,
            discount = 0,
            final_price = total,
            status = "pending",
            source = "whatsapp"
        )
        db.session.add(order)
        db.session.flush()

        for item in cart_items:
            product = item["product"]
            order_item = OrderItem(
                order_id=order.id,
                product_id = product.id,
                product_name = product.name,
                size=item["size"],
                quantity=item["qty"],
                price=product.price
            )
            db.session.add(order_item)

        db.session.commit()

        message = "🛒 NEW ORDER\n\n"
        message += f"Name: {name}\n"
        message += f"Phone: {phone}\n"
        message += f"Address: {address}\n\n"

        message += "Items:\n"

        for item in cart_items:
            product = item["product"]
            size = item["size"]
            qty = item["qty"]
            subtotal = item["subtotal"]

            message += f"- {product.name} | Size: {size} | Qty: {qty} = ₹{subtotal}\n"

        message += f"\nTotal: ₹{total}"

        seller_number = STORE_PHONE
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/{seller_number}?text={encoded_message}"

        session.pop("cart", None)

        return redirect(whatsapp_url)

    return render_template(
        "shop/checkout.html",
        cart_items=cart_items,
        total=total
    )

@app.route("/admin/products", methods=["GET", "POST"])
@limiter.limit("20 per minute")
def admin_products():

    if not admin_logged_in():
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"]
        price = request.form["price"]
        stock = int(request.form["stock"])
        image = request.files["image"]

        if not allowed_file(image.filename):
            flash("Only image files are allowed ⚠️")
            return redirect("/admin/products")

        category = request.form["category"]
        if category not in {c["slug"] for c in CATEGORIES}:
            flash("Please choose a valid category ⚠️")
            return redirect("/admin/products")

        sizes = request.form.getlist("sizes")
        sizes = [s for s in sizes if s in ALLOWED_SIZES]

        if len(sizes) == 0:
            flash("Please select at least one size ⚠️")
            return redirect("/admin/products")

        max_sizes_allowed = min(stock, 4)

        if len(sizes) > max_sizes_allowed:
            flash(f"For stock {stock} you can select at most {max_sizes_allowed} sizes ⚠️")
            return redirect("/admin/products")

        sizes = ",".join(sizes)

        upload_result = cloudinary.uploader.upload(
            image,
            folder="void_clothing/products"
        )

        filename = upload_result["secure_url"]

        description = request.form["description"]

        new_product = Product(
            name=name,
            price=price,
            stock=stock,
            image=filename,
            description=description,
            sizes=sizes,
            category=category
        )

        db.session.add(new_product)
        db.session.commit()

        flash("Product added successfully ✅")

        return redirect("/admin/products")

    products = Product.query.all()

    return render_template(
        "admin/admin.html",
        products=products
    )

@app.route("/admin")
@limiter.limit("20 per minute")
def admin():
    if not admin_logged_in():
        return redirect("/login")

    products = Product.query.all()
    customers = Customer.query.all()
    orders = Order.query.all()

    total_products = len(products)
    total_customers = len(customers)
    total_orders = len(orders)

    out_of_stock = 0

    for product in products:
        if product.stock == 0:
            out_of_stock+=1

    completed = [o for o in orders if o.status == "completed"]

    revenue = sum(o.final_price for o in completed)

    today = datetime.utcnow().date()

    today_revenue = sum(
        o.final_price 
        for o in completed
        if o.created_at.date() == today
    )

    week_start = today - timedelta(days = today.weekday())

    week_revenue = sum(
        o.final_price
        for o in completed
        if week_start <= o.created_at.date() <= today
    )

    month_start = today.replace(day=1)

    month_revenue = sum(
        o.final_price
        for o in completed
        if month_start <= o.created_at.date() <= today
    )
    
    return render_template(
        "admin/dashboard.html",
        total_products = total_products,
        out_of_stock=out_of_stock,
        total_orders=total_orders,
        revenue=revenue,
        total_customers=total_customers,
        today_revenue=today_revenue,
        week_revenue=week_revenue,
        month_revenue=month_revenue
        )

@app.route("/admin/orders")
@limiter.limit("30 per minute")
def admin_orders():
    if not admin_logged_in():
        return redirect("/login")

    orders = Order.query.order_by(
        Order.id.desc()
    ).all()

    return render_template(
        "admin/orders.html",
        orders=orders
    )

@app.route("/admin/orders/<int:order_id>")
@limiter.limit("30 per minute")
def admin_order_details(order_id):

    if not admin_logged_in():
        return redirect("/login")

    order = Order.query.get_or_404(order_id)

    customer = Customer.query.get(
        order.customer_id
    )

    items = OrderItem.query.filter_by(
        order_id=order.id
    ).all()

    return render_template(
        "admin/order_details.html",
        order=order,
        customer=customer,
        items=items
    )

@app.route("/admin/orders/<int:order_id>/status",methods=["POST"])
def update_order_status(order_id):

    if not admin_logged_in():
        return redirect("/login")

    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    allowed_statuses = {
        "pending",
        "processing",
        "out_for_delivery",
        "completed",
        "cancelled"
    }
    if new_status not in allowed_statuses:
        flash("Invalid order status ⚠️")
        return redirect(url_for("admin_order_details",order_id=order.id))
    order.status = new_status
    db.session.commit()

    flash("Order status updated successfully ✅")

    return redirect(url_for("admin_order_details",order_id=order.id))


@app.route("/admin/customers")
@limiter.limit("30 per minute")
def admin_customer():
    if not admin_logged_in():
        return redirect("/login")
    
    customers = Customer.query.order_by(
            Customer.id.desc()
    ).all()

    return render_template(
        "admin/customers.html",
        customers=customers
    )


@app.route("/admin/delete/<int:id>", methods=["POST"])
def delete_product(id):
    if not admin_logged_in():
        return redirect("/login")
    product = Product.query.get(id)
    if product:
        Review.query.filter_by(product_id=id).delete()

        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully ✅")
    return redirect("/admin/products")

@app.route("/admin/edit/<int:id>",methods=["GET","POST"])
def edit_product(id):
    if not admin_logged_in():
        return redirect("/login")
    product = Product.query.get(id)
    if not product:
        return "Product not found", 404
    if request.method == "POST":
        product.name = request.form["name"]
        product.price = request.form["price"]
        product.stock = int(request.form["stock"])
        product.category = request.form["category"]
        product.description = request.form["description"]
        sizes = request.form.getlist("sizes")
        sizes = [s for s in sizes if s in ALLOWED_SIZES]

        if len(sizes) == 0:
            flash("Please select at least one size ⚠️")
            return redirect(f"/admin/edit/{id}")

        max_sizes_allowed = min(product.stock, 4)

        if len(sizes) > max_sizes_allowed:
            flash(f"For stock {product.stock} you can select at most {max_sizes_allowed} sizes ⚠️")
            return redirect(f"/admin/edit/{id}")

        product.sizes = ",".join(sizes)
        image = request.files.get("image")

        if image and image.filename != "":
            if not allowed_file(image.filename):
                flash("Only image files are allowed ⚠️")
                return redirect(f"/admin/edit/{id}")
            upload_result = cloudinary.uploader.upload(
                image,
                folder="void_clothing/products"
            )

            product.image = upload_result["secure_url"]

        db.session.commit()
        flash("Product edited successfully ✅")
        return redirect("/admin/products")
    
    return render_template("admin/edit.html",product=product)



@app.route("/admin/generate-inventory-report", methods=["POST"])
def generate_inventory_report_route():
    if not admin_logged_in():
        return redirect("/login")

    products = [
        {"id": p.id, "name": p.name, "price": p.price,
         "stock": p.stock, "category": p.category}
        for p in Product.query.all()
    ]

    path = generate_inventory_report(products)
    start_background_task("Inventory report PDF generated")   # thread wala part same rahega

    return send_file(os.path.abspath(path), as_attachment=True,
                     download_name="inventory_report.pdf")

@app.route("/login",methods=["GET","POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password,password):
            session["admin"] = username
            session["admin_login_time"] = datetime.utcnow().isoformat()
            return redirect("/admin")
        
        error = "Invalid username or password. Please enter correct details."
        return render_template("auth/login.html", error=error)
    return render_template("auth/login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    session.pop("admin_login_time",None)
    return redirect("/login")

@app.route("/cartzero")
def cart_to_zero():
    session.pop("cart",None)
    return redirect("/cart")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("customer/404.html"),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("customer/500.html"),500
    
@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("customer/429.html"),429

@app.route("/privacy")
def privacy():
    return render_template("customer/privacy.html")


@app.route("/terms")
def terms():
    return render_template("customer/terms.html")

@app.route("/shipping")
def shipping():
    return render_template("customer/shipping.html")

@app.route("/robots.txt")
def robots_txt():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        f"Sitemap: {request.url_root.rstrip('/')}/sitemap.xml\n"
    )
    return body, 200, {"Content-Type": "text/plain"}

@app.route("/sitemap.xml")
def sitemap():
    products = Product.query.all()
    pages = [
        "/",
        "/collection",
        "/privacy",
        "/terms",
        "/shipping"
    ]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        xml += f"""
        <url>
            <loc>{request.url_root.rstrip('/')}{page}</loc>
        </url>
"""
    for product in products:
        xml += f"""
    <url>
        <loc>{request.url_root.rstrip('/')}/product/{product.id}</loc>
    </url>
"""
    xml += "</urlset>"

    return Response(xml, mimetype="application/xml")   

@app.route("/admin/toggle-stock/<int:id>" , methods=["POST"])
def toggle_stock(id):
    if not admin_logged_in():
        return redirect("/login")
    
    product = Product.query.get(id)

    if product:
        if product.stock > 0:
            product.stock = 0
            flash("Product marked as Out of Stock ⚠️")
        else:
            product.stock = 1
            flash("Product marked as Available ✅")
        
        db.session.commit()
    
    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=os.getenv("FLASK_DEBUG") == "1")
    