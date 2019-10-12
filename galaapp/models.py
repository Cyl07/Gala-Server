from flask_sqlalchemy import SQLAlchemy
from .views import app


db = SQLAlchemy(app)

inventory = db.Table(
    "inventory",
    db.Column("counter_id", db.Integer, db.ForeignKey("counter.id")),
    db.Column("product_id", db.Integer, db.ForeignKey("product.id")),
)

shopping_cart = db.Table(
    "shopping_cart",
    db.Column("product_quantity_id", db.Integer, db.ForeignKey("product_quantity.id")),
    db.Column("transaction_id", db.Integer, db.ForeignKey("transaction.id")),
)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float, nullable=False)
    happy_hours = db.relationship("Happy_Hour", backref="product", lazy=True)
    categorie = db.Column(db.String(64), nullable=False)
    sub_categorie = db.Column(db.String(64), nullable=False)
    counters = db.relationship(
        "Counter", secondary=inventory, backref=db.backref("products", lazy="dynamic")
    )


class Product_quantity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer, nullable=False)
    shopping_carts = db.relationship(
        "Transaction",
        secondary=shopping_cart,
        backref=db.backref("products_quantity", lazy="dynamic"),
    )


class Happy_Hour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)


class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UID = db.Column(db.String(32), nullable=False)
    money = db.Column(db.Integer, nullable=False)
    transactions = db.relationship("Transaction", backref="user", lazy=True)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    counter_id = db.Column(db.String(32), nullable=False)
    amount = db.Column(db.Integer)


db.create_all()
