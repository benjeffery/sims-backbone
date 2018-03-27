from swagger_server.models.event_set import EventSet
from swagger_server.models.event_set_note import EventSetNote
from datetime import date, datetime
from typing import List, Dict
from six import iteritems

import logging

from backbone_server.controllers.event_set_controller import EventSetController

from local.base_local_api import BaseLocalApi

class LocalEventSetApi(BaseLocalApi):

    def __init__(self, api_client=None):

        super().__init__(api_client)

        self.event_set_controller = EventSetController()

    def create_event_set(self, eventSetId, user = None, token_info = None):
        """
        creates an eventSet
        
        :param eventSetId: ID of eventSet to create
        :type eventSetId: str
        :param eventSet: 
        :type eventSet: dict | bytes

        :rtype: EventSet
        """
        logging.basicConfig(level=logging.DEBUG)

        (ret, retcode) = self.event_set_controller.create_event_set(eventSetId, user,
                                                     self.event_set_controller.token_info(token_info))

        return self.create_response(ret, retcode, 'EventSet')

    def create_event_set_item(self, eventSetId, samplingEventId, user = None, token_info = None):
        """
        Adds a samplingEvent to an eventSet
        
        :param eventSetId: ID of eventSet to modify
        :type eventSetId: str
        :param samplingEventId: ID of samplingEvent to add to the set
        :type samplingEventId: str

        :rtype: EventSet
        """
        (ret, retcode) = self.event_set_controller.create_event_set_item(eventSetId, samplingEventId, user,
                                                      self.event_set_controller.token_info(token_info))
        return self.create_response(ret, retcode, 'EventSet')


    def create_event_set_note(self, eventSetId, noteId, note, user = None, token_info = None):
        """
        Adds a note to an eventSet
        
        :param eventSetId: ID of eventSet to modify
        :type eventSetId: str
        :param noteId: ID of note to modify in the set
        :type noteId: str
        :param note: 
        :type note: dict | bytes

        :rtype: None
        """
        (ret, retcode) = self.event_set_controller.create_event_set_note(eventSetId, noteId, note, user,
                                                      self.event_set_controller.token_info(token_info))

        return self.create_response(ret, retcode)

    def delete_event_set(self, eventSetId, user = None, token_info = None):
        """
        deletes an eventSet
        
        :param eventSetId: ID of eventSet to delete
        :type eventSetId: str

        :rtype: None
        """
        (ret, retcode) = self.event_set_controller.delete_event_set(eventSetId, user, self.event_set_controller.token_info(token_info))

        return self.create_response(ret, retcode)

    def delete_event_set_item(self, eventSetId, samplingEventId, user = None, token_info = None):
        """
        deletes a samplingEvent from an eventSet
        
        :param eventSetId: ID of eventSet to modify
        :type eventSetId: str
        :param samplingEventId: ID of samplingEvent to remove from the set
        :type samplingEventId: str

        :rtype: None
        """
        (ret, retcode) = self.event_set_controller.delete_event_set_item(eventSetId, samplingEventId, user,
                                                      self.event_set_controller.token_info(token_info))
        return self.create_response(ret, retcode)


    def delete_event_set_note(self, eventSetId, noteId, user = None, token_info = None):
        """
        deletes an eventSet note
        
        :param eventSetId: ID of eventSet to modify
        :type eventSetId: str
        :param noteId: ID of note to remove from the set
        :type noteId: str

        :rtype: None
        """
        (ret, retcode) = self.event_set_controller.delete_event_set_note(eventSetId, noteId, user,
                                                      self.event_set_controller.token_info(token_info))

        return self.create_response(ret, retcode)

    def download_event_set(self, eventSetId, start=None, count=None, user = None, token_info = None):
        """
        fetches an eventSet
        
        :param eventSetId: ID of eventSet to fetch
        :type eventSetId: str

        :rtype: EventSet
        """
        (ret, retcode) = self.event_set_controller.download_event_set(eventSetId, start, count, user,
                                                      self.event_set_controller.token_info(token_info))

        return self.create_response(ret, retcode, 'EventSet')

    def download_event_sets(self, user = None, token_info = None):
        """
        fetches eventSets
        

        :rtype: EventSets
        """
        (ret, retcode) = self.event_set_controller.download_event_sets(user,
                                                      self.event_set_controller.token_info(token_info))
        return self.create_response(ret, retcode, 'EventSets')

    def update_event_set(self, eventSetId, eventSet, user = None, token_info = None):
        """
        updates an eventSet
        
        :param eventSetId: ID of eventSet to update
        :type eventSetId: str
        :param eventSet: 
        :type eventSet: dict | bytes

        :rtype: EventSet
        """
        (ret, retcode) = self.event_set_controller.update_event_set(eventSetId, eventSet, user,
                                                      self.event_set_controller.token_info(token_info))
        return self.create_response(ret, retcode, 'EventSet')


    def update_event_set_note(self, eventSetId, noteId, note, user = None, token_info = None):
        """
        Adds a note to an eventSet
        
        :param eventSetId: ID of eventSet to modify
        :type eventSetId: str
        :param noteId: ID of note to modify in the set
        :type noteId: str
        :param note: 
        :type note: dict | bytes

        :rtype: None
        """

        (ret, retcode) = self.event_set_controller.update_event_set_note(eventSetId, noteId, note, user,
                                                      self.event_set_controller.token_info(token_info))
        return self.create_response(ret, retcode)