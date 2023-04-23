import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from schemas import StoreSchema
from db import db
from models.store import StoreModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

blp = Blueprint("Stores", __name__, description="Operations on stores")

@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404()
        return store
        
    def delete(self, store_id):
        try:
            del stores[store_id]
            return {"message": "Success delete!"}
        except KeyError:
            abort(404, message="Store not found!")

    @blp.response(200, StoreSchema)
    def put(self, store_id):
        request_data = request.get_json()

        if store_id not in stores:
            abort(404, message="Store not found!")

        for store in stores.values():
            if store["name"] == request_data["name"]:
                abort(400, message="Store already exists.")

        store_data = stores[store_id]
        store_data |= request_data
        return store_data
    
@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return stores.values()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, request_data):
        new_store = StoreModel(**request_data)
        try:
            db.session.add(new_store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="Store already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the Store.")

        return new_store