from flask.views import MethodView
from flask_smorest import abort, Blueprint
from sqlalchemy.exc import SQLAlchemyError
from models import UserModel
from schemas import UserSchema
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from db import db
from blocklist import BLOCKLIST

blp = Blueprint("Users", __name__, description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        user_exist = UserModel.query.filter(UserModel.username == user_data["username"]).first()
        if user_exist:
            abort(400, message="A user with this username already exists!")

        user = UserModel(username=user_data["username"], password=pbkdf2_sha256.hash(user_data["password"]))

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return user
    
@blp.route("/user/<int:user_id>")
class User(MethodView):

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    @blp.response(202)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        
        return { "message" : "User deleted!"}


@blp.route("/login")
class UserLogin(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            token = create_access_token(identity=user.id)
            return { "token": token }, 200
        
        abort(401, message="Invalid credentials.")

@blp.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        jwt = get_jwt()["jti"]
        BLOCKLIST.add(jwt)
        return { "message": "User logged with succeful" }, 200