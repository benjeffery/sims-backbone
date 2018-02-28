from backbone_server.errors.duplicate_key_exception import DuplicateKeyException

from backbone_server.sampling_event.edit import SamplingEventEdit
from backbone_server.sampling_event.fetch import SamplingEventFetch

from swagger_server.models.sampling_event import SamplingEvent

import mysql.connector
from mysql.connector import errorcode
import psycopg2

import logging
import uuid

class SamplingEventPost():

    def __init__(self, conn):
        self._logger = logging.getLogger(__name__)
        self._connection = conn


    def post(self, sampling_event):

        with self._connection:
            with self._connection.cursor() as cursor:

                uuid_val = uuid.uuid4()

                study_id = SamplingEventEdit.fetch_study_id(cursor, sampling_event.study_name, True)
                partner_species = SamplingEventEdit.fetch_partner_species(cursor, sampling_event, study_id)

                stmt = '''INSERT INTO sampling_events 
                            (id, study_id, doc, doc_accuracy, location_id, proxy_location_id, partner_species_id) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)'''
                args = (uuid_val,study_id, sampling_event.doc, sampling_event.doc_accuracy,
                        sampling_event.location_id, sampling_event.proxy_location_id,
                        partner_species)

                try:
                    cursor.execute(stmt, args)

                    SamplingEventEdit.add_identifiers(cursor, uuid_val, sampling_event)

                except mysql.connector.Error as err:
                    if err.errno == errorcode.ER_DUP_ENTRY:
                        raise DuplicateKeyException("Error inserting sampling_event {}".format(sampling_event)) from err
                    else:
                        self._logger.fatal(repr(error))
                except psycopg2.IntegrityError as err:
                    print(err.pgcode)
                    print(err.pgerror)
                    raise DuplicateKeyException("Error inserting sampling_event {}".format(sampling_event)) from err
                except DuplicateKeyException as err:
                    raise err

                sampling_event = SamplingEventFetch.fetch(cursor, uuid_val)

        return sampling_event

