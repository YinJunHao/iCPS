from flask import Blueprint, render_template

from CPSBuilder.utils.db import *
from CPSBuilder.utils.archive.module_functions import *
from CPSBuilder.utils.route import *

from CPSBuilder.modules.archive.execution_module import ExecutionModule

import config

import logging
logger = logging.getLogger(__name__)

client = MongoClient(config.mongo_ip, config.mongo_port)

job_monitoring = Blueprint('job_monitoring', __name__,
                           template_folder='templates')

execution_module = ExecutionModule(client)


@job_monitoring.route('/progress_monitor/<string:user_id>/<string:job_id>')
def progress_monitor(job_id, user_id):
    action_seq, step_seq = execution_module.get_prev_step_record(job_id, user_id)
    logger.info(f"[{job_id}]: Monitoring step {action_seq}-{step_seq}")
    step_details = {
        "action_seq": action_seq,
        "step_seq": step_seq
    }
    try:
        job_details = execution_module.fetch_action_detail_list(
            user_id, {'job_id': job_id})[0]
    except IndexError:
        logger.error(f"[{job_id}]: No job detail found")
    return render_template('progress_monitor.html', job_id=job_id, job_details=job_details, step_details=step_details)
