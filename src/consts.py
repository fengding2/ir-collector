import sys
import os
import traceback
from os.path import dirname, abspath

## add the root path into path env
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
CURRENT_DIR = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(CURRENT_DIR)
PARENT_DIR = abspath(dirname(CURRENT_DIR))
LOG_PATH = CURRENT_DIR + '/logs/'
LOG_FILE_NAME = 'server.log'
CONTACTS_FILE = CURRENT_DIR + '/contacts.txt'

DATA_DIR = PARENT_DIR + '/data'
OUTPUT_DIR = PARENT_DIR + '/out'

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)
    
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
