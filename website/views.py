from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    session,
)
from flask_login import login_required, current_user, login_user
from sqlalchemy import func
from .models import (
    CartItem,
    Favorites,
    Order,
    Product,
    Size,
    User,
    UserCartCount,
    UserFavoritesCount,
)
from datetime import datetime
import json
import random
from typing import Any, Dict, List, Literal, Optional, Union
from . import db

views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home() -> str:
    products: List[Product] = Product.query.all()
    random.shuffle(products)
    random_products: List[Product] = products[:4]
    sizes: List[Size] = Size.query.all()
    cart_items: List[CartItem] = CartItem.query.filter_by(user_id=current_user.id).all()
    user_cart: List[Dict[str, Any]] = []
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        if product:
            item: Dict[str, Any] = {
                "cart_item": cart_item,
                "product": product,
                "quantity": cart_item.quantity,
                "cart_item_id": cart_item.id,
            }
            user_cart.append(item)

    return render_template(
        "base.html",
        user=current_user,
        products=random_products,
        sizes=sizes,
        user_cart=user_cart,
    )


@views.route("/set-language/<lang>")
def set_language(lang) -> Response:
    if lang in ["en", "ru"]:
        session["lang"] = lang
        return redirect(request.referrer or url_for("home"))
    else:
        return redirect(url_for("home"))


@views.route("/cart")
@login_required
def cart() -> str:
    cart_count: int = current_user.get_cart_count()
    cart_items: List[CartItem] = CartItem.query.filter_by(user_id=current_user.id).all()
    user_cart: List[Dict[str, Union[CartItem, Product, str, int]]] = []
    for cart_item in cart_items:
        product: Product = Product.query.get(cart_item.product_id)
        if product:
            size: Size = Size.query.get(cart_item.size_id)
            size_value: Union[str, int] = size.size if size else "0"
            item: Dict[str, Union[CartItem, Product, str, int]] = {
                "cart_item": cart_item,
                "product": product,
                "size": size_value,
                "quantity": cart_item.quantity,
                "cart_item_id": cart_item.id,
            }
            user_cart.append(item)

    return render_template(
        "cart.html", user_cart=user_cart, user=current_user, cart_count=cart_count
    )


@views.route("/favorites")
@login_required
def favorites() -> str:
    favorites_count: int = current_user.get_favorites_count()
    favorites: List[Favorites] = Favorites.query.filter_by(
        user_id=current_user.id
    ).all()
    user_favorites: List[Product] = []

    for favorite in favorites:
        product: Product = Product.query.get(favorite.product_id)
        if product:
            user_favorites.append(product)

    cart_items: List[CartItem] = CartItem.query.filter_by(user_id=current_user.id).all()
    user_cart: List[Dict[str, Any]] = []
    for cart_item in cart_items:
        product: Product = Product.query.get(cart_item.product_id)
        if product:
            size: Size | None = Size.query.get(cart_item.size_id)
            size_value: Any = size.size if size else "0"
            item: Dict[str, Any] = {
                "cart_item": cart_item,
                "product": product,
                "size": size_value,
                "quantity": cart_item.quantity,
                "cart_item_id": cart_item.id,
            }
            user_cart.append(item)

    return render_template(
        "favorites.html",
        favorites_count=favorites_count,
        user_favorites=user_favorites,
        user=current_user,
        user_cart=user_cart,
    )


@views.route("/order")
@login_required
def order() -> str:
    user_orders: List[Order] = Order.query.filter_by(user_id=current_user.id).all()

    processed_orders: List[Dict[str, Any]] = []
    for order in user_orders:
        cart_items = json.loads(order.cart_data)

        processed_order: Dict[str, Any] = {
            "id": order.id,
            "name": order.name,
            "email": order.email,
            "phone": order.phone,
            "country": order.country,
            "comment": order.comment,
            "city": order.city,
            "address": order.address,
            "cart_items": cart_items,
            "total_price": order.total_price,
        }
        processed_orders.append(processed_order)

    return render_template(
        "order.html",
        processed_orders=processed_orders,
        user=current_user,
    )


@views.route("/checkout", methods=["POST", "GET"])
@login_required
def checkout() -> Union[Response, str]:
    if request.method == "POST":
        name: str = request.form.get("name", "")
        email: str = request.form.get("email", "")
        phone: str = request.form.get("phone", "")
        country: str = request.form.get("country", "")
        city: str = request.form.get("city", "")
        address: str = request.form.get("address", "")
        comment: str = request.form.get("comment", "")
        total_price = session.get("total_price")
        cart_items: List[CartItem] = CartItem.query.filter_by(
            user_id=current_user.id
        ).all()
        if not cart_items:
            flash(
                "Your cart is empty. Please add items to your cart before checking out.",
                "warning",
            )
            return redirect(url_for("views.checkout"))

        cart_data: List[Dict[str, Any]] = []
        for cart_item in cart_items:
            product: Product = Product.query.get(cart_item.product_id)
            if product:
                size: Size = Size.query.get(cart_item.size_id)
                size_value: Union[str, int] = size.size if size else "0"
                item: Dict[str, Any] = {
                    "product_id": cart_item.product_id,
                    "name": product.name,
                    "size": size_value,
                    "quantity": cart_item.quantity,
                    "cart_item_id": cart_item.id,
                }
                cart_data.append(item)

        order = Order(
            name=name,
            email=email,
            phone=phone,
            country=country,
            city=city,
            address=address,
            comment=comment,
            timestamp=datetime.now(),
            user_id=current_user.id,
            cart_data=json.dumps(cart_data),
            total_price=total_price,
        )

        db.session.add(order)
        db.session.commit()

        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        user_cart_count = UserCartCount.query.filter_by(user_id=current_user.id).first()
        if user_cart_count:
            user_cart_count.cart_count = 0
        else:
            user_cart_count = UserCartCount(user_id=current_user.id, cart_count=0)

        db.session.add(user_cart_count)
        db.session.commit()

        session["cart_count"] = 0

        session["total_price"] = 0
        session.pop("total_price", None)
        flash("Your order has been placed successfully!", "success")

        return redirect(url_for("views.home"))
    else:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        user_cart = []
        for cart_item in cart_items:
            product = Product.query.get(cart_item.product_id)
            if product:
                size = Size.query.get(cart_item.size_id)
                size_value = size.size if size else "0"
                item = {
                    "cart_item": cart_item,
                    "product": product,
                    "size": size_value,
                    "quantity": cart_item.quantity,
                    "cart_item_id": cart_item.id,
                }
                user_cart.append(item)

        return render_template("checkout.html", user=current_user, user_cart=user_cart)


@views.route("/product")
def product_page() -> str:
    if current_user.is_authenticated:
        category: Any = None
        products: List[Product] = Product.query.all()
        sizes: List[Size] = Size.query.all()
        cart_items: List[CartItem] = CartItem.query.filter_by(
            user_id=current_user.id
        ).all()
        user_cart: List[Dict[str, Any]] = []
        for cart_item in cart_items:
            product: Product = Product.query.get(cart_item.product_id)
            if product:
                item: Dict[str, Any] = {
                    "cart_item": cart_item,
                    "product": product,
                    "quantity": cart_item.quantity,
                    "cart_item_id": cart_item.id,
                }
                user_cart.append(item)
        return render_template(
            "product.html",
            products=products,
            sizes=sizes,
            user=current_user,
            category=category,
            user_cart=user_cart,
        )
    else:
        products: List[Product] = Product.query.all()
        sizes: List[Size] = Size.query.all()
        return render_template(
            "product.html", products=products, sizes=sizes, user=None
        )


@views.route("/product/<category>", methods=["GET"])
def category(category: str) -> str:
    products: List[Product] = Product.query.filter_by(category=category).all()
    cart_items: List[CartItem] = CartItem.query.filter_by(user_id=current_user.id).all()
    user_cart: List[Dict[str, Any]] = []
    for cart_item in cart_items:
        product: Product = Product.query.get(cart_item.product_id)
        if product:
            item: Dict[str, Any] = {
                "cart_item": cart_item,
                "product": product,
                "quantity": cart_item.quantity,
                "cart_item_id": cart_item.id,
            }
            user_cart.append(item)
    return render_template(
        "product.html",
        products=products,
        category=category,
        user=current_user,
        user_cart=user_cart,
    )


@views.route("/search", methods=["GET", "POST"])
def search() -> str:
    if request.method == "GET":
        search_query: str = request.args.get("search_query")
        if search_query is not None:
            products: List = Product.query.filter(
                func.lower(Product.name).like(f"%{search_query.lower()}%")
            ).all()
        else:
            products: list = []
        return render_template(
            "search.html", products=products, query=search_query, user=current_user
        )
    else:
        return render_template("search.html", user=current_user)


@views.route("/add-to-favorites", methods=["POST"])
@login_required
def add_to_favorites() -> Response:
    product_id: Optional[int] = int(request.form.get("product_id"))

    product: Optional[Product] = Product.query.get(product_id)

    if product:
        if not current_user.has_favorited(product):
            current_user.add_to_favorites(product)
            db.session.commit()

            user_favorites_count: Optional[UserFavoritesCount] = (
                UserFavoritesCount.query.filter_by(user_id=current_user.id).first()
            )
            if user_favorites_count:
                user_favorites_count.favorites_count += 1
            else:
                user_favorites_count = UserFavoritesCount(
                    user_id=current_user.id, favorites_count=1
                )
                db.session.add(user_favorites_count)

            db.session.commit()
            flash("Successfully added to your favorites!", "success")
        else:
            flash("Product already exists!", "error")
    else:
        flash("Product is undefined!", "error")

    session["favorites_count"] = (
        UserFavoritesCount.query.filter_by(user_id=current_user.id)
        .first()
        .favorites_count
    )

    return redirect(request.referrer or url_for("views.favorites"))


@views.route("/remove-from-favorites", methods=["POST"])
@login_required
def remove_from_favorites() -> Response:
    product_id: Optional[int] = int(request.form.get("product_id"))

    product: Optional[Product] = Product.query.get(product_id)

    if product:
        if current_user.has_favorited(product):
            current_user.remove_from_favorites(product)
            db.session.commit()

            user_favorites_count: Optional[UserFavoritesCount] = (
                UserFavoritesCount.query.filter_by(user_id=current_user.id).first()
            )
            if user_favorites_count:
                user_favorites_count.favorites_count -= 1
            else:
                user_favorites_count = UserFavoritesCount(
                    user_id=current_user.id, favorites_count=0
                )
                db.session.add(user_favorites_count)

            db.session.commit()

            session["favorites_count"] = user_favorites_count.favorites_count

        else:
            flash("Product does not exist in favorites!", "info")
    else:
        flash("Product is undefined!", "error")

    flash("Successfully remove from your favorites!", "success")

    return redirect(request.referrer or url_for("views.favorites", user=current_user))


@views.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart() -> Response:
    product_id: str = request.form.get("product_id")
    quantity: str = request.form.get("quantity")

    user: User = User.query.get(current_user.id)

    product: Product = Product.query.get(product_id)

    if not product:
        flash("Product is undefined!", "error")
        return redirect(request.referrer or url_for("views.cart", user=current_user))

    if product.get_requires_size() and (
        not request.form.get("size_id") or request.form.get("size_id") == "None"
    ):
        flash("Please select a size", "error")
        return redirect(request.referrer or url_for("views.cart", user=current_user))

    user_cart_count: UserCartCount = UserCartCount.query.filter_by(
        user_id=current_user.id
    ).first()
    if user_cart_count:
        user_cart_count.cart_count += 1
    else:
        user_cart_count = UserCartCount(user_id=current_user.id, cart_count=1)
    db.session.add(user_cart_count)

    flash("Successfully added to your shopping cart!", "success")

    cart_item: CartItem = CartItem.query.filter_by(
        user_id=user.id, product_id=product_id, size_id=request.form.get("size_id")
    ).first()

    if cart_item:
        if quantity is not None:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity += 1
    else:
        cart_item = CartItem(
            user_id=user.id,
            product_id=product_id,
            size_id=request.form.get("size_id"),
            quantity=1,
        )
        db.session.add(cart_item)

    db.session.commit()

    cart_items: List[CartItem] = CartItem.query.filter_by(user_id=user.id).all()
    total_price: int = sum(
        Product.query.get(item.product_id).price * item.quantity for item in cart_items
    )

    session["cart_count"] = user_cart_count.cart_count
    session["total_price"] = total_price

    return redirect(
        request.referrer
        or url_for("views.cart", user=current_user, total_price=total_price)
    )


@views.route("/remove_from_cart", methods=["POST"])
@login_required
def remove_from_cart() -> Response:
    cart_item_id: str = request.form.get("cart_item_id")

    cart_item: CartItem = CartItem.query.get(cart_item_id)
    user_cart_count: UserCartCount = UserCartCount.query.filter_by(
        user_id=current_user.id
    ).first()
    if not cart_item:
        flash("Cart item not found!", "error")
        return redirect(request.referrer or url_for("views.cart", user=current_user))

    if cart_item.quantity == 1:
        db.session.delete(cart_item)
        if user_cart_count:
            user_cart_count.cart_count -= 1
        else:
            user_cart_count = UserCartCount(user_id=current_user.id, cart_count=0)
    else:
        cart_item.quantity -= 1
        if user_cart_count:
            user_cart_count.cart_count -= 1

    db.session.add(user_cart_count)
    db.session.commit()

    session["cart_count"] = user_cart_count.cart_count

    cart_items: List[CartItem] = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price: int = sum(
        Product.query.get(item.product_id).price * item.quantity for item in cart_items
    )
    session["total_price"] = total_price

    flash("Item removed from your shopping cart!", "success")

    return redirect(request.referrer or url_for("views.cart", user=current_user))
