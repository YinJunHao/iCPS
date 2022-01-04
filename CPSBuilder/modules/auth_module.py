from pymongo import MongoClient
from CPSBuilder.utils.db import *
from passlib.hash import sha256_crypt
from bson import ObjectId

import logging
logger = logging.getLogger(__name__)


class AuthModule():
    def __init__(self, client, test=False):
        if test:
            self.user_db = client['test-user']
        else:
            self.user_db = client['user']

        self.login_col = self.user_db['login']
        self.profile_col = self.user_db['profile']

    def register_user(self, name, user_id, password, position):
        """
        Adds a new user into the authentication database.
        """
        found_user = []
        # for item in self.login_db.find({"user_id": user_id}):
        #     found_user.append(item)
        # if len(found_user) == 0:
        #     post = {
        #         'name': name,
        #         'user_id': user_id,
        #         'password': password
        #     }
        #
        #     self.login_db.insert_one(post)
        #
        #     # need to add newly registered user as human resource
        #     post_resource = {
        #         'name': name,
        #         'ID': user_id,
        #         'capability': position
        #     }
        #     self.human.insert_one(post_resource)
        #
        #     # end of edit
        #     return True
        # else:
        #     return False
        for item in self.login_col.find({"user_id": user_id}):
            found_user.append(item)
        if len(found_user) == 0:
            post = {
                "name": name,
                "user_id": user_id,
                "password": sha256_crypt.hash(str(password))
            }

            self.login_col.insert_one(post)

            # need to add newly registered user in profile
            post_resource = {
                "user_id": user_id,
                "name": name,
                "position": position,
                "is_admin": self.is_admin(position)
            }
            self.profile_col.insert_one(post_resource)
            return True
        else:
            return False

    def login_user(self, user_id, password):
        """
        Checks whether the inputted password matches the hashed password in the database.
        """
        found_user = []
        for item in self.login_col.find({'user_id': user_id}):
            found_user.append(item)
            print(found_user)
        if len(found_user) == 0:
            print("user not found")
            return False
        else:
            print("here")
            print(found_user[0]['password'])
            hash = found_user[0]['password']
            print(password)
            return sha256_crypt.verify(password, hash)


    def is_admin(self, position):
        """
            Determine whether newly added user has administration rights or not
        """
        if position in ["Lecturer", "Research Engineer", "PhD Student", "Master Student"]:
            return True
        else:
            return False

    def change_password(self, user_id, old_password, new_password, name):
        """
            Change Password for user.
        """
        found_user = []
        for item in self.login_col.find({"user_id": user_id}):
            found_user.append(item)
        if len(found_user) == 0:
            return False
        else:
            print("here")
            hash = found_user[0]["password"]
            if sha256_crypt.verify(old_password, hash):
                query = {
                    "user_id": user_id
                }
                post = {
                    "name": name,
                    "user_id": user_id,
                    "password": sha256_crypt.hash(str(new_password))
                }
                self.login_col.update_one(query, {"$set": post})
                return True
            else:
                return False

    # def is_admin(self, user_id):
    #     """
    #     Checks whether the user is an admin based on capabality score.
    #     """
    #     capability = self.get_capability(user_id)
    #     if capability and (capability >= 9):
    #         return True
    #     if capability == None:
    #         return None
    #     else:
    #         return False

    # def get_capability(self, user_id):
    #     """
    #     Retrieves capability of the user.
    #     """
    #     # print(user_id)
    #     try:
    #         user = next(self.human.find({'ID': user_id}))
    #         return user['capability']
    #     except StopIteration:
    #         return None