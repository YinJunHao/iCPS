import unittest
from pymongo import MongoClient
from bson import ObjectId
from pprint import pprint
from CPSBuilder.modules import visualizer
from CPSBuilder.utils import db
import config

client = MongoClient(config.mongo_ip, config.mongo_port)
client.drop_database("test-search-engine")
client.drop_database("test-process")
client.drop_database("test-condition")
client.drop_database("test-resource")
client.drop_database("test-var-sentence")


class TesterProcess(unittest.TestCase):
    def setUp(self):
        self.task = visualizer.TaskDisplay(client, test=False)
        self.step = visualizer.StepDisplay(client, test=False)

    def test_get_process_details(self):
        # prepare input
        task_ObjectId = "5ddb76b3a900571e78dd1dcf"
        r1 = self.task.get_process_details(task_ObjectId)
        pprint(r1)

    def test_get_step_details(self):
        step_ObjectId = "5ddb5af1a900571e78dd1dc2"
        r1 = self.step.get_step_details(step_ObjectId)
        pprint(r1)


class TesterOntologyVisualizer(unittest.TestCase):
    def setUp(self):
        task_var = "demo"
        self.target = visualizer.OntologyVisualizer(task_var)  # todo: create test workbook

    def test_package_state_details(self):
        # prepare input
        post = {
            "NamedState": ["A", "A1", "B", "B1"],
            "Superclass": ["NamedState", "A", "NamedState", "B"],
            "Type": ["task", "task", "job", "job"],
            "PhyResource": ["r1", "r1", "r2", "r2"],
            "PhyResourceClass": ["R", "R", "R", "R"],
            "CyberResource": ["-1", "-1", "-1", "-1"]
        }
        # actual output
        a1 = [
            {
                "var": "A1",
                "class": "A",
                "type": "task",
                "exec": [{"class": "R",
                          "type": "r1",
                          "software_id": "-1"}],
            },
            {
                "var": "B1",
                "class": "B",
                "type": "job",
                "exec": [{"class": "R",
                          "type": "r2",
                          "software_id": "-1"}],
            }
        ]
        # test
        r1, r2 = self.target.package_state(post)
        # compare
        self.assertEqual(r1, a1)

    def test_package_is_blocked_by_step_details(self):
        post = {
            "NamedStep": ["1", "1", "2", "2", "2"],
            "isBlockedByStep": [1, 2, 3, 3, 3],
            "StepBlocker": ["3", "4", "-1", "1", "2"]
        }
        step_sentence_index_dict = {
            "1": 2,
            "2": 3,
            "3": 0,
            "4": 1,
            "-1": "-1",  # todo: unsure
        }
        state_var_index_dict = {

        }
        a1 = [
            {
                "step": "1",
                "isBlockedByStep": 1,
                "StepBlocker": ["3"]
            },
            {
                "step": "1",
                "isBlockedByStep": 2,
                "StepBlocker": ["4"]
            },
            {
                "step": "2",
                "isBlockedByStep": 3,
                "StepBlocker": ["-1", "1", "2"]
            }
        ]
        a2 = [
            {
                "step": "1",
                "index": 1,
                "StepBlocker": ["3"]
            },
            {
                "step": "1",
                "index": 2,
                "StepBlocker": ["4"]
            },
            {
                "step": "2",
                "index": 3,
                "StepBlocker": ["-1", "1", "2"]
            }
        ]
        condition = "isBlockedByStep"
        r1 = self.target.package_condition(post, condition, step_sentence_index_dict, state_var_index_dict)
        r1 = [
            r for idx, r in enumerate(r1)
            if (r["step"] == a2[idx]["step"]
                and r["index"] == a2[idx]["index"])
        ]
        print(".")
        pprint(r1)
        for idx, r in enumerate(r1):
            self.assertEqual(r["step"], a2[idx]["step"])
            self.assertEqual(r["index"], a2[idx]["index"])
            self.assertCountEqual(r["StepBlocker"], a2[idx]["StepBlocker"])

    def test_package_has_prerequisite_step_details(self):
        post = {
            "NamedStep": ["1", "1", "2", "2", "2"],
            "hasPrerequisiteStep": [1, 2, 3, 3, 3],
            "StepPrerequisite": ["3", "4", "-1", "1", "2"]
        }
        a1 = [
            {
                "step": "1",
                "hasPrerequisiteStep": 1,
                "StepPrerequisite": ["3"]
            },
            {
                "step": "1",
                "hasPrerequisiteStep": 2,
                "StepPrerequisite": ["4"]
            },
            {
                "step": "2",
                "hasPrerequisiteStep": 3,
                "StepPrerequisite": ["-1", "1", "2"]
            }
        ]
        a2 = [
            {
                "step": "1",
                "index": 1,
                "StepPrerequisite": ["3"]
            },
            {
                "step": "1",
                "index": 2,
                "StepPrerequisite": ["4"]
            },
            {
                "step": "2",
                "index": 3,
                "StepPrerequisite": ["-1", "1", "2"]
            }
        ]
        condition = "hasPrerequisiteStep"
        r1 = self.target.package_condition(post, condition)
        print(".")
        pprint(r1)
        r1 = [
            r for idx, r in enumerate(r1)
            if (r["step"] == a2[idx]["step"]
                and r["index"] == a2[idx]["index"])
        ]

        for idx, r in enumerate(r1):
            self.assertEqual(r["step"], a2[idx]["step"])
            self.assertEqual(r["index"], a2[idx]["index"])
            self.assertCountEqual(r["StepPrerequisite"], a2[idx]["StepPrerequisite"])

    def test_package_is_blocked_by_state_details(self):
        post = {
            "NamedStep": ["1", "1", "2", "2"],
            "isBlockedByState": [1, 2, 3, 3],
            "StateBlocker": ["3", "4", "-1", "1"]
        }
        a1 = [
            {
                "step": "1",
                "isBlockedByState": 1,
                "StateBlocker": ["3"]
            },
            {
                "step": "1",
                "isBlockedByState": 2,
                "StateBlocker": ["4"]
            },
            {
                "step": "2",
                "isBlockedByState": 3,
                "StateBlocker": ["-1", "1"]
            }
        ]
        a2 = [
            {
                "step": "1",
                "index": 1,
                "StateBlocker": ["3"]
            },
            {
                "step": "1",
                "index": 2,
                "StateBlocker": ["4"]
            },
            {
                "step": "2",
                "index": 3,
                "StateBlocker": ["-1", "1"]
            }
        ]
        condition = "isBlockedByState"
        r1 = self.target.package_condition(post, condition)
        r1 = [
            r for idx, r in enumerate(r1)
            if (r["step"] == a2[idx]["step"]
                and r["index"] == a2[idx]["index"])
        ]
        print(".")
        pprint(r1)
        for idx, r in enumerate(r1):
            self.assertEqual(r["step"], a2[idx]["step"])
            self.assertEqual(r["index"], a2[idx]["index"])
            self.assertCountEqual(r["StateBlocker"], a1[idx]["StateBlocker"])

    def test_package_has_prerequisite_state_details(self):
        post = {
            "NamedStep": ["1", "1", "2", "2"],
            "hasPrerequisiteState": [1, 2, 3, 3],
            "StatePrerequisite": ["3", "4", "-1", "1"]
        }
        a1 = [
            {
                "step": "1",
                "hasPrerequisiteState": 1,
                "StatePrerequisite": ["3"]
            },
            {
                "step": "1",
                "hasPrerequisiteState": 2,
                "StatePrerequisite": ["4"]
            },
            {
                "step": "2",
                "hasPrerequisiteState": 3,
                "StatePrerequisite": ["-1", "1"]
            }
        ]
        a2 = [
            {
                "step": "1",
                "index": 1,
                "StatePrerequisite": ["3"]
            },
            {
                "step": "1",
                "index": 2,
                "StatePrerequisite": ["4"]
            },
            {
                "step": "2",
                "index": 3,
                "StatePrerequisite": ["-1", "1"]
            }
        ]
        condition = "hasPrerequisiteState"
        r1 = self.target.package_condition(post, condition)
        r1 = [
            r1[idx] for idx, r in enumerate(r1)
            if (r["step"] == a1[idx]["step"]
                and r[condition] == a1[idx][condition])
        ]
        print(".")
        pprint(r1)
        for idx, r in enumerate(r1):
            self.assertEqual(r["step"], a1[idx]["step"])
            self.assertEqual(r[condition], a1[idx][condition])
            self.assertCountEqual(r["StatePrerequisite"], a1[idx]["StatePrerequisite"])

    def test_package_is_achieved_by_details(self):
        post = {
            "NamedStep": ["1", "1", "2", "2"],
            "isAchievedBy": [1, 2, 3, 3],
            "hasPrerequisiteState": [1, 2, 3, 3],
            "StateCorrect": ["A", "B", "C", "D"]
        }
        a1 = [
            {
                "step": "1",
                "isAchievedBy": 1,
                "hasPrerequisiteState": [1],
                "StateCorrect": ["A"],
            },
            {
                "step": "1",
                "isAchievedBy": 2,
                "hasPrerequisiteState": [2],
                "StateCorrect": ["B"],
            },
            {
                "step": "2",
                "isAchievedBy": 3,
                "hasPrerequisiteState": [3],
                "StateCorrect": ["C", "D"]
            }
        ]
        a2 = [
            {
                "step": "1",
                "index": 1,
                "hasPrerequisiteState_index": [1],
                "StateCorrect": ["A"],
            },
            {
                "step": "1",
                "index": 2,
                "hasPrerequisiteState_index": [2],
                "StateCorrect": ["B"],
            },
            {
                "step": "2",
                "index": 3,
                "hasPrerequisiteState_index": [3],
                "StateCorrect": ["C", "D"]
            }
        ]
        condition = "isAchievedBy"
        r1 = self.target.package_condition(post, condition)
        r1 = [
            r for idx, r in enumerate(r1)
            if (r["step"] == a2[idx]["step"]
                and r["index"] == a2[idx]["index"])
        ]
        print(".")
        pprint(r1)
        for idx, r in enumerate(r1):
            self.assertEqual(r["step"], a2[idx]["step"])
            self.assertEqual(r["index"], a2[idx]["index"])
            self.assertCountEqual(r["hasPrerequisiteState"], a1[idx]["hasPrerequisiteState"])
            self.assertCountEqual(r["StateCorrect"], a1[idx]["StateCorrect"])

    def test_package_is_failed_by_state(self):
        post = {
            "NamedStep": ["1", "1", "2", "2"],
            "isFailedByState": [1, 2, 3, 3],    # index
            "hasPrerequisiteState": [1, 2, 3, 3],
            "StateCorrect": ["A", "-1", "B", "C"],
            "StateWrong": ["D", "E", "F", "F"],
            "StepReturn": ["1", "1", "1", "1"]
        }
        a1 = [
            {
                "step": "1",
                "isFailedByState": 1,
                "hasPrerequisiteState": [1],
                "StateCorrect": ["A"],
                "StateWrong": ["D"],
                "StepReturn": ["1"]
            },
            {
                "step": "1",
                "isFailedByState": 2,
                "hasPrerequisiteState": [2],
                "StateCorrect": ["-1"],
                "StateWrong": ["E"],
                "StepReturn": ["1"]
            },
            {
                "step": "2",
                "isFailedByState": 3,
                "hasPrerequisiteState": [3],
                "StateCorrect": ["B", "C"],
                "StateWrong": ["F"],
                "StepReturn": ["1"]
            }
        ]
        a2 = [
            {
                "step": "1",
                "isFailedByState": 1,
                "hasPrerequisiteState": [1],
                "StateCorrect": ["A"],
                "StateWrong": ["D"],
                "StepReturn": ["1"]
            },
            {
                "step": "1",
                "isFailedByState": 2,
                "hasPrerequisiteState": [2],
                "StateCorrect": ["-1"],
                "StateWrong": ["E"],
                "StepReturn": ["1"]
            },
            {
                "step": "2",
                "isFailedByState": 3,
                "hasPrerequisiteState": [3],
                "StateCorrect": ["B", "C"],
                "StateWrong": ["F"],
                "StepReturn": ["1"]
            }
        ]
        condition = "isFailedByState"
        r1 = self.target.package_condition(post, condition)
        r1 = [
            r for idx, r in enumerate(r1)
            if (r["step"] == a2[idx]["step"]
                and r["index"] == a2[idx]["index"])
        ]
        print(".")
        pprint(r1)
        for idx, r in enumerate(r1):
            self.assertEqual(r["step"], a2[idx]["step"])
            self.assertEqual(r["index"], a2[idx]["index"])
            self.assertCountEqual(r["hasPrerequisiteState"], a1[idx]["hasPrerequisiteState"])
            self.assertCountEqual(r["StateCorrect"], a1[idx]["StateCorrect"])
            self.assertCountEqual(r["StateWrong"], a1[idx]["StateWrong"])

    def test_package_empty_step(self):
        # prepare input
        post = {
            "NamedStep": ["s1", "s2", "s2"],
            "isAtLocation": ["w1", "w1", "w2"]
        }
        a1 = [
            {
                "sentence": "s1",
                "location_id": ["w1"]
            },
            {
                "sentence": "s2",
                "location_id": ["w1", "w2"]
            }
        ]
        # test
        r1, r2 = self.target.package_empty_step(post)
        pprint(r1)
        # check
        self.assertCountEqual(r1, a1)

    def test_package_objective(self):
        # prepare input
        post = {
            "Layer": [1, 1, 2, 2],
            "NamedObjective": ["o1", "o2", "o1", "o1"],
            "Index": [0, 1, 0, 0],
            "isAchievedBy": ["s1", "s2", "o1", "o2"]
        }
        a1 = [
            {
                "sentence": "o1",
                "layer": 1,
                "content_layer": "step",
                "content": ["s1"]
            },
            {
                "sentence": "o2",
                "layer": 1,
                "content_layer": "step",
                "content": ["s2"]
            },
            {
                "sentence": "o1",
                "layer": 2,
                "content_layer": "objective_layer_1",
                "content": ["o1", "o2"]
            }
        ]
        a2 = {
            "objective_layer_1": [
                {
                    "sentence": "o1",
                    "layer": 1,
                    "content_layer": "step",
                    "content": ["s1"]
                },
                {
                    "sentence": "o2",
                    "layer": 1,
                    "content_layer": "step",
                    "content": ["s2"]
                }
            ],
            "objective_layer_2": [
                {
                    "sentence": "o1",
                    "layer": 2,
                    "content_layer": "objective_layer_1",
                    "content": ["o1", "o2"]
                }
            ]
        }
        # test
        r1 = self.target.package_objective(post)
        pprint(r1)
        # check
        self.assertCountEqual(r1, a2)

    def test_package_task(self):
        # prepare input
        task_var = "example_onto"
        post = {
            "Layer": [1, 1, 2, 2],
            "NamedObjective": ["o1", "o2", "o1", "o1"],
            "Index": [0, 1, 0, 0],
            "isAchievedBy": ["s1", "s2", "o1", "o2"]
        }
        a1 = {
            "sentence": "o1",
            "content_layer": "objective_layer_1",
            "content": ["o1", "o2"]
        }

        # test
        r1 = self.target.package_task(post, task_var)
        pprint(r1)
        # check
        self.assertCountEqual(r1, a1)


if __name__ == '__main__':
    unittest.main()

