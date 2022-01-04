from archive.CognitiveEngine.modules import CognitiveEngine
from flask import Blueprint
from flask import Response, request

from archive.CognitiveEngine.functions.module_functions import *
from archive.CognitiveEngine.functions.route_functions import *

from CPSBuilder.modules.archive.execution_module import ExecutionModule

import logging
logger = logging.getLogger(__name__)

# config mongodb
client = MongoClient(config.mongo_ip, config.mongo_port)

# initialize modules
cognitive_engine = CognitiveEngine(client)
execution_module = ExecutionModule(client)

# initialize blueprint
process_flow_control = Blueprint('process_flow_control', __name__)

"""
Route is used to test cognitive engine algorithm. 
Not for production.
"""
@process_flow_control.route("/api/job-monitoring/test-js", methods=['POST'])
def test_js_monitoring():
    job_id = request.args.get('job_id')
    user_id = request.args.get('user_id')
    action_seq = int(request.args.get('action_seq'))
    step_seq = int(request.args.get('step_seq'))
    execution_module.post_job_to_board(job_id, user_id, action_seq, step_seq)
    return ""



@process_flow_control.route('/api/cognitive-engine/reasoner', methods=['GET', 'POST'])
# def get_process_status(job_id, user_id, action_status, resource_type, action_sequence):
def get_process_status():
    """
    This function is not being used in the CPS. Developed for testing of the reasoner.
    """
    if request.method == 'GET':
        return Response('pong', 200)
    data = request.get_json()
    job_id = data.get('job_id')
    user_id = data.get('user_id')
    action_status = data.get('action_status')
    action_seq = data.get('action_seq')
    step_seq = data.get('step_seq')
    total_action_count = data.get('total_action_count')
    total_step_count = data.get('total_step_count')

    step_status, next_action_seq, next_step_seq = cognitive_engine.get_inference_class(
        job_id, user_id, action_status, action_seq, step_seq, total_action_count, total_step_count)
    res = {
        "step_status": step_status,
        "next_action_seq": next_action_seq,
        "next_step_seq": next_step_seq
    }
    headers = {'Content-Type': 'application/json'}
    return Response(json.dumps(res), 200, headers=headers)

@process_flow_control.route('/api/cognitive-engine/reasoner/get-next-step', methods=['GET', 'POST'])
# def get_process_status(job_id, user_id, action_status, resource_type, action_sequence):
def get_next_step():
    """
    This function is not being used in the CPS. Developed for testing of the reasoner.
    """
    if request.method == 'GET':
        return Response('pong', 200)
    data = request.get_json()
    job_id = data.get('job_id')
    user_id = data.get('user_id')
    action_status = data.get('action_status')
    action_seq = int(data.get('action_seq'))
    step_seq = int(data.get('step_seq'))
    total_action_count = data.get('total_action_count')
    total_step_count = data.get('total_step_count')
    print(f"data received!")

    step_status, next_action_seq, next_step_seq = cognitive_engine.get_next_step(
        job_id, user_id, action_status, action_seq, step_seq, total_action_count, total_step_count)
    res = {
        "step_status": step_status,
        "next_action_seq": next_action_seq,
        "next_step_seq": next_step_seq
    }
    headers = {'Content-Type': 'application/json'}
    return Response(json.dumps(res), 200, headers=headers)