
import logging

import urllib

from backbone_server.sampling_event.post import SamplingEventPost
from backbone_server.sampling_event.put import SamplingEventPut
from backbone_server.sampling_event.get import SamplingEventGetById
from backbone_server.sampling_event.delete import SamplingEventDelete
from backbone_server.sampling_event.get_by_identifier import SamplingEventGetByIdentifier
from backbone_server.sampling_event.get_by_location import SamplingEventsGetByLocation
from backbone_server.sampling_event.get_by_study import SamplingEventsGetByStudy
from backbone_server.sampling_event.get_by_taxa import SamplingEventsGetByTaxa

from backbone_server.event_set.get import EventSetGetById

from swagger_server.models.sampling_events import SamplingEvents

from backbone_server.controllers.base_controller  import BaseController

from backbone_server.errors.duplicate_key_exception import DuplicateKeyException
from backbone_server.errors.missing_key_exception import MissingKeyException
from backbone_server.errors.permission_exception import PermissionException

class SamplingEventController(BaseController):

    def create_sampling_event(self, samplingEvent, user = None, auths = None):
        """
        create_sampling_event
        Create a samplingEvent
        :param samplingEvent: 
        :type samplingEvent: dict | bytes

        :rtype: SamplingEvent
        """

        try:
            study_id = samplingEvent.study_name

            self.check_permissions(study_id, auths)
        except PermissionException as pe:
            self.log_action(user, 'create_sampling_event', None, samplingEvent, None, 403)
            return pe.message, 403

        retcode = 201
        samp = None

        try:
            post = SamplingEventPost(self.get_connection())

            samp = post.post(samplingEvent)
        except DuplicateKeyException as dke:
            logging.getLogger(__name__).error("create_samplingEvent: {}".format(repr(dke)))
            retcode = 422

        self.log_action(user, 'create_sampling_event', None, samplingEvent, samp, retcode)

        return samp, retcode


    def delete_sampling_event(self, samplingEventId, user = None, auths = None):
        """
        deletes an samplingEvent
        
        :param samplingEventId: ID of samplingEvent to fetch
        :type samplingEventId: str

        :rtype: None
        """

        try:
            self.check_permissions(None, auths)
        except PermissionException as pe:
            self.log_action(user, 'delete_sampling_event', samplingEventId, None, None, 403)
            return pe.message, 403

        delete = SamplingEventDelete(self.get_connection())

        retcode = 200
        samp = None

        try:
            delete.delete(samplingEventId)
        except MissingKeyException as dme:
            logging.getLogger(__name__).error("delete_samplingEvent: {}".format(repr(dme)))
            retcode = 404

        self.log_action(user, 'delete_sampling_event', samplingEventId, None, None, retcode)

        return None, retcode


    def download_sampling_event(self, samplingEventId, user = None, auths = None):
        """
        fetches an samplingEvent
        
        :param samplingEventId: ID of samplingEvent to fetch
        :type samplingEventId: str

        :rtype: SamplingEvent
        """

        try:
            self.check_permissions(None, auths)
        except PermissionException as pe:
            self.log_action(user, 'download_sampling_event', samplingEventId, None, None, 403)
            return pe.message, 403

        get = SamplingEventGetById(self.get_connection())

        retcode = 200
        samp = None

        try:
            samp = get.get(samplingEventId)
        except MissingKeyException as dme:
            logging.getLogger(__name__).error("download_samplingEvent: {}".format(repr(dme)))
            retcode = 404

        self.log_action(user, 'download_sampling_event', samplingEventId, None, samp, retcode)

        return samp, retcode

    def download_sampling_events_by_event_set(self, event_set_id, start, count, user = None, auths = None):
        """
        fetches samplingEvents for a event_set
        
        :param event_set_id: event_set
        :type event_set_id: str

        :rtype: SamplingEvents
        """

        try:
            study_id = None;

            self.check_permissions(study_id, auths)
        except PermissionException as pe:
            self.log_action(user, 'download_sampling_events_by_event_set', event_set_id, None, None, 403)
            return pe.message, 403

        retcode = 200
        samp = None

        try:
            get = EventSetGetById(self.get_connection())
            evntSt = get.get(event_set_id, start, count)

            samp = evntSt.members

        except MissingKeyException as dme:
            logging.getLogger(__name__).error("download_sampling_events_by_event_set: {}".format(repr(dme)))
            retcode = 404

        self.log_action(user, 'download_sampling_events_by_event_set', event_set_id, None, samp, retcode)

        return samp, retcode

    def download_sampling_events_by_identifier(self, propName, propValue, studyName, user = None, auths = None):
        """
        fetches a samplingEvent by property value
        
        :param propName: name of property to search
        :type propName: str
        :param propValue: matching value of property to search
        :type propValue: str

        :rtype: SamplingEvent
        """

        try:
            self.check_permissions(None, auths)
        except PermissionException as pe:
            self.log_action(user, 'download_sampling_events_by_identifier', propName + '/' +
                            propValue, None, None, 403)
            return pe.message, 403

        get = SamplingEventGetByIdentifier(self.get_connection())

        retcode = 200
        samp = None

        try:
            propValue = urllib.parse.unquote_plus(propValue)
            samp = get.get(propName, propValue, studyName)
        except MissingKeyException as dme:
            logging.getLogger(__name__).error("download_samplingEvent: {}".format(repr(dme)))
            retcode = 404

        self.log_action(user, 'download_sampling_events_by_identifier', propName + '/' +
                        propValue, None, samp, retcode)

        return samp, retcode

    def download_sampling_events_by_location(self, locationId, start, count, user = None, auths = None):
        """
        fetches samplingEvents for a location
        
        :param locationId: location
        :type locationId: str

        :rtype: SamplingEvents
        """

        try:
            self.check_permissions(None, auths)
        except PermissionException as pe:
            self.log_action(user, 'download_sampling_events_by_location', locationId, None, None, 403)
            return pe.message, 403

        get = SamplingEventsGetByLocation(self.get_connection())

        retcode = 200
        samp = None

        try:
            samp = get.get(locationId, start, count)
        except MissingKeyException as dme:
            logging.getLogger(__name__).error("download_samplingEvent: {}".format(repr(dme)))
            retcode = 404

        self.log_action(user, 'download_sampling_events_by_location', locationId, None, samp,
                        retcode)

        return samp, retcode

    def download_sampling_events_by_study(self, studyName, start, count, user = None, auths = None):
        """
        fetches samplingEvents for a study
        
        :param studyName: location
        :type studyName: str

        :rtype: SamplingEvents
        """

        try:
            study_id = studyName;

            self.check_permissions(study_id, auths)
        except PermissionException as pe:
            self.log_action(user, 'download_sampling_events_by_study', studyName, None, None, 403)
            return pe.message, 403

        get = SamplingEventsGetByStudy(self.get_connection())

        retcode = 200
        samp = None

        try:
            samp = get.get(studyName, start, count)
        except MissingKeyException as dme:
            logging.getLogger(__name__).error("download_samplingEvent: {}".format(repr(dme)))
            retcode = 404

        self.log_action(user, 'download_sampling_events_by_study', studyName, None, samp, retcode)

        return samp, retcode

    def download_sampling_events_by_taxa(self, taxaId, start, count, user = None, auths = None):
        """
        fetches samplingEvents for a taxa
        
        :param taxaId: taxa
        :type taxaId: str

        :rtype: SamplingEvents
        """

        try:
            study_id = None;

            self.check_permissions(study_id, auths)
        except PermissionException as pe:
            self.log_action(user, 'download_sampling_events_by_taxa', taxaId, None, None, 403)
            return pe.message, 403

        get = SamplingEventsGetByTaxa(self.get_connection())

        retcode = 200
        samp = None

        try:
            samp = get.get(taxaId, start, count)
        except MissingKeyException as dme:
            logging.getLogger(__name__).error("download_sampling_events_by_taxa: {}".format(repr(dme)))
            retcode = 404

        self.log_action(user, 'download_sampling_events_by_taxa', taxaId, None, samp, retcode)

        return samp, retcode

    def update_sampling_event(self, samplingEventId, samplingEvent, user = None, auths = None):
        """
        updates an samplingEvent
        
        :param samplingEventId: ID of samplingEvent to update
        :type samplingEventId: str
        :param samplingEvent: 
        :type samplingEvent: dict | bytes

        :rtype: SamplingEvent
        """

        try:
            study_id = samplingEvent.study_name

            self.check_permissions(study_id, auths)
        except PermissionException as pe:
            self.log_action(user, 'update_sampling_event', samplingEventId, samplingEvent, None, 403)
            return pe.message, 403

        retcode = 200
        samp = None

        try:
            put = SamplingEventPut(self.get_connection())

            samp = put.put(samplingEventId, samplingEvent)
        except DuplicateKeyException as dke:
            logging.getLogger(__name__).error("update_samplingEvent: {}".format(repr(dke)))
            retcode = 422
        except MissingKeyException as dme:
            logging.getLogger(__name__).error("update_samplingEvent: {}".format(repr(dme)))
            retcode = 404

        self.log_action(user, 'update_sampling_event', samplingEventId, samplingEvent, samp, retcode)

        return samp, retcode

