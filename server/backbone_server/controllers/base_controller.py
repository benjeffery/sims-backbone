import logging
import os
import json

class BaseController():

    _connection = None
    _logger = None

    def __init__ (self):
        if os.getenv('BBDEBUG'):
            logging.basicConfig(level=logging.DEBUG)
        self._logger = logging.getLogger(__name__)
        self._connection = self._init_connection()

    def __del__(self):
        if self._connection:
            self._connection.close()

    def get_connection(self):
        return self._connection

    def _init_connection(self):
        _postgres = True

        if _postgres:
            import psycopg2
            from psycopg2.extras import register_uuid
            from psycopg2.extras import LoggingConnection

            config = {
                'user': os.getenv('DB_USER',os.getenv('USER')),
                'database': os.getenv('DATABASE','backbone_service'),
                'password': os.getenv('DB_PASSWORD',None),
                'host': os.getenv('DB_HOST','localhost'),
            }

            psycopg2.extensions.register_type(register_uuid())
            psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
            psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
            conn = psycopg2.connect(connection_factory=LoggingConnection, **config )
            conn.initialize(self._logger)
    #        cur = conn.cursor()
    #        cur.execute("SET search_path TO " + 'backbone,public,contrib')
    #        cur.close()
        else:
            import mysql.connector
            from mysql.connector import errorcode
            config = {
                'user': 'iwright',
                'database': 'backbone_service'
            }

            try:
                conn = mysql.connector.connect(**config)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    self._logger.critical("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    self._logger.critical("Database does not exist")
                else:
                    self._logger.critical(err)
        return conn

    """
    Convert the connexion token_info (OAuth) response into something that can be made consistent
    with AWS Custom Auth details
    """
    def token_info(self, tok_info):
        resp = []
        if tok_info and 'memberOf' in tok_info:
            for auth_grp in tok_info['memberOf']:
                dns = auth_grp.split(',')
                cn = dns[0].split('=')[1]
                resp.append(cn)

        return resp

    """
    Convert AWS authorizer into consistent format
    """
    def authorizer(self, authorizer):
        resp = []
        return resp

    """
    Throw an exception if no permission
    """
    def check_permissions(self, study_id, perms):

        pass


    def log_action(self, user, action, entity_id, content, result, retcode):

        try:
            #content_json = None
            #if content:
            #    content_json = json.dumps(content.to_dict())
            #result_json = None
            #if result:
            #    result_json = json.dumps(content.to_dict())
            args = (user, action, entity_id, str(content), str(result), retcode)

            self._logger.debug("log_action {}".format(args))

            if action.startswith('create') or action.startswith('update') or \
                    action.startswith('delete') or retcode != 200:
                with self._connection:
                    with self._connection.cursor() as cursor:
                        cursor.execute('''INSERT INTO archive (submitter, action_id, entity_id,
                                       input_value, output_value, result_code) VALUES (%s, %s, %s, %s, %s, %s)''', args)
        except Exception:
            #Don't want to fail if it's just a logging problem
            args = (user, action, entity_id, content, result, retcode)
            print("log_action {}".format(args))
            self._logger.exception('Failed to log action')
