import unittest
from pymongo import MongoClient
from bson import ObjectId
from pprint import pprint
from CPSBuilder.modules import executor_mapper
from CPSBuilder.utils import db
import config

resource_db_name = "test-resource"
client = MongoClient(config.mongo_ip, config.mongo_port)
# drop test dbs
client.drop_database(resource_db_name)
# recreate test dbs
resource_db = client[resource_db_name]


class TesterTask(unittest.TestCase):
    def setUp(self):
        self.target = executor_mapper.ExecutorMapper(client, test=True)

    def test_map_exec_to_step(self):
        # prepare phy resource doc
        posts = [
            {
                "ID": "phy_id1",
                "class": "hardware",
                "type": "roller",
                "name": "Name",
                "location_id": "loc",
                "available": True,
                "online": True
            },
            {
                "ID": "phy_id2",
                "class": "hardware",
                "type": "roller",
                "name": "Name",
                "location_id": "loc",
                "available": True,
                "online": False
            }
        ]
        resource_db["physical"].insert_many(posts)
        posts = [
            {
                "ID": "cyb_id1",
                "class": "software",
                "physical_resource_id": ["phy_id1"]
            },
            {
                "ID": "cyb_id2",
                "class": "software",
                "physical_resource_id": ["phy_id2"]
            }
        ]
        resource_db["cyber"].insert_many(posts)
        # prepare input
        state_exec = {
            "class": "A",
            "type": "job",
            "exec": [
                {
                    "ID": "phy_id1",
                    "class": "hardware",
                    "type": "roller",
                    "name": "Name",
                    "software_id": "cyb_id1"
                }
            ]
        }
        location_id = "loc"
        # test function
        r1 = self.target.map_exec_to_step(state_exec, location_id)
        print(r1)
        # assert
        a1 = [
            {
                "ID": "phy_id1",
                "class": "hardware",
                "type": "roller",
                "name": "Name",
                "software_id": "cyb_id1",
            }
        ]
        self.assertCountEqual(r1, a1)


if __name__ == '__main__':
    unittest.main()
