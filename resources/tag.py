from flask.views import MethodView
from flask_smorest import abort, Blueprint
from sqlalchemy.exc import SQLAlchemyError
from models import TagModel, StoreModel, ItemModel, ItemTagModel
from schemas import TagSchema, TagItemSchema
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


@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class TagLinkItem(MethodView):
    @blp.response(200, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag
    
    @blp.response(200, TagItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return { "message": "Item removed with success!", "item": item, "tag": tag }
      
@blp.route("/tag/<int:tag_id>")
class TagList(MethodView):

    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(202)
    @blp.alt_response(404, description="Tag not found")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if tag.items:
            abort(400, message="This tag have items!")

        try:
            db.session.delete(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {"message": "Tag deleted."}