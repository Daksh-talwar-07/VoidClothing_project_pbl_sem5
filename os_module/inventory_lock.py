import threading

inventory_lock = threading.Lock()


def check_and_add_to_cart(cart, key, product):
    with inventory_lock:

        product_id = str(product.id)

        total_qty_for_product = 0

        for cart_key, qty in cart.items():
            if cart_key.startswith(f"{product_id}_"):
                total_qty_for_product += qty

        if total_qty_for_product >= product.stock:
            return False

        if key in cart:
            cart[key] += 1
        else:
            cart[key] = 1

        return True