import config
from pymongo import MongoClient
from datetime import datetime


client = MongoClient(config.mongo_ip, config.mongo_port)
job_db = client["job"]
job_task_col = job_db["job-task"]
state_buffer_col = job_db["state-buffer"]
broadcast_buffer_col = job_db["broadcast-buffer"]


def create_job_task(job_id, step_tup_list):
    query = {
        "job_id": job_id,
    }
    executor = [
        {
            "index": 0,
            "same_as_step": None,
            "state": {
                "class": "complete",
                "type": "task"
            },
            "preferred_exec": {
                "ID": "H87566",
                "class": "hardware",
                "name": "cam1",
                "type": "camera",
                "software_id": "print_dummy",
            },
            "alternative_exec": [],
            "actual_exec": {
                "ID": None,
                "class": None,
                "type": None,
            },
            "status": False,
        }
    ]
    step = [
        {
            "index": tup[0],
            "var": tup[1],
            "status": "incomplete",
            "exec": executor
        }
        for tup in sorted(step_tup_list, key=lambda x: x[0])
    ]
    post = {
        "job_id": job_id,
        "status": "pending",
        "objective_layer_1": [
            {
                "index": 0,
                "content": list(range(17, 33)),
                "datetime_start": None,
                "datetime_end": None,
                "status": "pending",
            }
        ],
        "step": step
    }
    inserted = job_task_col.insert_one(post)  # create empty buffer for job_id
    task_ObjectId = inserted.inserted_id
    return str(task_ObjectId)


def create_state_buffer(job_id, task_ObjectId):
    query = {
        "job_id": job_id
    }
    post = {
        "job_id": job_id,
        "job_terminated": False,
        "to_be_collected": list()
    }
    curs = state_buffer_col.find(query)
    doc = None
    for item in curs:
        doc = item
    if doc is None:  # buffer for job_id is not created previously
        state_buffer_col.insert_one(post)   # create empty buffer for job_id
    # else:
    #     state_buffer_col.update_one(query, {"$set": post})
    # search for doc with task_ObjectId
    query = {
        "to_be_collected": {
            "$all": [{
                "$elemMatch": {
                    "task_ObjectId": task_ObjectId,
                }
            }]
        },
    }
    curs = state_buffer_col.find(query)
    doc = None
    for item in curs:
        doc = item
    # create to_be_collected for task_ObjectId
    if doc is None:  # if to_be_collected is not created previously
        new_info = {
            "$push": {  # append to list
                "to_be_collected": {
                    "task_ObjectId": task_ObjectId,
                    "state_buffer": list(),
                    "can_be_collected": False
                }
            }
        }
        state_buffer_col.update_one({"job_id": job_id}, new_info)
    else:
        new_info = {
            "$set": {   # reset data
                "to_be_collected.$.task_ObjectId": task_ObjectId,
                "to_be_collected.$.state_buffer": list(),
                "to_be_collected.$.can_be_collected": False
            }
        }
        state_buffer_col.update_one(query, new_info)


def create_broadcast_buffer(job_id, task_ObjectId):
    query = {
        "job_id": job_id
    }
    post = {
        "job_id": job_id,
        "to_be_broadcast": list()
    }
    curs = broadcast_buffer_col.find(query)
    doc = None
    for item in curs:
        doc = item
    if doc is None:  # buffer for job_id is not created previously
        broadcast_buffer_col.insert_one(post)   # create empty buffer for job_id
    # else:
    #     broadcast_buffer_col.update_one(query, {"$set": post})
    # search for doc with task_ObjectId
    query = {
        "to_be_broadcast": {
            "$all": [{
                "$elemMatch": {
                    "task_ObjectId": task_ObjectId,
                }
            }]
        },
    }
    curs = broadcast_buffer_col.find(query)
    doc = None
    for item in curs:
        doc = item
    # create to_be_collected for task_ObjectId
    if doc is None:  # if to_be_collected is not created previously
        new_info = {
            "$push": {  # append to list
                "to_be_broadcast": {
                    "task_ObjectId": task_ObjectId,
                    "step_list": list(),
                    "blocker_list": list(),
                    "output_list": list(),
                    "have_been_broadcast": False
                }
            }
        }
        broadcast_buffer_col.update_one({"job_id": job_id}, new_info)
    else:
        new_info = {
            "$set": {   # reset data
                "to_be_broadcast.$.task_ObjectId": task_ObjectId,
                "to_be_broadcast.$.step_list": list(),
                "to_be_broadcast.$.blocker_list": list(),
                "to_be_broadcast.$.output_list": list(),
                "to_be_broadcast.$.have_been_broadcast": False
            }
        }
        broadcast_buffer_col.update_one(query, new_info)


if __name__ == "__main__":
    job_id = "test"
    step_tup_list = [(0, 0)]
    task_ObjectId = create_job_task(job_id, step_tup_list)
    create_state_buffer(job_id, task_ObjectId)
    create_broadcast_buffer(job_id, task_ObjectId)
