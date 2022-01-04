def robot_db():
    robotdb = [{'ID': 'E00001', 'name': 'Right Arm', 'type': 'lift_base', 'assigned': '1', 'availability': '0'},
               {'ID': 'E00002', 'name': 'Left Arm', 'type': 'base', 'assigned': '1', 'availability': '1'},
               {'ID': 'E00003', 'name': 'Head', 'type': 'lift_base', 'assigned': '0', 'availability': '0'},
               {'ID': 'F00001', 'name': 'Leg', 'type': 'Vehicle', 'assigned': '0', 'availability': '1'},
               {'ID': 'G00002', 'name': 'Right Leg', 'type': 'robot arm', 'assigned': '1', 'availability': '1'}]
    return robotdb

def history_db():
    historydb = [{'job_id': 'AT00030', 'task_status': ['artificial_trachea', 'Step pending processing.'], 'job_submission_timestamp': '2019-02-21 16:00:00'},
                 {'job_id': 'AT00031', 'task_status': ['Break', 'Completed.'], 'job_submission_timestamp': '2019-02-21 15:55:24'},
                 {'job_id': 'AT00032', 'task_status': ['Cutting', 'Step pending processing.'], 'job_submission_timestamp': '2019-02-21 16:55:24'},
                 {'job_id': 'BT00030', 'task_status': ['artificial_body', 'Completed.'], 'job_submission_timestamp': '2019-03-21 16:55:24'},
                 {'job_id': 'BT00031', 'task_status': ['artificial_arm', 'Step pending processing.'], 'job_submission_timestamp': '2019-02-22 16:55:24'},
                 {'job_id': 'CT00030', 'task_status': ['artificial_trachea', 'Processing.'], 'job_submission_timestamp': '2018-02-21 16:55:24'}]
    return historydb

def hardware_db():
    hardwaredb = []
    return hardwaredb

def processes_db():
    processesdb = [['artificial_trachea', ['step 1', 'step 2', 'step 3', 'step 4'], 'bob']
                   ['artificial_trachea', ['step 1', 'step 2', 'step 3', 'step 4'], 'mary']
                   ['artificial_trachea', ['step 1', 'step 2', 'step 3', 'step 4'], 'john']
                   ['artificial_trachea', ['step 1', 'step 2', 'step 3', 'step 4'], 'jack']
                   ['artificial_trachea', ['step 1', 'step 2', 'step 3', 'step 4'], 'jill']
                   ['artificial_trachea', ['step 1', 'step 2', 'step 3', 'step 4'], 'tom']]
    return processesdb



