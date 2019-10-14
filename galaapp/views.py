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
    if counter:
        result = {}
        categories = []
        for product in counter.products:
            categories.append(product.categorie)
        categories = list(dict.fromkeys(categories))

        for categorie in categories:
            sub_categories = []
            categorie_dict = {}
            for product in counter.products:
                if product.categorie == categorie:
                    sub_categories.append(product.sub_categorie)
            sub_categories = list(dict.fromkeys(sub_categories))

            print(categorie + "\n")
            for sub_categorie in sub_categories:
                products = []
                sub_categorie_dict = {}
                for product in counter.products:
                    product_dict = {}
                    if product.sub_categorie == sub_categorie:
                        products.append(product)
                        product_dict["uid"] = product.code
                        product_dict["defaultPrice"] = product.price
                        hh_string = ""
                        for happy_hour in product.happy_hours:
                            hh_string += (
                                "{:%Hh%M}".format(happy_hour.start)
                                + " - "
                                + "{:%Hh%M}".format(happy_hour.end)
                                + " = "
                                + "{}".format(happy_hour.price)
                                + " ; "
                            )

                        product_dict["happyHour"] = hh_string[:-3]

                        sub_categorie_dict[product.name] = product_dict
                    else:
                        pass

                categorie_dict[sub_categorie] = sub_categorie_dict
            result[categorie] = categorie_dict
        return jsonify(result), 200
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


@app.route("/refund/<int:transaction_id>", methods=["POST"])
def refund(transaction_id):
    transaction = db.session.query(Transaction).filter_by(id=transaction_id).first()
    if transaction:
        user = db.session.query(User).filter_by(UID=transaction.user_UID).first()
        if user:
            user.money -= transaction.amount
            db.session.delete(transaction)
            db.session.commit()
            return jsonify({"user_UID": user.UID, "user_balance": user.money}), 200
        else:
            return "User not found", 404
    else:
        return "Transaction not found", 404


@app.route("/transfer_money", methods=["POST"])
def transfer_money():
    req_data = json.loads(request.data)
    user1 = db.session.query(User).filter_by(UID=req_data["user1_UID"]).first()
    user2 = db.session.query(User).filter_by(UID=req_data["user2_UID"]).first()
    if user1 and user2:
        if req_data["amount"] <= user2.money:
            user2.money -= req_data["amount"]
            user1.money += req_data["amount"]
            db.session.commit()
            return jsonify(
                {
                    "user1_UID": user1.UID,
                    "user1_balance": user1.money,
                    "user2_UID": user2.UID,
                    "user2_balance": user2.money,
                }
            )
        else:
            return jsonify({"user_UID": user2.UID, "user_balance": user2.money}), 401
    else:
        return "User not found", 404
