from openapi_server.models.sampling_event import SamplingEvent
from openapi_server.models.sampling_events import SamplingEvents
from openapi_server.models.location import Location
from openapi_server.models.attr import Attr
from backbone_server.errors.missing_key_exception import MissingKeyException

from backbone_server.location.fetch import LocationFetch
from backbone_server.sampling_event.fetch import SamplingEventFetch

from backbone_server.sampling_event.edit import SamplingEventEdit

import logging


class SamplingEventsGetByLocation():

    def __init__(self, conn):
        self._logger = logging.getLogger(__name__)
        self._connection = conn

    def get(self, location_id, start, count):

        with self._connection:
            with self._connection.cursor() as cursor:

                locations = {}

                try:
                    location = LocationFetch.fetch(cursor, location_id)
                except MissingKeyException as mke:
                    raise mke

                fields = '''SELECT sampling_events.id'''
                query_body = ''' FROM sampling_events
                        WHERE location_id = %s OR proxy_location_id = %s'''
                args = (location_id, location_id,)

                count_args = args
                count_query = 'SELECT COUNT(sampling_events.id) ' + query_body

                query_body = query_body + ''' ORDER BY doc, id'''

                if not (start is None and count is None):
                    query_body = query_body + ' LIMIT %s OFFSET %s'
                    args = args + (count, start)

                sampling_events = SamplingEvents(sampling_events=[], count=0)

                stmt = fields + query_body

                cursor.execute(stmt, args)

                samp_ids = []
                for samp_id in cursor:
                    samp_ids.append(samp_id)

                locations = {}
                sampling_events.sampling_events = []
                for samp_id in samp_ids:
                    event = SamplingEventFetch.fetch(cursor, samp_id, locations)
                    sampling_events.sampling_events.append(event)
                sampling_events.locations = locations

                if not (start is None and count is None):
                    cursor.execute(count_query, count_args)
                    sampling_events.count = cursor.fetchone()[0]
                else:
                    sampling_events.count = len(sampling_events.sampling_events)

                sampling_events.attr_types = []


                for samp_id in samp_ids:
                    col_query = '''select distinct attr_type from sampling_event_attrs se
                    JOIN attrs a ON se.attr_id=a.id
                    WHERE sampling_event_id = %s'''

                    cursor.execute(col_query, (samp_id,))
                    for (attr_type,) in cursor:
                        if attr_type not in sampling_events.attr_types:
                            sampling_events.attr_types.append(attr_type)

        return sampling_events
