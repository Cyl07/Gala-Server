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
    transaction.user_id = user.UID
    transaction.counter_id = req_data["counter_id"]
    transaction.rebuy = float(req_data["amount"])
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"user_UID": user.UID, "amount": user.money}), 200


@app.route("/buy", methods=["POST"])
def buy():
    req_data = json.loads(request.data)
    user = db.session.query(User).filter_by(UID=req_data["UID"]).first()
    products = req_data["Shopping_cart"]
    total = 0
    if user:
        for product in products:
            pdt = db.session.query(Product).filter_by(id=product["product_id"]).first()
            if (
                isinstance(pdt.happy_hour_end, datetime.datetime)
                and isinstance(pdt.happy_hour_start, datetime.datetime)
                and pdt.happy_hour_price
                and pdt.happy_hour_start < datetime.datetime.now()
                and datetime.datetime.now() < pdt.happy_hour_end
            ):
                product_cost = float(pdt.happy_hour_price) * int(product["quantity"])
            else:
                product_cost = float(pdt.price) * int(product["quantity"])

            total += product_cost

        if total <= user.money:
            user.money -= total
            db.session.commit()
            print(user.money)
            return "Transaction done", 200
        else:
            return "You don't have enough money", 401

    else:
        return "User not found", 404
