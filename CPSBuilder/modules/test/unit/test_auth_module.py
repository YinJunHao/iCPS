import unittest
from pymongo import MongoClient
from bson import ObjectId
from CPSBuilder.modules import auth_module
from CPSBuilder.utils import db
from passlib.hash import sha256_crypt
import config

client = MongoClient(config.mongo_ip, config.mongo_port)
client.drop_database("test-user")


class TesterUser(unittest.TestCase):
    def setUp(self):
        self.user = auth_module.AuthModule(client, test=True)

    def test_login_user(self):
        # prepare input
        user_id = "user_id"
        password = "password"
        name = "test"
        position = "Lecturer"
        # self.user.register_user(name, user_id, password, position)
        # test
        result = self.user.login_user(user_id, password)
        # check
        self.assertTrue(result)

    def test_change_password(self):
        # prepare input
        user_id = "user_id"
        old_password = "password"
        new_password = "password1"
        position = "Lecturer"
        name = "test"
        self.user.register_user(name, user_id, old_password, position)
        # test
        result = self.user.change_password(user_id, old_password, new_password, name)
        # check
        self.assertTrue(result)

    def test_register_user(self):
        # prepare input
        user_id = "user_id"
        password = "password"
        name = "test"
        position = "Lecturer"
        # test
        result = self.user.register_user(name, user_id, password, position)
        # check
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

