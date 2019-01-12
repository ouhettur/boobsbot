logindb = 'logindb'
passdb = 'passdb'
dbhost = 'dbhost'
dbname = 'dbname'
token = 'token'

ACCESS_KEY_ID = 'ACCESS_KEY_ID'
ACCESS_SECRET_KEY = 'ACCESS_SECRET_KEY'
BUCKET_NAME = 'BUCKET_NAME'


try:
    from local_config import *
except ImportError:
    raise ImportError('no file local_config.py in the directory')


