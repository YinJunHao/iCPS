# import eventlet
# eventlet.monkey_patch()

from pprint import pprint
import serial, time
import logging

logger = logging.getLogger(__name__)

class PositionSensor():
    def __init__(self, client, port):
        print('initializing pos sensor...')
        self.ser = serial.Serial()
        #ser.port = ‘/dev/ttyACM0’
        self.ser.port = port
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 1
        print('opening serial...')
        self.ser.open()
        # test = ser.read()
        # print(test)
        self.ser.write(b'\r\r')
        time.sleep(0.5)
        self.ser.write(b'lep\r')
        self.ser.close()
        logger.info('Position sensor is initialized.')
        print('Position sensor is initialized.')

        self.hardware_resources = client['resources']['hardware_resources']
        self.human_resources = client['resources']['human_resources']
        self.robot = client['resources']['robot']

    def ser_readline(self):
        # print('read line')
        return self.ser.readline()

    def open_ser(self):
        # print('open port')
        self.ser.open()

    def close_ser(self):
        # print('close port')
        self.ser.close()

    def update_coordinates_in_db(self, position_sensor_tag, x, y, z):
        logger.info(f"Finding my record (position sensor tag) in resource db...")
        query = {"coordinate.position_sensor_tag": position_sensor_tag}
        # todo: change that if-else into dict for simplification
        if not self.find_in_resources_db(self.hardware_resources, query): #if cannot find in thi db
            if not self.find_in_resources_db(self.robot, query):
                if not self.find_in_resources_db(self.human_resources, query):
                    db = None
                    print(f"unregistered position sensor tag {position_sensor_tag} at {x}, {y}, {z}")
                    logger.error(f"unregistered position sensor tag {position_sensor_tag} at {x}, {y}, {z}")
                elif self.find_in_resources_db(self.human_resources, query): #if found
                    db = self.human_resources
            elif self.find_in_resources_db(self.robot, query):
                db = self.robot
        elif self.find_in_resources_db(self.hardware_resources, query):
            db = self.hardware_resources
        if db is not None:
            print(f"position sensor tag {position_sensor_tag} at {x}, {y}, {z} is in {db}")
            logger.info(f"position sensor tag {position_sensor_tag} at {x}, {y}, {z} is in {db}")
            new_info = {
                "coordinate.x": float(x),
                "coordinate.y": float(y),
                "coordinate.z": float(z)
            }
            new_info = {"$set": new_info}
            db.update_one(query, new_info, upsert=False)


    def find_in_resources_db(self, db, query):
        result = db.find(query, {"_id": 0, "coordinate": 1})
        out = []
        for item in result:
            out.append(item)
        if len(out) == 0:
            return False
        else:
            # pprint(out)
            return True

