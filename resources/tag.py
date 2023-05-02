from flask.views import MethodView
from flask_smorest import abort, Blueprint
from sqlalchemy.exc import SQLAlchemyError
from models import TagModel, StoreModel
from schemas import TagSchema
from db import db

blp = Blueprint("Tags", __name__, description="Operations on tags")

@blp.route("/store/<string:store_id>/tag")
class Tag(MethodView):

    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()
    
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag_exist = TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first()

        if tag_exist:
            abort(400, message="This tag already exist!")

        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
            return tag
        except SQLAlchemyError as e:
            abort(500, message=str(e))

@blp.route("/tag/<int:tag_id>")
class TagList(MethodView):

    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag