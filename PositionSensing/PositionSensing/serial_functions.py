# import eventlet
# eventlet.monkey_patch()

import logging

from pymongo import MongoClient
from config import *
from PositionSensing.PositionSensing.listener import PositionSensor

logger = logging.getLogger(__name__)
client = MongoClient(mongo_ip, mongo_port)
position_sensor = PositionSensor(client, 'COM3')

def position_sensing():
    print("pos thread started")
    while True:
        try:
            # print("trying hard...")
            position_sensor.open_ser()
            value = position_sensor.ser_readline()
            print(f"value is {value}")
            position_sensor.close_ser()
            if value:
                text = value.decode('utf-8')
                lst = text.split(',')
                if len(lst) == 8:
                    if lst[1] == '0' and int(lst[6]) > 75:
                        position_sensor_tag = lst[2]
                        x = lst[3]
                        y = lst[4]
                        z = lst[5]
                        confidence_level = lst[6]
                        # todo: check how to improve accuracy of sensors(inaccurate by +- 20cm)
                        print(f"device_name:{position_sensor_tag} x:{x} y:{y} z:{z} confidence: {confidence_level}")
                        logger.info(f"device_name:{position_sensor_tag} x:{x} y:{y} z:{z} confidence: {confidence_level}")
                        position_sensor.update_coordinates_in_db(position_sensor_tag, x, y, z)
        except KeyboardInterrupt:
            # todo: check what this does...
            position_sensor.ser.flushInput()
            position_sensor.ser.flushOutput()
            position_sensor.ser.close()
            print('Connection closed')
            logger.info('Connection closed')
            break
        except Exception as e:
            position_sensor.ser.close()
            print(e)
            logger.info(e)