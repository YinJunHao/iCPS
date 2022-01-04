from flask import render_template, request, flash, redirect, url_for, session, logging, Blueprint
from CPSBuilder.modules import visualizer

from pprint import pprint

import logging
logger = logging.getLogger(__name__)

#initialize MongoDB client
from pymongo import MongoClient
import config
client = MongoClient(config.mongo_ip, config.mongo_port)

#initialize processes
running = Blueprint('running', __name__, static_folder='static', template_folder='templates')

job_display = visualizer.JobDisplay(client)
task_display = visualizer.TaskDisplay(client)

@running.route('/running', methods=['GET', 'POST'])
def running_jobs():
    job_list = job_display.get_running_job(session["user_id"])
    for job in job_list:
        job["task_list"] = list()
        task_list = job_display.get_job_task(job["job_id"])
        for task in task_list:
            job["task_list"].append(task["var"])
    pprint(job_list)
    return render_template('running.html', job_list=job_list)