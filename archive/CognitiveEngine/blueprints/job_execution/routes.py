import eventlet
from flask import Blueprint, Response, request, redirect, url_for

from archive.CognitiveEngine.functions.module_functions import *
from archive.CognitiveEngine.functions.route_functions import *

from CPSBuilder.modules.archive.cloud_insert_module import CloudInsertModule
from CPSBuilder.modules.archive.resource_management_module import ResourceManagementModule
from CPSBuilder.modules.archive.execution_module import ExecutionModule
from archive.CognitiveEngine.modules.cognitive_engine import CognitiveEngine

from threading import Thread

import config

import logging
logger = logging.getLogger(__name__)

client = MongoClient(config.mongo_ip, config.mongo_port)

job_execution = Blueprint('job_execution', __name__,
                          template_folder='templates')

cloud_insert_module = CloudInsertModule(client)
resource_management_module = ResourceManagementModule(client)
execution_module = ExecutionModule(client)
cognitive_engine = CognitiveEngine(client)

eventlet.monkey_patch()


@job_execution.route('/api/assign_job', methods=['GET'])
def assign_job():
    """
    Called once by step_generator\route.
    This API endpoint is called after a job is inserted into the database. \n
    It broadcasts the first step of the job into the broadcast database directs the user to the job history page to monitor progress.
    """
    job_id = request.args.get('job_id')
    user_id = request.args.get('user_id')

    action_seq, step_seq = execution_module.init_job_execution(job_id, user_id)
    return redirect(url_for('job_monitoring.progress_monitor', job_id=job_id, user_id=user_id, action_seq=action_seq, step_seq=step_seq))


@job_execution.route('/api/builder/add-cyber-twin', methods=['POST'])
def add_cyber_twin():
    data = request.get_json()
    res = execution_module.add_cyber_twin(data)
    return res


@job_execution.route('/api/builder/report-status', methods=['POST'])
def update_status():
    """
    Called multiple times by cyber twins.
    Calls a route api in execution module that's in CPSBuilder.
    This API feeds the cognitive engine with environment variables and outputs the inferred steps. \n
    This API is called by a cyber twin indicating that the process has ended and the result needs to be evaluated. \n
    Depending on the output of the cognitive engine the database is also updated accordingly.
    """
    # data = request.get_json()
    # testres = data.get('testing')
    # res = f'Received {testres} with thanks'
    # status = 200

    data = request.get_json()

    user_id = data.get('user_id')
    job_id = data.get('job_id')

    action_seq = int(data.get('action_seq'))
    step_seq = int(data.get('step_seq'))
    step_start = data.get('step_start')
    step_end = data.get('step_end')
    exec_status = data.get('step_status')

    logger.info(
        f'For job: {job_id}, user: {user_id}, action: {action_seq}, step: {step_seq}, status: {exec_status}')

    if cognitive_engine.check_step_completion(job_id, user_id, action_seq, step_seq):
        # all executors have completed this step
        logger.info(
            f'{job_id}-{user_id}: has completed step check for {action_seq}-{step_seq}')
        '''get job details to query database'''
        job_details = {
            "job_id": job_id
        }
        # todo: need to change the way that determines total action-step count
        # this part determines the total number of action/step count
        total_step_count_list = execution_module.fetch_action_detail_list(
            user_id, job_details)
        total_action_count = len(
            total_step_count_list[0]['action_details_list'])
        print(f'total number of actions: {total_action_count}')
        total_step_count = total_step_count_list[0][
            'action_details_list'][action_seq]['total_step_count']
        print(f'fetch {total_step_count}')

        """
        Obtain process control from cognitive engine
        """

        step_status = cognitive_engine.check_step_status(
            job_id, user_id, action_seq, step_seq)

        # todo: need to change the way that decides next action-step seq
        # this part decides the next action-step seq
        # inferred_step_status, next_action_seq, next_step_seq = cognitive_engine.get_inference_class(
        #     job_id, user_id, step_status, action_seq, step_seq, total_action_count, total_step_count)
        # inferred_step_status, next_action_seq, next_step_seq = 'completed', 0, 0

        #Instead of directly calling the inference ^, call
        inferred_step_status, next_action_seq, next_step_seq = cognitive_engine.get_next_step(job_id, user_id, step_status, action_seq, step_seq, total_action_count, total_step_count)
        logger.info(
            f'{job_id}-{user_id}: Status {inferred_step_status}. Next step is {next_action_seq}-{next_step_seq} ')

        # if something breaks in get_inference_class, next_action_seq and next_step_seq will be None
        # then the next action-step will not be broadcasted
        # todo: handle last step completion >> next_action_seq: 'job_done' and next_step_seq: 'job_done'
        if next_action_seq is not None and next_step_seq is not None:
            if next_action_seq != "job_done" and next_step_seq != "job_done":   # if not completed
                # send new job to execution module in CPSBuilder
                send_new_job_t = Thread(target=execution_module.post_job_to_board, args=(
                    job_id, user_id, next_action_seq, next_step_seq))
                send_new_job_t.start()
                print(f'{job_id}-{user_id}: New thread started. Broadcasting new item for job: {job_id}, user: {user_id}, action: {next_action_seq}, step: {next_step_seq}.')

            new_info = {}
            '''update new info'''
            new_info[f"action_details_list.{str(action_seq)}.action_exec.{str(step_seq)}.step_start"] = step_start
            new_info[f"action_details_list.{str(action_seq)}.action_exec.{str(step_seq)}.step_complete"] = step_end
            new_info[f"action_details_list.{str(action_seq)}.action_exec.{str(step_seq)}.step_status"] = step_status

            # Check if all action-step are completed
            if inferred_step_status == "completed":
                new_info[f"action_details_list.{str(action_seq)}.completed_step_count"] = (
                    step_seq + 1)
                if total_step_count == step_seq + 1:
                    new_info[f"action_details_list.{str(action_seq)}.action_complete"] = step_end
                    new_info[f"action_details_list.{str(action_seq)}.action_status"] = "completed"
                    if total_action_count == action_seq + 1:
                        new_info["task_status"] = "completed"

                if step_seq == 0:
                    new_info[f"action_details_list.{str(action_seq)}.action_start"] = step_start

            else:
                new_info[f"action_details_list.{str(action_seq)}.action_status"] = step_status
                new_info["task_status"] = step_status
                '''when the job is restarted, update task_status to pending again'''

            # send updated job to execution module in CPSBuilder
            execution_module.update_job_history(user_id, job_details, new_info)
            print(f'update db with {new_info}')

            res = f'Status {inferred_step_status} received and job history updated'
            status = 200
            return Response(res, status)
        else:
            logger.error(
                f'{job_id}-{user_id}: Cognitive engine does not have a next step inferred for {action_seq}-{step_seq}.')
            res = f'No suitable inference made received and job history updated'
            status = 200
        return Response(res, status)
    else:
        logger.info(
            f'{job_id}-{user_id}: has not been completed. Wait for updates from other cybertwin')
        res = f'{job_id} for user {user_id} has not been completed. Wait for updates from other cybertwin'
        status = 200
        return Response(res, status)
