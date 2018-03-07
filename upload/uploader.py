from __future__ import print_function
import json
import csv
import re
import time
import datetime
import logging
import sys
import swagger_client
from swagger_client.rest import ApiException

from decimal import *

import urllib.parse
from copy import deepcopy

from pprint import pprint
from pprint import pformat

import os
import requests

class Uploader():

    _location_cache = {}
    _sample_cache = {}

    _auth_token = None

    _data_file = None

    _event_set = None

    _message_buffer = []

    def __init__(self, config_file):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        # Configure OAuth2 access token for authorization: OauthSecurity
        self._auth_token = self.get_access_token(config_file)

        self._use_message_buffer = False

    @property
    def message_buffer(self):
        return self._message_buffer

    @property
    def use_message_buffer(self):
        return self._use_message_buffer

    @use_message_buffer.setter
    def use_message_buffer(self, use_buffer):
        self._use_message_buffer = use_buffer

    
    def get_access_token(self, config_file):

        with open(config_file) as json_file:
            args = json.load(json_file)
            r = requests.get(os.getenv('TOKEN_URL'), args, headers = { 'service': 'http://localhost/full-map' })
            at = r.text.split('=')
            token = at[1].split('&')[0]
            return(token)

    def setup(self, filename):

        self._data_file = os.path.basename(filename)

        self._event_set = os.path.basename(filename).split('.')[0]

        configuration = swagger_client.Configuration()
        configuration.access_token = self._auth_token

        api_instance = swagger_client.EventSetApi(swagger_client.ApiClient(configuration))
        event_set_id = self._event_set # str | ID of eventSet to create

        try:
            # creates an eventSet
            api_response = api_instance.create_event_set(event_set_id)
        except ApiException as e:
            if e.status != 422: #Already exists
                print("Exception when calling EventSetApi->create_event_set: %s\n" % e)

    def report(self, message, values):

        if values:
            msg = "{}\t{}".format(message, sorted(values.items(), key=lambda x: x))
        else:
            msg = message

        if self.use_message_buffer:
            self._message_buffer.append(msg)
        else:
            print(msg)

    def load_data_file(self, data_def, filename):

        self.setup(filename)

        input_stream = open(filename)

        return self.load_data(data_def, input_stream, True, False)


    def parse_date(self, defn, date_value):

        accuracy = None
        data_value = date_value.split(' ')[0]
        try:
            if 'date_format' in defn:
                date_format = defn['date_format']
            else:
                date_format = '%Y-%m-%d'
            data_value = datetime.datetime(*(time.strptime(data_value, date_format))[:6]).date()
        except ValueError as dpe:
            try:
                date_format = '%d/%m/%Y'
                data_value = datetime.datetime(*(time.strptime(data_value, date_format))[:6]).date()
            except ValueError as dpe:
                try:
                    date_format = '%d-%b-%Y'
                    data_value = datetime.datetime(*(time.strptime(data_value, date_format))[:6]).date()
                except ValueError as dpe:
                    try:
                        date_format = '%d/%m/%y'
                        data_value = datetime.datetime(*(time.strptime(data_value, date_format))[:6]).date()
                    except ValueError as dpe:
                        try:
                            date_format = '%d %b %Y'
                            data_value = datetime.datetime(*(time.strptime(date_value, date_format))[:6]).date()
                        except ValueError as dpe:
                            date_format = '%Y'
                            data_value = datetime.datetime(*(time.strptime(data_value[:4], date_format))[:6]).date()
                            accuracy = 'year'
#          else:
            #To make sure that the default conversion works
  #              data.typed_data_value

        return data_value, accuracy

    def load_data(self, data_def, input_stream, skip_header, update_only):

        processed = 0

        with input_stream as csvfile:
            data_reader = csv.reader(csvfile, delimiter='\t')

            if skip_header:
                next(data_reader)

            for row in data_reader:
                entity_id = None
                values = {}
                prop_by_column = {}
                processed = processed + 1
                #Ensure columns are processed in order - see also doc_accuracy comment below
                #For more predictable behaviour
                for name, defn in sorted(data_def['values'].items(), key=lambda x: x[1]['column']):
                    identity = False
                    #print(repr(defn))
                    #print(repr(row))
                    data_value = row[defn['column']]
                    if data_value == '\\N':
                        continue
                    #Convert data value - make sure you set data_value
                    try:
                        if 'regex' in defn:
                            re_match = re.search(defn['regex'], data_value)
                            if re_match:
                                #print("Groupdict:" + repr(re_match.groupdict()))
                                try:
                                    data_value = re_match.group(1)
                                except IndexError as iere:
                                        raise InvalidDataValueException("Failed to parse {} using {}"
                                                                        .format(data_value, defn['regex'])) from iere
                                #print("Transformed value is:" + data_value + " from " + row[defn['column']])
                                #print(repr(re_match.groupdict()))
                                #if row[defn['column']] != "" and data_value == "":
                                #    print("Empty match: {} {}".format(defn['regex'], row[defn['column']]))
                            #else:
                            #    print("No match: {} {}".format(defn['regex'], data_value))
                        if defn['type'] == 'datetime':
                            if not (data_value == '' or
                                    data_value == 'NULL' or
                                    data_value == '-' or
                                    data_value == 'None'):
                                try:
                                    data_value, values[name + '_accuracy'] = self.parse_date(defn, data_value)
                                except ValueError as dpe:
                                    self.report("Failed to parse date '{}'".format(data_value),
                                                                                   values)
                                    continue
                            else:
                                #Skip this property
                                continue

                        if 'replace' in defn:
                            for subs in defn['replace']:
                                data_value = re.sub("^" + subs[0] + "$", subs[1], data_value)
                                #print("Transformed value is:" + data_value + " from " + row[defn['column']])

                    except IndexError:
                        self._logger.critical(repr(defn))
                        self._logger.critical(repr(row))
                        raise

                    if defn['type'] == 'string':
                        #Ignore empty values
                        #This can be important e.g. if date is parsed and set doc_accuracy to year
                        #and doc_accuracy accuracy defined column is empty
                        if data_value and data_value.strip():
                            values[name] = data_value.strip()
                        #else:
                        #    print('Ignoring {} {} {}'.format(name, data_value, values))

                    else:
                        values[name] = data_value

                self.process_item(values)


    def add_locations_from_values(self, existing, sampling_event, values):

        if existing and values['study_id'][:4] == '0000':
            values['study_id'] = existing.study_name

        location_name, location = self.process_location(values, '', existing)
        proxy_location_name, proxy_location = self.process_location(values, 'proxy_', existing)

        if location:
            sampling_event.location_id = location.location_id
        if proxy_location:
            sampling_event.proxy_location_id = proxy_location.location_id

        sampling_event.location = location
        sampling_event.proxy_location = proxy_location


    def process_item(self, values):

        if 'study_id' not in values:
            values['study_id'] = '0000-Unknown'

        # Configure OAuth2 access token for authorization: OauthSecurity
        configuration = swagger_client.Configuration()
        configuration.access_token = self._auth_token

        # create an instance of the API class
        api_instance = swagger_client.SamplingEventApi(swagger_client.ApiClient(configuration))

        samp = self.create_sampling_event_from_values(values)

        #print(samp)

        existing = self.lookup_sampling_event(api_instance, samp, values)

        self.add_locations_from_values(existing, samp, values)

        return self.process_sampling_event(values, samp, existing)

    def add_location_identifier(self, looked_up, study_id, partner_name):

        if not looked_up:
            return

        found = False
        if looked_up.identifiers and study_id:
            for ident in looked_up.identifiers:
#                print(ident)
#                print(study_id)
                if ident.study_name[:4] == study_id[:4] and \
                    ident.identifier_value == partner_name:
                    found = True

        if not found:
            #print("adding identifier1 {}".format(looked_up))
            if not looked_up.identifiers:
                looked_up.identifiers = []
            #print("values: {} {}".format(study_id, partner_name))
            if study_id and partner_name:
                # Configure OAuth2 access token for authorization: OauthSecurity
                configuration = swagger_client.Configuration()
                configuration.access_token = self._auth_token

                api_instance = swagger_client.LocationApi(swagger_client.ApiClient(configuration))
#                print("adding identifier {}".format(looked_up.identifiers))
                new_ident = swagger_client.Identifier( identifier_type = 'partner_name', 
                                                      identifier_value = partner_name,
                                                      identifier_source = self._event_set, 
                                                      study_name = study_id)
                #print("adding identifier2 {}".format(new_ident))
                looked_up.identifiers.append(new_ident)
                #print("adding identifier3 {}".format(looked_up))
                try:
                    updated = api_instance.update_location(looked_up.location_id, looked_up)
                except ApiException as err:
                    #print("Error adding location identifier {} {}".format(looked_up, err))
                    message = 'duplicate location\t' + study_id + '\t' + partner_name + '\t' + \
                                str(looked_up.latitude) + '\t' + str(looked_up.longitude)
                    try:
                        conflict = api_instance.download_partner_location(partner_name)
                        if conflict and conflict.locations:
                            conflict_loc = api_instance.download_location(conflict.locations[0].location_id)
                            conflict_loc = api_instance.download_gps_location(str(looked_up.latitude),
                                                                              str(looked_up.longitude))
                            message = message + '\t' + str(conflict_loc.latitude) + '\t' + str(conflict_loc.longitude)
                            message = message + "\nProbable conflict with {}".format(conflict_loc)
                    except ApiException as err:
                        try:
                            conflict_loc = api_instance.download_gps_location(str(looked_up.latitude),
                                                                              str(looked_up.longitude))
                            for cname in conflict_loc.identifiers:
                                if cname.study_name[:4] == study_id[:4]:
                                    message = message + '\t' + cname.identifier_value
                        except ApiException as err:
                            print(err)
                    raise Exception(message)
        #else:
        #    print("identifier exists")

    def update_country(self, country, looked_up):

        ret = looked_up
        #print(country)
        #print(looked_up)
        if country:
            update_country = False
            if looked_up.country:
                if looked_up.country != country:
                    #print("Country confict {} {}".format(country, looked_up))
                    raise Exception("Country conflict not updating {} {}".format(country, looked_up))
            else:
                looked_up.country = country
                update_country = True
            if update_country:
                configuration = swagger_client.Configuration()
                configuration.access_token = self._auth_token

                api_instance = swagger_client.LocationApi(swagger_client.ApiClient(configuration))
                updated = api_instance.update_location(looked_up.location_id, looked_up)
                ret = updated

        return ret

    def create_location_from_values(self, values, prefix):

        if prefix + 'location_name' not in values:
            #print("No {}location name: {}".format(prefix, values))
            return None, None

        partner_name = values[prefix + 'location_name']

        if not partner_name:
            self.report("No location name: ",values)
            return None, None

        #Will have been set to 0000 if not present
        if 'study_id' in values:
            study_id = values['study_id'][:4]

        loc = swagger_client.Location(None)

        loc.identifiers = [
            swagger_client.Identifier(identifier_type='partner_name',
                                      identifier_value=partner_name,
                                      identifier_source=self._event_set, study_name=study_id)
        ]

        try:
            if prefix + 'latitude' in values and values[prefix + 'latitude']:
                loc.latitude = round(float(Decimal(values[prefix + 'latitude'])),7)
            if prefix + 'longitude' in values and values[prefix + 'longitude']:
                loc.longitude = round(float(Decimal(values[prefix + 'longitude'])),7)
        except Exception as excp:
            print(excp)
            pass

        if prefix + 'resolution' in values:
            loc.accuracy = values[prefix + 'resolution']

        if prefix + 'country' in values:
            loc.country = values[prefix + 'country']


        if 'description' in values:
            loc.notes = self._data_file + ' ' + values['description']
        else:
            loc.notes = self._data_file

        #print(values)
        #print(loc)

        return partner_name, loc

    def lookup_location(self, api_instance, loc, study_id, partner_name, values):

        looked_up = None

        try:
            looked_up = api_instance.download_gps_location(str(loc.latitude), str(loc.longitude))
            looked_up = api_instance.download_location(looked_up.location_id)
        except Exception as err:
            #print(repr(err))
            #print("Failed to find location {}".format(loc))
            pass

        if not looked_up:
            try:
                named_locations = api_instance.download_partner_location(partner_name)
                for named_loc in named_locations.locations:
                    for ident in named_loc.identifiers:
                        if ident.study_name[:4] == study_id[:4]:
                            if loc.latitude and loc.longitude:
                                nloc = pformat(named_loc.to_dict(), width=1000, compact=True)
                                self.report("Location name conflict1\t{}\t{}\t{}\t{}\t{}".
                                  format(study_id,partner_name,nloc,
                                        loc.latitude, loc.longitude), values)
                            else:
                                looked_up = named_loc
            except ApiException as err:
                #Can't be found by name either
                pass

        return looked_up

    def process_location(self, values, prefix, existing_event):

        partner_name, loc = self.create_location_from_values(values, prefix)

        if loc is None:
            return None, None

        study_id = None
        if 'study_id' in values:
            study_id = values['study_id'][:4]

        existing_location = None
        if prefix == 'proxy_':
            if existing_event and existing_event.proxy_location:
                existing_location = deepcopy(existing_event.proxy_location)
        else:
            if existing_event and existing_event.location:
                existing_location = deepcopy(existing_event.location)

        if existing_location:
            orig = deepcopy(existing_location)
            orig.location_id = None
            if orig == loc:
                return partner_name, existing_location

        # Configure OAuth2 access token for authorization: OauthSecurity
        configuration = swagger_client.Configuration()
        configuration.access_token = self._auth_token

        api_instance = swagger_client.LocationApi(swagger_client.ApiClient(configuration))

        looked_up = self.lookup_location(api_instance, loc, study_id, partner_name, values)

        ret = None

        if looked_up is not None:
            try:
                #print("Found location {}".format(looked_up))
                loc.location_id = looked_up.location_id
                try:
                    self.add_location_identifier(looked_up, study_id, partner_name)

                    loc.location_id = None
                    try:
                        ret = self.update_country(loc.country, looked_up)
                    except ApiException as err:
                        print(err)
                except Exception as err:
                    #Either a duplicate or country conflict
                    self.report(err, values)

            except Exception as err:
                print(repr(err))
                #print("Failed to find location {}".format(loc))
        else:

            try:
                created = api_instance.create_location(loc)
                ret = created
            #    print("Created location {}".format(created))
            except ApiException as err:
                if err.status == 422:
                    idents = '\t'.join(pformat(x.to_dict(), width=1000, compact=True) for x in
                              loc.identifiers)
                    self.report("Location name conflict2\t{}\t{}\t{}\t{}\t{}".
                      format(study_id,partner_name,idents, loc.latitude, loc.longitude), values)
                else:
                    self.report("Error creating location {} {}".format(loc, err), values)
                return None, None

        return partner_name, ret

    def create_sampling_event_from_values(self, values):

        doc = None
        doc_accuracy = None
        study_id = None
        ret = None

        if 'doc' in values:
            if isinstance(values['doc'], datetime.date):
                doc = values['doc']
        else:
            if 'year' in values:
                if isinstance(values['year'], datetime.date):
                    doc = values['year']
                    values['doc_accuracy'] = 'year'

        if 'doc_accuracy' in values:
            doc_accuracy = values['doc_accuracy']

        if 'study_id' in values:
            study_id = values['study_id']

        samp = swagger_client.SamplingEvent(None, study_name = study_id, doc = doc)


        if 'species' in values and values['species'] and len(values['species']) > 0:
            samp.partner_species = values['species']

        if doc_accuracy:
            samp.doc_accuracy = doc_accuracy

        idents = []
        if 'sample_roma_id' in values:
            idents.append(swagger_client.Identifier ('roma_id', values['sample_roma_id'],
                                                     self._event_set))
        if 'sample_partner_id' in values and values['sample_partner_id']:
            idents.append(swagger_client.Identifier ('partner_id', values['sample_partner_id'],
                                                     self._event_set))
        if 'sample_partner_id_1' in values and values['sample_partner_id_1']:
            idents.append(swagger_client.Identifier ('partner_id', values['sample_partner_id_1'],
                                                     self._event_set))
        if 'sample_oxford_id' in values and values['sample_oxford_id']:
            idents.append(swagger_client.Identifier ('oxford_id', values['sample_oxford_id'],
                                                     self._event_set))
        if 'sample_lims_id' in values and values['sample_lims_id']:
            idents.append(swagger_client.Identifier ('sanger_lims_id', values['sample_lims_id'],
                                                     self._event_set))
        if 'sample_alternate_oxford_id' in values and len(values['sample_alternate_oxford_id']) > 0:
            idents.append(swagger_client.Identifier ('alt_oxford_id',
                                                     values['sample_alternate_oxford_id'],
                                                     self._event_set))
        if 'sample_source_id' in values and values['sample_source_id'] and values['sample_source_type']:
            idents.append(swagger_client.Identifier (values['sample_source_type'],
                                                     values['sample_source_id'],
                                                     self._event_set))
        if 'sample_source_id1' in values and values['sample_source_id1'] and values['sample_source_type1']:
            idents.append(swagger_client.Identifier (values['sample_source_type1'],
                                                     values['sample_source_id1'],
                                                     self._event_set))
        if 'sample_source_id2' in values and values['sample_source_id2'] and values['sample_source_type2']:
            idents.append(swagger_client.Identifier (values['sample_source_type2'],
                                                     values['sample_source_id2'],
                                                     self._event_set))

        samp.identifiers = idents

        #print(values)
        #print(samp)
        return samp

    def merge_events(self, api_instance, existing, found, values):

        es_api_instance = None

        configuration = swagger_client.Configuration()
        configuration.access_token = self._auth_token

        es_api_instance = swagger_client.EventSetApi(swagger_client.ApiClient(configuration))

        existing, changed = self.merge_sampling_event_objects(es_api_instance, existing, found,
                                                              values)
        ret = existing

        if changed:

            for event_set in found.event_sets:
                try:
                    es_api_instance.create_event_set_item(event_set, existing.sampling_event_id)
                except ApiException as err:
                    #Probably because it already exists
                    self._logger.debug("Error adding sample {} to event set {} {}".format(existing.sampling_event_id, self._event_set, err))

            api_instance.delete_sampling_event(found.sampling_event_id)

            #print("Updating {} to {}".format(orig, existing))
            existing = api_instance.update_sampling_event(existing.sampling_event_id, existing)
        else:
            self.report("Merge didn't change anything {} {}".format(existing, found), None)

        return existing

    def lookup_sampling_event(self, api_instance, samp, values):

        existing = None

        if 'unique_id' in values:
            if values['unique_id'] in self._sample_cache:
                existing_sample_id = self._sample_cache[values['unique_id']]
                existing = api_instance.download_sampling_event(existing_sample_id)
                return existing

        #print ("not in cache: {}".format(samp))
        if len(samp.identifiers) > 0:
            #print("Checking identifiers {}".format(samp.identifiers))
            for ident in samp.identifiers:
                try:
                    #print("Looking for {} {}".format(ident.identifier_type, ident.identifier_value))

                    found_events = api_instance.download_sampling_events_by_identifier(ident.identifier_type,
                                                           urllib.parse.quote_plus(ident.identifier_value))

                    for found in found_events.sampling_events:
                        if ident.identifier_type == 'partner_id':
                            #Partner ids within 1087 are not unique
                            if samp.study_name[:4] == '1087':
                                continue
                            if 'sample_lims_id' in values and values['sample_lims_id']:
                                #Partner id is not the only id
                                if len(samp.identifiers) > 2:
                                    continue
                                #Probably still not safe even though at this point it's a unique partner_id
                                continue
                            else:
                                #Not safe as partner id's can be the same across studies
                                #unless check study id as well
                                #print('Checking study ids {} {} {}'.format(samp.study_name,
                                #                                           found.study_name, ident))
                                if samp.study_name:
                                    if samp.study_name[:4] == '0000':
                                        continue
                                    if found.study_name[:4] != samp.study_name[:4]:
                                        continue
                                else:
                                    continue


                        #Only here if found - otherwise 404 exception
                        if existing and existing.sampling_event_id != found.sampling_event_id:
                            #self.report("Merging into {} using {}"
                            #                .format(existing.sampling_event_id,
                            #                                   ident.identifier_type), values)
                            found = self.merge_events(api_instance, existing, found, values)
                        existing = found
                        break
                        #print ("found: {} {}".format(samp, found))
                except ApiException as err:
                    #self._logger.debug("Error looking for {}".format(ident))
                    #print("Not found")
                        pass

        #if not existing:
        #    print('Not found {}'.format(samp))
        return existing

    def set_additional_event(self, es_api_instance, sampling_event_id, study_id):

        if study_id[:4] == '0000' or study_id[:4] == '1089':
            return

        event_set_id = 'Additional events: {}'.format(study_id)

        try:
            # creates an eventSet
            api_response = es_api_instance.create_event_set(event_set_id)
        except ApiException as e:
            if e.status != 422: #Already exists
                print("Exception when calling EventSetApi->create_event_set: %s\n" % e)

        try:
            es_api_instance.create_event_set_item(event_set_id, sampling_event_id)
        except ApiException as err:
            #Probably because it already exists
            self._logger.debug("Error adding sample {} to event set {} {}".format(sampling_event_id, event_set_id, err))


    def merge_sampling_event_objects(self, es_api_instance, existing, samp, values):

        orig = deepcopy(existing)
        new_ident_value = False

        for new_ident in samp.identifiers:
            found = False
            for existing_ident in existing.identifiers:
                if existing_ident == new_ident:
                    found = True
            if not found:
                new_ident_value = True
                #print("Adding {} to {}".format(new_ident, existing))
                existing.identifiers.append(new_ident)

#        print("existing {} {}".format(existing, study_id))
        if samp.study_name:
            if existing.study_name:
                if samp.study_name != existing.study_name:
                    if samp.study_name[:4] == existing.study_name[:4]:
                        #print("#Short and full study ids used {} {} {}".format(values, study_id, existing.study_name))
                        pass
                    else:
                        if not (existing.study_name[:4] == '0000' or samp.study_name[:4] == '0000'):
                            self.report("Conflicting study_id value {} {}"
                                            .format(samp.study_name, existing.study_name), values)

                        if not samp.study_name[:4] == '0000':
                            if ((int(samp.study_name[:4]) < int(existing.study_name[:4]) or
                                 existing.study_name[:4] == '0000') and
                                (samp.study_name[:4] != '1089')):
                                self.set_additional_event(es_api_instance,
                                                          existing.sampling_event_id,
                                                          existing.study_name)
                                existing.study_name = samp.study_name
                                new_ident_value = True
                            else:
                                if not (samp.study_name[:4] == '0000' or samp.study_name[:4] == '1089'):
                                    self.set_additional_event(es_api_instance,
                                                          existing.sampling_event_id,
                                                              samp.study_name)
            else:
                existing.study_name = samp.study_name
                new_ident_value = True
        else:
            if existing.study_name:
#                    print("Adding loc ident {} {}".format(location_name, existing.study_name))
                try:
                    self.add_location_identifier(location, existing.study_name, location_name)
                except Exception as err:
                    #Almost certainly a duplicate
                    self.report(err, values)
                try:
                    self.add_location_identifier(proxy_location, existing.study_name,
                                             proxy_location_name)
                except Exception as err:
                    #Almost certainly a duplicate
                    self.report(err, values)

        if samp.doc:
            if existing.doc:
                if samp.doc != existing.doc:
                    update_doc = True
                    if samp.doc_accuracy and samp.doc_accuracy == 'year':
                        if not existing.doc_accuracy:
                            update_doc = False
                        if existing.doc_accuracy and existing.doc_accuracy != 'year':
                            update_doc = False

                    if update_doc:
                        self.report("Conflicting doc value updated {} {}"
                                        .format(samp.doc, existing.doc), values)
                        existing.doc = samp.doc
                        if samp.doc_accuracy:
                            existing.doc_accuracy = samp.doc_accuracy
                        else:
                            if existing.doc_accuracy:
                                existing.doc_accuracy = 'day'

                        new_ident_value = True
                    else:
                        self.report("Conflicting doc value not updated {} {}"
                                        .format(samp.doc, existing.doc), values)
            else:
                existing.doc = samp.doc
                new_ident_value = True

        if samp.location:
            if existing.location:
                if samp.location.location_id != existing.location_id:
                    location = samp.location
                    self.report("Conflicting location value updated {}\t{}\t{}\t{}\t{}\t{}".format(
                                                                       samp.location.identifiers[0].identifier_value,
                                                                                         samp.location.latitude,
                                                                                         samp.location.longitude,
                                                                       existing.location.identifiers[0].identifier_value,
                                                                                         existing.location.latitude,
                                                                                         existing.location.longitude)
                                    ,values)
                    #existing.location_id = location.location_id
                    #new_ident_value = True
            else:
                existing.location_id = samp.location.location_id
                new_ident_value = True

        if samp.proxy_location:
            if existing.proxy_location:
                if samp.proxy_location.location_id != existing.proxy_location_id:
                    proxy_location = samp.proxy_location
                    self.report("Conflicting proxy location value updated {}\t{}"
                                .format(pformat(proxy_location.to_dict(), width=1000, compact=True),
                                               pformat(existing.proxy_location.to_dict(), width=1000, compact=True)),
                               values)
                    existing.proxy_location_id = proxy_location.location_id
                    new_ident_value = True
            else:
                existing.proxy_location_id = samp.proxy_location.location_id
                new_ident_value = True

        if samp.partner_species:
            if existing.partner_species:
                if existing.partner_species != samp.partner_species:
                    fuzzyMatch = False
                    if existing.partner_species == 'Plasmodium falciparum/vivax mixture':
                        if samp.partner_species == 'Plasmodium vivax':
                            fuzzyMatch = True
                        if samp.partner_species == 'Plasmodium falciparum':
                            fuzzyMatch = True

                    if existing.partner_species == 'Plasmodium falciparum':
                        if samp.partner_species == 'P. falciparum':
                            fuzzyMatch = True

                    if not fuzzyMatch:
                        self.report("Conflicting partner_species value not updated record {}\t{}".format(
                                                                           samp.partner_species,
                                                                           existing.partner_species),
                                        values)

            else:
                existing.partner_species = samp.partner_species
                new_ident_value = True

        return existing, new_ident_value

    def process_sampling_event(self, values, samp, existing):

        #print('process_sampling event {} {} {} {} {}'.format(values, location_name, location, proxy_location_name, proxy_location))

        # Configure OAuth2 access token for authorization: OauthSecurity
        configuration = swagger_client.Configuration()
        configuration.access_token = self._auth_token

        # create an instance of the API class
        api_instance = swagger_client.SamplingEventApi(swagger_client.ApiClient(configuration))

        es_api_instance = swagger_client.EventSetApi(swagger_client.ApiClient(configuration))

        if 'sample_lims_id' in values and values['sample_lims_id']:
            if not existing:
                self.report("Could not find not adding ", values)
                return None

        if existing:

            #print("existing pre merge")
            #print(existing)
            existing, changed = self.merge_sampling_event_objects(es_api_instance, existing, samp,
                                                                 values)
            #print("existing post merge")
            #print(existing)
            ret = existing

            if changed:
                #print("Updating {} to {}".format(orig, existing))
                ret = api_instance.update_sampling_event(existing.sampling_event_id, existing)

            try:
                es_api_instance.create_event_set_item(self._event_set, existing.sampling_event_id)
            except ApiException as err:
                #Probably because it already exists
                self._logger.debug("Error adding sample {} to event set {} {}".format(existing.sampling_event_id, self._event_set, err))

        else:
            #print("Creating {}".format(samp))
            if len(samp.identifiers) == 0:
                return None

            try:
                created = api_instance.create_sampling_event(samp)

                ret = created

                try:
                    es_api_instance.create_event_set_item(self._event_set, created.sampling_event_id)
                except ApiException as err:
                    #Probably because it already exists
                    self._logger.debug("Error adding sample {} to event set {} {}".format(created.sampling_event_id, self._event_set, err))

            except ApiException as err:
                print("Error adding sample {} {}".format(samp, err))
                self._logger.error("Error inserting {}".format(samp))
                sys.exit(1)

            if 'unique_id' in values:
                self._sample_cache[values['unique_id']] = created.sampling_event_id

        return ret

if __name__ == '__main__':
    sd = Uploader(sys.argv[3])
    with open(sys.argv[2]) as json_file:
        json_data = json.load(json_file)
        sd.load_data_file(json_data, sys.argv[1])

    #print(repr(sd.fetch_entity_by_source('test',1)))
