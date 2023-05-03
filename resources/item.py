from flask import request
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from schemas import ItemSchema, ItemUpdateSchema
from db import db
from models.item import ItemModel
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt

blp = Blueprint("Items", __name__, description="Operations on items")

@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):
        jwt = get_jwt()

        if not jwt.get("isAdmin"):
            abort(401, message="This action can do only by a admin user")

        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted"}

    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, request_data, item_id):
        item_data = ItemModel.query.get(item_id)

        if item_data:
            item_data.price = request_data["price"]
            item_data.name = request_data["name"]
        else:
            item_data = ItemModel(id=item_id, **request_data)

        db.session.add(item_data)
        db.session.commit()
        return item_data

@blp.route("/item")
class ItemList(MethodView):
    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, request_data):
        new_item = ItemModel(**request_data)
        try:
            db.session.add(new_item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")

        return new_item

    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()