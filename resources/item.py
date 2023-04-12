import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from db import items, stores

blp = Blueprint("Items", __name__, description="Operations on items")

@blp.route("/item/<string:item_id>")
class Item(MethodView):
    def get(self, item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(404, message="Item not found!")

    def delete(self, item_id):
        try:
            del items[item_id]
            return {"message": "Success delete!"}
        except KeyError:
            abort(404, message="Item not found!")

    def put(self, item_id):
        request_data = request.get_json()

        if item_id not in items:
            abort(404, message="Item not found!")

        for item in items.values():
            if item["name"] == request_data["name"] and item["store_id"] == items[item_id]["store_id"]:
                abort(400, message="Item already exist!")  

        item_data = items[item_id]
        item_data |= request_data
        return item_data, 200


@blp.route("/item")
class ItemList(MethodView):
    def post(self):
        request_data = request.get_json()

        if request_data["store_id"] not in stores:
            abort(404, message="Store not found!")

        for item in items.values():
            if item["name"] == request_data["name"] and item["store_id"] == request_data["store_id"]:
                abort(400, message="Item already exist!")  

        item_id = uuid.uuid4().hex
        new_item = { **request_data, "id": item_id }
        items[item_id] = new_item
        return new_item, 201

    def get(self):
        return {"items": list(items.values())}