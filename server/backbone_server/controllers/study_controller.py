import logging

from backbone_server.errors.missing_key_exception import MissingKeyException
from backbone_server.errors.integrity_exception import IntegrityException
from backbone_server.study.gets import StudiesGet
from backbone_server.study.get import StudyGet
from backbone_server.study.put import StudyPut

from backbone_server.controllers.base_controller import BaseController

from backbone_server.controllers.decorators import apply_decorators


@apply_decorators
class StudyController(BaseController):

    def download_studies(self, start=None, count=None, user=None, auths=None):
        """
        fetches studies

        :param start: for pagination start the result set at a record x
        :type start: int
        :param count: for pagination the number of entries to return
        :type count: int

        :rtype: Studies
        """

        get = StudiesGet(self.get_connection())

        studies = get.get()

        return studies, 200

    def download_study(self, study_name, user=None, auths=None):
        """
        fetches a study

        :param study_name: ID of study to fetch
        :type study_name: str

        :rtype: Study
        """

        get = StudyGet(self.get_connection())

        study = None
        retcode = 200
        try:
            study = get.get(study_name)
        except MissingKeyException as dme:
            logging.getLogger(__name__).debug(
                "update_study: {}".format(repr(dme)))
            retcode = 404
            study = str(dme)

        return study, retcode

    def update_study(self, study_name, study, user=None, auths=None):
        """
        updates a study

        :param study_name: ID of study to update
        :type study_name: str
        :param study:
        :type study: dict | bytes

        :rtype: Study
        """

        retcode = 200
        updated_study = None

        try:
            put = StudyPut(self.get_connection())

            updated_study = put.put(study_name, study)
        except IntegrityException as dme:
            logging.getLogger(__name__).debug(
                "update_study: {}".format(repr(dme)))
            retcode = 422
            updated_study = str(dme)
        except MissingKeyException as dme:
            logging.getLogger(__name__).debug(
                "update_study: {}".format(repr(dme)))
            retcode = 404
            updated_study = str(dme)

        return updated_study, retcode
