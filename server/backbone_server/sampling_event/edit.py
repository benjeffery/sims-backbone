from backbone_server.errors.duplicate_key_exception import DuplicateKeyException
from backbone_server.errors.nested_edit_exception import NestedEditException

from backbone_server.location.fetch import LocationFetch
import uuid

class SamplingEventEdit():


    @staticmethod
    def check_location_details(cursor, location_id, location):

        current_location = None

        if location_id:
            current_location = LocationFetch.fetch(cursor, location_id)

            cli = current_location.attrs

            #It's OK if the location id is set but the location object not filled in
            if location:
                idents = location.attrs

                if location != current_location:
                    raise NestedEditException("Implied location edit not allowed for {}".format(location_id))

        return current_location

    @staticmethod
    def fetch_study_id(cursor, study_name, create):
        study_id = None

        if not study_name:
            return study_id

        cursor.execute('''SELECT id FROM studies WHERE study_code = %s''', (study_name[:4],))
        result = cursor.fetchone()

        if result:
            study_id = result[0]
        else:
            if not create:
                return None
            study_id = uuid.uuid4()
            cursor.execute('''INSERT INTO studies (id, study_code, study_name) VALUES (%s, %s,
                           %s)''', (study_id, study_name[:4], study_name))
        return study_id

    @staticmethod
    def fetch_partner_species(cursor, sampling_event, study_id):
        partner_species = None

        if not sampling_event.partner_species:
            return partner_species

        cursor.execute('''SELECT id FROM partner_species_identifiers WHERE study_id = %s AND
                       partner_species = %s''',
                           (study_id, sampling_event.partner_species))
        result = cursor.fetchone()

        if result:
            partner_species = result[0]
        else:
            partner_species = uuid.uuid4()
            cursor.execute('''INSERT INTO partner_species_identifiers (id, study_id,
                           partner_species) VALUES (%s, %s, %s)''',
                           (partner_species, study_id, sampling_event.partner_species))
        return partner_species

    @staticmethod
    def add_attrs(cursor, uuid_val, sampling_event):
        if sampling_event.attrs:
            for ident in sampling_event.attrs:
                if not (ident.attr_type == 'partner_id' or \
                        ident.attr_type == 'individual_id'):
                    cursor.execute('''SELECT * FROM attrs
                                   JOIN sampling_event_attrs ON sampling_event_attrs.attr_id =
                                   attrs.id
                                   WHERE attr_type = %s AND attr_value = %s AND
                                   attr_source = %s''',
                                   (ident.attr_type, ident.attr_value,
                                    ident.attr_source))
                    if cursor.fetchone():
                        raise DuplicateKeyException("Error inserting sampling_event attr {} {}"
                                                    .format(ident.attr_type, sampling_event))

                    cursor.execute('''SELECT * FROM attrs
                                   JOIN sampling_event_attrs ON sampling_event_attrs.attr_id =
                                   attrs.id
                                   WHERE attr_type = %s AND attr_value = %s AND
                                   sampling_event_id != %s''',
                                   (ident.attr_type, ident.attr_value,
                                    uuid_val))
                    if cursor.fetchone():
                        raise DuplicateKeyException("Error inserting sampling_event attr {} {}"
                                                    .format(ident.attr_type, sampling_event))

                attr_id = uuid.uuid4()
                stmt = '''INSERT INTO attrs
                    (id, attr_type, attr_value, attr_source)
                    VALUES (%s, %s, %s, %s)'''
                cursor.execute(stmt, (attr_id, ident.attr_type, ident.attr_value,
                                      ident.attr_source))

                stmt = '''INSERT INTO sampling_event_attrs
                    (sampling_event_id, attr_id)
                    VALUES (%s, %s)'''
                cursor.execute(stmt, (uuid_val, attr_id))




    @staticmethod
    def clean_up_taxonomies(cursor):

        unused_species = '(select partner_species_identifiers.id from partner_species_identifiers LEFT JOIN studies ON studies.id = study_id LEFT JOIN sampling_events ON sampling_events.study_id = studies.id WHERE sampling_events.id IS NULL)'
        unused_idents = 'DELETE FROM taxonomy_identifiers WHERE partner_species_id IN ' + unused_species
        unused_species_idents = 'DELETE FROM partner_species_identifiers WHERE id IN ' + unused_species

        cursor.execute(unused_idents)
        cursor.execute(unused_species_idents)
