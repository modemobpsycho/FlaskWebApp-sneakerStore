from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import JSON, DateTime
from sqlalchemy.sql import func
from . import db


class CustomSessionModel(db.Model):
    __tablename__: str = "sessions"

    session_id = db.Column(db.String(255), primary_key=True)
    data = db.Column(db.Text)
    expiry = db.Column(db.DateTime)
    modified = db.Column(db.DateTime, default=datetime.utcnow)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    category = db.Column(db.String(100))
    requires_size = db.Column(db.Boolean, default=False)

    sizes = db.relationship("Size", backref="product", cascade="all, delete-orphan")

    favorites = db.relationship(
        "User", secondary="favorites", backref=db.backref("favorites", lazy="dynamic")
    )

    def get_requires_size(self):
        return self.requires_size


class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Boolean, nullable=False, default=True)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    size_id = db.Column(db.Integer, db.ForeignKey("size.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)


class Favorites(db.Model):
    __tablename__ = "favorites"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship(
        "User", backref=db.backref("favorites_assoc", cascade="all, delete-orphan")
    )

    product = db.relationship(
        "Product", backref=db.backref("users_assoc", cascade="all, delete-orphan")
    )


class UserCartCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    cart_count = db.Column(db.Integer, default=0)


class UserFavoritesCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    favorites_count = db.Column(db.Integer, default=0)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    favorite_products = db.relationship(
        "Product", secondary="favorites", backref=db.backref("users", lazy="dynamic")
    )
    cart_items = db.relationship("CartItem", backref="user", lazy="dynamic")

    def add_to_favorites(self, product) -> None:
        if product not in self.favorite_products:
            self.favorite_products.append(product)

    def has_favorited(self, product) -> bool:
        return product in self.favorites

    def get_favorites_count(self) -> int:
        return Favorites.query.filter_by(user_id=self.id).count()

    def get_favorites(self):
        return self.favorites.all()

    def remove_from_favorites(self, product) -> None:
        if product in self.favorite_products:
            self.favorite_products.remove(product)

    def get_cart_count(self) -> int:
        return CartItem.query.filter_by(user_id=self.id).count()

    def has_cart(self, product) -> bool:
        return product in self.cart_items


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.Text)
    timestamp = db.Column(DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=False)
    cart_data = db.Column(JSON)
    total_price = db.Column(db.Float, nullable=False, default=0.0)

    products = db.relationship(
        "Product",
        secondary="order_product",
        backref=db.backref("orders", lazy="dynamic"),
    )


order_product = db.Table(
    "order_product",
    db.Column("order_id", db.Integer, db.ForeignKey("order.id"), primary_key=True),
    db.Column("product_id", db.Integer, db.ForeignKey("product.id"), primary_key=True),
)
