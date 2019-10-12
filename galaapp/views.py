from flask import Flask, request, render_template, jsonify, json
import datetime

app = Flask(__name__)
app.config.from_object("config")

from .models import *


@app.route("/refilling/<string:user_UID>", methods=["POST"])
def refilling(user_UID):
    req_data = json.loads(request.data)
    user = db.session.query(User).filter_by(UID="%s" % user_UID).first()
    if user:
        user.money += float(req_data["amount"])
    else:
        user = User()
        user.UID = "%s" % user_UID
        user.money = req_data["amount"]
        db.session.add(user)

    transaction = Transaction()
    transaction.user_UID = user.UID
    transaction.counter_id = req_data["counter_id"]
    transaction.computer_MAC = req_data["computer_MAC"]
    transaction.amount = req_data["amount"]
    transaction.time = datetime.datetime.now()
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"user_UID": user.UID, "user_balance": user.money}), 200


@app.route("/buy/<string:user_UID>", methods=["POST"])
def buy(user_UID):
    req_data = json.loads(request.data)
    user = db.session.query(User).filter_by(UID="%s" % user_UID).first()
    products = req_data["shopping_cart"]
    total = 0
    shop_cart = []

    transaction = Transaction()
    transaction.user_UID = user.UID
    transaction.counter_id = req_data["counter_id"]
    transaction.computer_MAC = req_data["computer_MAC"]
    transaction.time = datetime.datetime.now()
    db.session.add(transaction)

    if user:
        for product in products:
            pdt = (
                db.session.query(Product)
                .filter_by(code=product["product_code"])
                .first()
            )

            if pdt:
                product_cost = float(pdt.price) * int(product["quantity"])

                for happy_hour in pdt.happy_hours:
                    if (
                        isinstance(happy_hour.end, datetime.datetime)
                        and isinstance(happy_hour.start, datetime.datetime)
                        and happy_hour.price
                        and happy_hour.start < datetime.datetime.now()
                        and datetime.datetime.now() < happy_hour.end
                    ):
                        product_cost = float(happy_hour.price) * int(
                            product["quantity"]
                        )

                product_quantity = Product_quantity()
                product_quantity.product_code = pdt.code
                product_quantity.quantity = product["quantity"]
                db.session.add(product_quantity)
                transaction.products_quantity.append(product_quantity)

                total += product_cost
            else:
                return "product not found", 404

        if total <= user.money:
            user.money -= total
            transaction.amount = -total
            db.session.commit()
            return jsonify({"user_UID": user.UID, "user_balance": user.money}), 200
        else:
            return jsonify({"user_UID": user.UID, "user_balance": user.money}), 401

    else:
        return "User not found", 404


@app.route("/get_counter_products/<int:counter_id>", methods=["POST"])
def get_counter_products(counter_id):
    counter = db.session.query(Counter).filter_by(id=counter_id).first()
    products = []
    if counter:
        for product in counter.products:
            happy_hours = []
            for happy_hour in product.happy_hours:
                happy_hour_dic = {
                    "start": happy_hour.start,
                    "end": happy_hour.end,
                    "price": happy_hour.price,
                }
                happy_hours.append(happy_hour_dic)

            product_dic = {
                "code": product.code,
                "name": product.name,
                "price": product.price,
                "happy_hours": happy_hours,
                "categorie": product.categorie,
                "sub_categorie": product.sub_categorie,
            }
            products.append(product_dic)

        return jsonify(products), 200
    else:
        return "Counter not found", 404


@app.route("/get_general_history/<int:history_size>", methods=["POST"])
def get_general_history(history_size):
    transactions = (
        db.session.query(Transaction)
        .order_by(Transaction.id.desc())
        .slice(0, history_size)
    )
    trans_list = []
    for transaction in transactions:
        shopping_cart = []
        for product_quantity in transaction.products_quantity:
            shopping_cart.append(
                {
                    "product_code": product_quantity.product_code,
                    "quantity": product_quantity.quantity,
                }
            )

        trans_list.append(
            {
                "id": transaction.id,
                "user_UID": transaction.user_UID,
                "counter_id": transaction.counter_id,
                "computer_MAC": transaction.computer_MAC,
                "shopping_cart": shopping_cart,
                "amount": transaction.amount,
                "time": transaction.time,
            }
        )
    return jsonify(trans_list), 200


@app.route("/get_user_history/<string:user_UID>/<int:history_size>", methods=["POST"])
def get_user_history(user_UID, history_size):
    transactions = (
        db.session.query(Transaction)
        .filter_by(user_UID=user_UID)
        .order_by(Transaction.id.desc())
        .slice(0, history_size)
    )
    trans_list = []
    for transaction in transactions:
        shopping_cart = []
        for product_quantity in transaction.products_quantity:
            shopping_cart.append(
                {
                    "product_code": product_quantity.product_code,
                    "quantity": product_quantity.quantity,
                }
            )

        trans_list.append(
            {
                "id": transaction.id,
                "user_UID": transaction.user_UID,
                "counter_id": transaction.counter_id,
                "computer_MAC": transaction.computer_MAC,
                "shopping_cart": shopping_cart,
                "amount": transaction.amount,
                "time": transaction.time,
            }
        )
    return jsonify(trans_list), 200


@app.route("/get_counter_history/<int:counter_id>/<int:history_size>", methods=["POST"])
def get_counter_history(counter_id, history_size):
    transactions = (
        db.session.query(Transaction)
        .filter_by(counter_id=counter_id)
        .order_by(Transaction.id.desc())
        .slice(0, history_size)
    )
    trans_list = []
    for transaction in transactions:
        shopping_cart = []
        for product_quantity in transaction.products_quantity:
            shopping_cart.append(
                {
                    "product_code": product_quantity.product_code,
                    "quantity": product_quantity.quantity,
                }
            )

        trans_list.append(
            {
                "id": transaction.id,
                "user_UID": transaction.user_UID,
                "counter_id": transaction.counter_id,
                "computer_MAC": transaction.computer_MAC,
                "shopping_cart": shopping_cart,
                "amount": transaction.amount,
                "time": transaction.time,
            }
        )
    return jsonify(trans_list), 200


@app.route(
    "/get_computer_history/<string:computer_MAC>/<int:history_size>", methods=["POST"]
)
def get_computer_history(computer_MAC, history_size):
    transactions = (
        db.session.query(Transaction)
        .filter_by(computer_MAC=computer_MAC)
        .order_by(Transaction.id.desc())
        .slice(0, history_size)
    )
    trans_list = []
    for transaction in transactions:
        shopping_cart = []
        for product_quantity in transaction.products_quantity:
            shopping_cart.append(
                {
                    "product_code": product_quantity.product_code,
                    "quantity": product_quantity.quantity,
                }
            )

        trans_list.append(
            {
                "id": transaction.id,
                "user_UID": transaction.user_UID,
                "counter_id": transaction.counter_id,
                "computer_MAC": transaction.computer_MAC,
                "shopping_cart": shopping_cart,
                "amount": transaction.amount,
                "time": transaction.time,
            }
        )
    return jsonify(trans_list), 200
