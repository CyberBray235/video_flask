from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, user_id, username, password,role):
        self.id = user_id
        self.username = username
        self.password = password
        self.role = role

    @staticmethod
    def get(user_id,mongo):
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            role = user_data.get('role', 'user')
            return User(str(user_data['_id']), user_data['username'], user_data['password'], role)
        return None

    @staticmethod
    def check_by_username(username,mongo):
        user_data = mongo.db.users.find_one({"username": username})
        if user_data:
            role = user_data.get('role', 'user')  #SI l'user n'a pas de rôle
            return User(str(user_data['_id']), user_data['username'], user_data['password'], role)
        return None

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)