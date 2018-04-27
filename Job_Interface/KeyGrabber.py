__author__ = 'aflentz'
import os
from ConfigParser import RawConfigParser

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
config = RawConfigParser()
if os.path.exists('/config.ini'):
    config.read('/config.ini')
else:
    config.read(BASE_DIR + '/config.ini')

class KeySettings:
    def __init__(self):
        self.host = config.get('SECRET', 'HOST')
        self.key = config.get('SECRET', 'SECRET_KEY')