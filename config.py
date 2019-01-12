# This is an example of a configuration file.
# logindb = 'logindb'
# passdb = 'passdb'
# dbhost = 'dbhost'
# dbname = 'dbname'
# token = 'token'
#
# ACCESS_KEY_ID = 'ACCESS_KEY_ID'
# ACCESS_SECRET_KEY = 'ACCESS_SECRET_KEY'
# BUCKET_NAME = 'BUCKET_NAME'

try:
    from dev_settings import logindb, passdb, dbhost, dbname, token, ACCESS_KEY_ID, ACCESS_SECRET_KEY, BUCKET_NAME
except ImportError:
    print('no file dev_settings.py in the directory')
    try:
        from prod_settings import logindb, passdb, dbhost, dbname, token, ACCESS_KEY_ID, ACCESS_SECRET_KEY, BUCKET_NAME
    except ImportError:
        raise ImportError('no file dev_settings.py or prod_settings.py in the directory')


