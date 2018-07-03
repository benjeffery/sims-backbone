from backbone_server.errors.duplicate_key_exception import DuplicateKeyException
from backbone_server.errors.missing_key_exception import MissingKeyException

from backbone_server.assay_datum.edit import AssayDatumEdit
from backbone_server.assay_datum.fetch import AssayDatumFetch

from swagger_server.models.assay_datum import AssayDatum

import psycopg2

import logging

class AssayDatumPut():

    def __init__(self, conn):
        self._logger = logging.getLogger(__name__)
        self._connection = conn


    def put(self, assay_datum_id, assay_datum):

        with self._connection:
            with self._connection.cursor() as cursor:

                stmt = '''SELECT id FROM assay_data WHERE id = %s'''
                cursor.execute( stmt, (assay_datum_id,))

                existing_assay_datum = None

                for (assay_datum_id,) in cursor:
                    existing_assay_datum = AssayDatum(assay_datum_id)

                if not existing_assay_datum:
                    raise MissingKeyException("Could not find assay_datum to update {}".format(assay_datum_id))

                stmt = '''UPDATE assay_data 
                            SET derived_sample_id = %s,
                            ebi_run_acc = %s
                            WHERE id = %s'''
                args = (assay_datum.derived_sample_id,
                        assay_datum.ebi_run_acc,
                        assay_datum_id)

                try:
                    cursor.execute(stmt, args)
                    rc = cursor.rowcount

                    cursor.execute('DELETE FROM assay_datum_attrs WHERE assay_datum_id = %s',
                                   (assay_datum_id,))

                    AssayDatumEdit.add_attrs(cursor, assay_datum_id, assay_datum)

                except psycopg2.IntegrityError as err:
                    raise DuplicateKeyException("Error updating assay_datum {}".format(assay_datum)) from err
                except DuplicateKeyException as err:
                    raise err

                assay_datum = AssayDatumFetch.fetch(cursor, assay_datum_id)

        if rc != 1:
            raise MissingKeyException("Error updating assay_datum {}".format(assay_datum_id))


        return assay_datum