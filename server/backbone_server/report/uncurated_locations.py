
import logging

from openapi_server.models.studies import Studies
from backbone_server.study.fetch import StudyFetch


class UncuratedLocations():

    def __init__(self, conn):
        self._logger = logging.getLogger(__name__)
        self._connection = conn

    def get(self):

        response = Studies([], 0)

        with self._connection:
            with self._connection.cursor() as cursor:

                # , curated_name, accuracy, country, partner_name
                stmt = '''select distinct studies.study_name AS study_id FROM sampling_events
                LEFT JOIN studies ON studies.id = sampling_events.study_id
                where curated_name is NULL or accuracy IS NULL OR country IS NULL ORDER BY study_id;'''

                cursor.execute(stmt)

                studies = []

                for (study_name,) in cursor:
                    studies.append(study_name)

                for study_id in studies:
                    study = StudyFetch.fetch(cursor, study_id)
                    response.studies.append(study)
                    response.count = response.count + 1

        return response
