from flask_sqlalchemy import SQLAlchemy

from .views import app

db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float, nullable=False)
    happy_hour_start = db.Column(db.DateTime)
    happy_hour_end = db.Column(db.DateTime)
    happy_hour_price = db.Column(db.Integer)
    categorie = db.Column(db.String(64), nullable=False)
    sub_categorie = db.Column(db.String(64), nullable=False)

    def __init__(self, name, price, categorie, sub_categorie):
        self.name = name
        self.price = price
        self.categorie = categorie
        self.sub_categorie = sub_categorie

    def add_happy_hour(self, happy_hour_start, happy_hour_end, happy_hour_price):
        self.happy_hour_start = happy_hour_start
        self.happy_hour_end = happy_hour_end
        self.happy_hour_price = happy_hour_price


class User(db.Model):
    UID = db.Column(db.Integer, primary_key=True)
    money = db.Column(db.Integer, nullable=False)
    transfers = db.relationship("Transfer", backref="user", lazy=True)

    def __init__(self, UID, money):
        self.UID = UID
        self.money = money


Shopping_Cart = db.Table(
    "shopping cart",
    db.Column(
        "transfer_id", db.Integer, db.ForeignKey("transfer.id"), primary_key=True
    ),
    db.Column("product_id", db.Integer, db.ForeignKey("product.id"), primary_key=True),
    db.Column("quantity", db.Integer, nullable=False),
)


class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.UID"), nullable=False)
    MAC = db.Column(db.String(12), nullable=False)
    rebuy = db.Column(db.Integer)
    shopping_cart = db.relationship(
        "Product",
        secondary=Shopping_Cart,
        lazy="subquery",
        backref=db.backref("transfer", lazy=True),
    )

    def __init__(self, user_id, MAC):
        self.user_id = user_id
        self.MAC = MAC


db.create_all()
