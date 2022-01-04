'''
Only related to socketio script.
'''
import eventlet
eventlet.monkey_patch()

import config
import logging
from threading import Thread, Event
from CPSBuilder.modules.socketio import socketio

from time import sleep


logger = logging.getLogger(__name__)

thread = Thread()
thread_stop_event = Event()


class BroadcastJob(Thread):
    def __init__(self, client, **kwargs):
        self.stop_sending = False
        self.job_history = client['job-history']
        self.kwargs = kwargs
        self.delay = 1
        self.timeout = 15
        super(BroadcastJob, self).__init__()

    def get_prev_step_record(self, job_id, user_id):
        try:
            job_details = next(
                self.job_history[user_id].find({'job_id': job_id}))
        except StopIteration:
            logger.error(f"[{job_id}]: {job_id} not found in database.")
            return None, None
        prev_action_seq = job_details.get("process_action_seq", "")
        prev_step_seq = job_details.get("process_step_seq", "")
        return prev_action_seq, prev_step_seq

    def broadcast_job(self, job_id, user_id, action_seq, step_seq):
        logger.info(
            f"[{job_id}]: broadcasting update message for {action_seq}-{step_seq}")
        prev_action_seq, prev_step_seq = self.get_prev_step_record(
            job_id, user_id)
        if prev_action_seq is None or prev_step_seq is None:
            return
        else:
            post = {
                "next_action_seq": action_seq,
                "next_step_seq": step_seq,
                "prev_action_seq": prev_action_seq,
                "prev_step_seq": prev_step_seq
            }
            count = 0
            socketio.emit("new_broadcast", post, namespace="/broadcast-queue")

    def _stop_thread(self):
        self.stop_sending = True

    def run(self):
        job_id = self.kwargs['job_id']
        user_id = self.kwargs['user_id']
        action_seq = self.kwargs['action_seq']
        step_seq = self.kwargs['step_seq']
        self.broadcast_job(job_id, user_id, action_seq, step_seq)
