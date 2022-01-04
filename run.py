'''
    CPS Builder consolidates interoperable modular components to develop, execute and analyse human-centered CPSs.
'''

from CPSBuilder.threads import context
from CPSBuilder import socketio
from CPSBuilder import create_app
import config

from datetime import datetime
from threading import Thread
from flask import render_template

import eventlet
eventlet.monkey_patch()


# create_app is imported from the main __init__.py
app = create_app(debug=True, async_mode="threading")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    import logging
    import os

    if not os.path.isdir('./CPSBuilder/data/'):
        os.mkdir('./CPSBuilder/data/')
    logging.basicConfig(filename=f'./CPSBuilder/data/app-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S").__str__()}.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    print('logging is activated')

    t_check_online_resource = Thread(target=context.check_online_resource)
    t_check_online_resource.start()
    print('t_check_online_resource start')
    #
    # t_generate_avail_p = Thread(target=context.generate_avail_p)
    # t_generate_avail_p.start()
    # print('t_generate_avail_p start')

    print("all thread initialized")
    # must be the last line. Run socketio to run socket + the binded app
    socketio.run(app, host=config.host, port=str(config.server_port))
    # socketio only sends, don't care if the receiver has received the msg, or the msg is lost

    '''
    flask debug must be False
    if flask debug is True, thread will initialize twice and break
    app.run(debug=False, host=config.host)
    '''

