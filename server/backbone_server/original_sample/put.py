from backbone_server.errors.duplicate_key_exception import DuplicateKeyException
from backbone_server.errors.missing_key_exception import MissingKeyException

from backbone_server.original_sample.edit import OriginalSampleEdit
from backbone_server.original_sample.fetch import OriginalSampleFetch
from backbone_server.location.edit import LocationEdit

from swagger_server.models.original_sample import OriginalSample

import psycopg2

import logging

class OriginalSamplePut():

    def __init__(self, conn):
        self._logger = logging.getLogger(__name__)
        self._connection = conn


    def put(self, original_sample_id, original_sample):

        with self._connection:
            with self._connection.cursor() as cursor:

                stmt = '''SELECT id, study_id FROM original_samples WHERE  id = %s'''
                cursor.execute( stmt, (original_sample_id,))

                existing_original_sample = None

                for (original_sample_id, original_study_id) in cursor:
                    existing_original_sample = OriginalSample(original_sample_id)

                if not existing_original_sample:
                    raise MissingKeyException("Could not find original_sample to update {}".format(original_sample_id))

                study_id = OriginalSampleEdit.fetch_study_id(cursor, original_sample.study_name, True)

                if study_id != original_study_id:
                    pass
                stmt = '''UPDATE original_samples 
                            SET study_id = %s, sampling_event_id = %s,
                            days_in_culture = %s
                            WHERE id = %s'''
                args = (study_id, original_sample.sampling_event_id,
                        original_sample.days_in_culture,
                        original_sample_id)

                try:
                    cursor.execute(stmt, args)
                    rc = cursor.rowcount

                    cursor.execute('DELETE FROM original_sample_attrs WHERE original_sample_id = %s',
                                   (original_sample_id,))

                    OriginalSampleEdit.add_attrs(cursor, original_sample_id, original_sample)

                except psycopg2.IntegrityError as err:
                    raise DuplicateKeyException("Error updating original_sample {}".format(original_sample)) from err
                except DuplicateKeyException as err:
                    raise err

                original_sample = OriginalSampleFetch.fetch(cursor, original_sample_id)

        if rc != 1:
            raise MissingKeyException("Error updating original_sample {}".format(original_sample_id))


        return original_sample