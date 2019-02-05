from backbone_server.errors.duplicate_key_exception import DuplicateKeyException

from swagger_server.models.individual import Individual
from swagger_server.models.attr import Attr

from backbone_server.individual.fetch import IndividualFetch
from backbone_server.sampling_event.edit import SamplingEventEdit

import psycopg2

import logging
import uuid

class IndividualEdit():

    _insert_ident_stmt = '''INSERT INTO individual_attrs
                    (individual_id, study_id, attr_type, attr_value, attr_source)
                    VALUES (%s, %s, %s, %s, %s)'''


    @staticmethod
    def get_or_create_individual_attr_id(cursor, ident, create=True):

        study_id = None
        if ident.study_name:
            study_id = SamplingEventEdit.fetch_study_id(cursor, ident.study_name, True)
        stmt = '''SELECT id FROM attrs
                JOIN individual_attrs la ON la.attr_id = attrs.id
                WHERE attr_type=%s AND attr_value=%s AND attr_source=%s'''
        args = (ident.attr_type, ident.attr_value, ident.attr_source)

        if study_id:
            stmt += ' AND study_id = %s'
            args = args + (study_id,)

        cursor.execute(stmt, args)

        res = cursor.fetchone()

        if res:
            return res[0], study_id

        if not create:
            return None, study_id

        uuid_val = uuid.uuid4()

        insert_stmt = '''INSERT INTO attrs
                    (id, study_id, attr_type, attr_value, attr_source)
                    VALUES (%s, %s, %s, %s, %s)'''

        cursor.execute(insert_stmt, (uuid_val, study_id, ident.attr_type, ident.attr_value, ident.attr_source))

        return uuid_val,study_id




    @staticmethod
    def clean_up_attrs(cursor, individual_id, old_study_id):

        if not individual_id:
            return

        if not old_study_id:
            return

        stmt = '''select a.id, a.study_id, li.individual_id FROM individual_attrs li
        JOIN attrs a ON a.id = li.attr_id
        LEFT JOIN sampling_events se ON
            (se.individual_id = li.individual_id OR se.proxy_individual_id = li.individual_id)
        WHERE se.id IS NULL AND li.individual_id = %s AND a.study_id = %s group by a.study_id, li.individual_id, a.id;'''

        cursor.execute(stmt, (individual_id, old_study_id,))

        obsolete_idents = []
        for (attr_id, study_id, individual_id) in cursor:
            obsolete_idents.append({ 'study_id': study_id, 'attr_id': attr_id})

        delete_stmt = 'DELETE FROM individual_attrs WHERE individual_id = %s AND attr_id = %s'

        for obsolete_ident in obsolete_idents:
            if obsolete_ident['study_id'] == old_study_id:
                cursor.execute(delete_stmt, (individual_id, obsolete_ident['attr_id']))

    @staticmethod
    def add_attrs(cursor, uuid_val, individual):

        studies = []
        study_attrs = {}

        try:
            if individual.attrs:
                for ident in individual.attrs:
                    attr_id, study_id = IndividualEdit.get_or_create_individual_attr_id(cursor, ident)
                    if ident.study_name:
                        if ident.attr_type in study_attrs:
                            studies = study_attrs[ident.attr_type]
                            if study_id in studies:
                                raise DuplicateKeyException("Error inserting individual - duplicate name for study {}".format(individual))
                        else:
                            study_attrs[ident.attr_type] = []
                        study_attrs[ident.attr_type].append(study_id)

                    cursor.execute('INSERT INTO individual_attrs(individual_id, attr_id) VALUES (%s, %s)',
                                   (uuid_val, attr_id))

        except psycopg2.IntegrityError as err:
            print(err.pgcode)
            print(err.pgerror)
            raise DuplicateKeyException("Error inserting individual {}".format(individual)) from err


    @staticmethod
    def update_attr_study(cursor, individual_id, old_study_id, new_study_id):

        if not individual_id:
            return

        old_attrs = []

        stmt = '''SELECT DISTINCT attr_type, attr_value, attr_source, study_name FROM individual_attrs
        JOIN attrs a ON a.id = individual_attrs.attr_id
                    JOIN studies s ON s.id = a.study_id
                    WHERE individual_id = %s AND study_id = %s'''

        cursor.execute(stmt, (individual_id, old_study_id))

        for (attr_type, attr_value, attr_source, study_name) in cursor:
            old_attrs.append(Attr(attr_type=attr_type,
                                          attr_value=attr_value,
                                          attr_source=attr_source,
                                             study_name=study_name))

        new_attrs = []

        cursor.execute(stmt, (individual_id, new_study_id))

        for (attr_type, attr_value, attr_source, study_name) in cursor:
            new_attrs.append(Attr(attr_type=attr_type,
                                          attr_value=attr_value,
                                          attr_source=attr_source,
                                             study_name=study_name))

        if len(new_attrs) == 0:
            if len(old_attrs) == 1:
                attr_id, study_id = IndividualEdit.get_or_create_individual_attr_id(cursor, old_attrs[0])
                cursor.execute('INSERT INTO individual_attrs(individual_id, attr_id) VALUES (%s, %s)',
                                   (individual_id, attr_id))
                cursor.execute('UPDATE attrs SET study_id=%s WHERE id=%s',(new_study_id, attr_id))

    @staticmethod
    def check_for_duplicate(cursor, individual, individual_id):

        for ident in individual.attrs:
            (match, study) = IndividualEdit.get_or_create_individual_attr_id(cursor, ident,
                                                            create=False)
            if match:
                raise DuplicateKeyException("Error updating individual - duplicate with {}".format(ident))
