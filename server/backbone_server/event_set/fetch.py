from swagger_server.models.sampling_event import SamplingEvent
from swagger_server.models.sampling_events import SamplingEvents
from swagger_server.models.event_set_note import EventSetNote
from swagger_server.models.event_set import EventSet

from swagger_server.models.location import Location
from swagger_server.models.identifier import Identifier

from backbone_server.sampling_event.fetch import SamplingEventFetch

from backbone_server.errors.missing_key_exception import MissingKeyException

import logging

from backbone_server.location.fetch import LocationFetch

class EventSetFetch():

    @staticmethod
    def fetch_event_set_id(cursor, event_set_name):

        stmt = '''SELECT id FROM event_sets WHERE event_set_name = %s'''

        cursor.execute( stmt, (event_set_name,))

        res = cursor.fetchone()

        if not res:
            raise MissingKeyException("No such event set {}".format(event_set_name))

        return res[0]

    @staticmethod
    def fetch(cursor, event_set_id, start, count):

        if not event_set_id:
            return None

        stmt = '''SELECT event_set_name FROM event_sets WHERE id = %s'''

        cursor.execute(stmt, (event_set_id,))

        res = cursor.fetchone()

        event_set = EventSet(res[0])

        fields = '''SELECT id, study_id, doc, doc_accuracy,
                        partner_species, partner_species_id,
                        location_id, latitude, longitude, accuracy, curated_name, curation_method, country, notes, partner_name,
                        proxy_location_id, proxy_latitude, proxy_longitude, proxy_accuracy,
                        proxy_curated_name, proxy_curation_method, proxy_country, proxy_notes,
                        proxy_partner_name'''
        query_body = ''' FROM v_sampling_events
                        JOIN event_set_members esm ON esm.sampling_event_id = v_sampling_events.id
                        WHERE esm.event_set_id = %s'''


        args = (event_set_id,)

        count_args = args
        count_query = 'SELECT COUNT(v_sampling_events.id) ' + query_body

        query_body = query_body + ''' ORDER BY doc, study_id, id'''

        if not (start is None and count is None):
            query_body = query_body + ' LIMIT %s OFFSET %s'
            args = args + (count, start)

        samples = SamplingEvents([], 0)

        stmt = fields + query_body

        cursor.execute(stmt, args)

        samples.sampling_events = SamplingEventFetch.load_sampling_events(cursor, True)

        if not (start is None and count is None):
            cursor.execute(count_query, count_args)
            samples.count = cursor.fetchone()[0]
        else:
            samples.count = len(samples.sampling_events)

        event_set.members = samples

        stmt = '''SELECT note_name, note_text FROM event_set_notes WHERE event_set_id = %s'''

        cursor.execute(stmt, (event_set_id,))

        event_set.notes = []
        for (name, value) in cursor:
            note = EventSetNote(name, value)
            event_set.notes.append(note)

        if len(event_set.notes) == 0:
            event_set.notes = None

        return event_set
