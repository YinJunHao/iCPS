from PositionSensing.serial_functions import position_sensing
import logging
from datetime import datetime

if __name__ == "__main__":
    logging.basicConfig(filename=f'./data/pos-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S").__str__()}.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    position_sensing()