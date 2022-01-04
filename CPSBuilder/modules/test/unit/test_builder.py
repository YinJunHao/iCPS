import unittest
from pymongo import MongoClient
from bson import ObjectId
from pprint import pprint
from CPSBuilder.modules import builder
from CPSBuilder.utils import db
import config

job_db_name = "test-job"
ontology_db_name = f"test-ontology"
client = None
client = MongoClient(config.mongo_ip, config.mongo_port)
# drop test dbs
client.drop_database(job_db_name)
client.drop_database(ontology_db_name)
# recreate test dbs
job_db = client[job_db_name]
ontology_db = client[ontology_db_name]


class TesterJob(unittest.TestCase):
    def setUp(self):
        self.target = builder.JobBuilder(client, test=True)

    def test_package_single_step(self):
        # prepare input
        data = {
            "index": 0,
            "var": "s1",
            "location_id": "L1",
            "param": "param_dict",
            "exec": [
                {
                    "index": 0,
                    "same_as_step_index": None,
                    "same_as_exec_index": 1,
                    "state": "state_dict_0",
                    "preferred_exec": None,
                    "alternative_exec": None,
                },
                {
                    "index": 1,
                    "same_as_step_index": None,
                    "same_as_exec_index": None,
                    "state": "state_dict_1",
                    "preferred_exec": "exec_dict",
                    "alternative_exec": "list_of_exec_dict",
                },
                {
                    "index": 2,
                    "same_as_step_index": None,
                    "same_as_exec_index": None,
                    "state": "state_dict_2",
                    "preferred_exec": "exec_dict",
                    "alternative_exec": "list_of_exec_dict",
                },
                {
                    "index": 3,
                    "same_as_step_index": None,
                    "same_as_exec_index": 2,
                    "state": "state_dict_3",
                    "preferred_exec": "exec_dict",
                    "alternative_exec": "list_of_exec_dict",
                },
            ]
        }

        # test
        r1 = self.target.package_single_step(data)
        print(r1)


class TesterOntology(unittest.TestCase):
    def setUp(self):
        self.target = builder.OntologyBuilder(client, test=True)

    def test_package_isAchievedBy(self):
        # prepare input
        state_index_var_dict = {
            0: "state1",
            1: "state2"
        }
        step = [
            {
                "sentence": "step",
                "index": 0,
                "step_cond_index": [0]
            }
        ]
        condition = [
            {
                "index": 0,
                "isAchievedBy_index": [0]
            }
        ]
        data = [
            {
                "StateCorrect_index": [0, 1],
                "hasPrerequisiteState_index": [0, 1],
                "index": 0,
            },
            {
                "StateCorrect_index": [2],
                "hasPrerequisiteState_index": [0],
                "index": 1,
            },
        ]

        # test
        r1 = self.target.package_isAchievedBy(data, condition, step, state_index_var_dict)
        print(r1)


if __name__ == '__main__':
    unittest.main()
