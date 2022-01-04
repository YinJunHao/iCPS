'''
Create your own config.py using the template below.
This template is applicable for the following repository:
1. IntelligentCPS
2. IntelligentCPS_CE
3. IntelligentCPS_CT
'''

# Flask
secret_key = 'secret123'    # (str)
host = '0.0.0.0'    # (str)

# Server
server_ip = '127.0.0.1'     # (str)
server_port = 5000    # (int)

# Resource
this_ip = None   # (str) where the CT is running on
port = None     # (int) where the CT is running on
resource_id = None  # (str) refer to db
resource_name = None     # (str) refer to db
resource_type = None    # (str) refer to db
resource_class = None   # (str) hardware/human/robot

# Mongodb
mongo_ip = server_ip    # (str) where mongoDB server is running
mongo_port = 27017  # (int)

# Cognitive Engine
cognitive_engine_ip = server_ip     # (str) where CE is running on
cognitive_engine_port = 8080    # (int)

# Serial communication
serial_port = None  # (str) if used

# TCP IP communication
tcp_ip = this_ip    # (str)
tcp_port = None     # (int) if used, dedicated port
buffer_size = 1024  # (int)

# File directory
excel_dir = "./CPSBuilder/ontos/"
