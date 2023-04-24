from flask.views import MethodView
from flask_smorest import abort, Blueprint
from schemas import StoreSchema, StoreUpdateSchema
from db import db
from models.store import StoreModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

blp = Blueprint("Stores", __name__, description="Operations on stores")

@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store
        
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}

    @blp.arguments(StoreUpdateSchema)
    @blp.response(200, StoreSchema)
    def put(self, request_data, store_id):
        store = StoreModel.query.get_or_404(store_id)

        store_exist = StoreModel.query.filter_by(name=request_data["name"]).first()

        if store_exist:
            abort(400, message="Store already exists.")
        
        store.name = request_data["name"]
        db.session.add(store)
        db.session.commit()

        return store
    
@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

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