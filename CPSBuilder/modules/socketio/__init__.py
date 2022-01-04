'''
This script is socketio server.
The server doesn't connect to anything but waits for client to connect to it.
'''

from flask_socketio import SocketIO
import logging

logger = logging.getLogger(__name__)
socketio = SocketIO()
# default events for socketio: connect, disconnect
# socketio client is in js

# connect event is automatically emitted when a client connects to the socketio server
@socketio.on('connect', namespace='/broadcast-queue', )
def test_connect():
    print('Broadcast client connected')
    logger.info("client connected.")

@socketio.on('disconnect', namespace='/broadcast-queue')
def test_disconnect():
    print('Broadcast client Disconnected')

@socketio.on('received-message', namespace='/broadcast-queue')
def confirm_receive(msg):
    print("message received by broadcast client")
    logger.info(f"Received on server. status: " + str(msg['status']) + "msg: " + str(msg['data']))

@socketio.on('connect', namespace='/actual-exec')
def test_connect():
    print('Broadcast client connected')
    logger.info("client connected.")

@socketio.on('disconnect', namespace='/actual-exec')
def test_disconnect():
    print('Broadcast client Disconnected')

@socketio.on('received-message', namespace='/actual-exec')
def confirm_receive(msg):
    print("message received by broadcast client")
    logger.info(f"Received on server. status: " + str(msg['status']) + "msg: " + str(msg['data']))

@socketio.on('new_actual_exec', namespace='/actual-exec')
def new_actual_exec(data):
    print(data)
    socketio.emit("new_actual_exec", data, namespace="/broadcast-queue")

