from __future__ import print_function
import sys

import openapi_client
from openapi_client.rest import ApiException
import uploader
import json
import datetime
import time

class Upload_ROMA(uploader.Uploader):

    def load_data_file(self, filename):

        self.setup(filename)

        (instance,dumps,) = self._event_set.split('_')

        with open(filename) as json_file:
            data = json.load(json_file)

        items = {}
        event_sets = []

        for item in data:
            if not item['model'] in items:
                items[item['model']] = {}
            items[item['model']][item['pk']] = item

        proxy_locations = {}

        if 'locations.proxylocation' in items:
            for key, item in items['locations.proxylocation'].items():
                fields = item['fields']
                proxy_locations[fields['location']] = fields['proxy_location']


        for key, item in items['samples.sample'].items():
            roma_pk_id = instance + '_' + str(item['pk'])
            fields = item['fields']
            roma_id = fields['sample_name']
            source_code = fields['external_id'].strip()
            #source_code = None
            date_format = '%Y-%m-%d'
            doc = datetime.datetime(*(time.strptime(fields['collection_date'], date_format))[:6]).date()

            loc = items['locations.location'][fields['location']]
            src_location_id = instance + '_loc_' + str(loc['pk'])
            latitude = loc['fields']['latitude']
            longitude = loc['fields']['longitude']
            loc_name = loc['fields']['location_name']
            country = items['locations.country'][loc['fields']['country']]['fields']['iso3']

            proxy_latitude = None
            proxy_longitude = None
            proxy_loc_name = None
            proxy_country = None
            proxy_src_location_id = None

            if fields['location'] in proxy_locations:
                proxy_loc = items['locations.location'][proxy_locations[fields['location']]]
                proxy_src_location_id = instance + '_loc_' + str(proxy_loc['pk'])
                proxy_latitude = proxy_loc['fields']['latitude']
                proxy_longitude = proxy_loc['fields']['longitude']
                proxy_loc_name = proxy_loc['fields']['location_name']
                proxy_country = items['locations.country'][proxy_loc['fields']['country']]['fields']['iso3']

            roma_manifest_id = fields['manifest']
            roma_study_id = items['samples.manifest'][roma_manifest_id]['fields']['study']
            manifest = instance + '_' + items['samples.manifest'][roma_manifest_id]['fields']['name']
            study_id = items['managements.study'][roma_study_id]['fields']['project_code'][1:]

            tags = {}
            if 'tags' in fields and fields['tags']:
                if isinstance(fields['tags'], str):
                    tags = json.loads(fields['tags'])
                else:
                    tags = fields['tags']

            oxford_code = None
            taxon = None
            patient_id = None
            if '27. original_oxford_code' in tags:
                oxford_code = tags['27. original_oxford_code'].strip()
                pass
            if 'Patient Id' in tags:
                patient_id = tags['Patient Id']
            elif '24. Patient Id' in tags:
                patient_id = tags['24. Patient Id']

            if 'Species' in tags:
                taxon = tags['Species'].strip()
            else:
                if filename.startswith('spot'):
                    taxon = 'P. falciparum'
                elif filename.startswith('vobs'):
                    taxon = 'Anopheles'
                elif filename.startswith('vivax'):
                    taxon = 'Plasmodium'

            values = {
                'study_id': study_id.strip(),
                'sample_roma_id': roma_id.strip(),
                'roma_pk_id': roma_pk_id,
                'sample_oxford_id': oxford_code,
                'sample_partner_id': source_code,
                'patient_id': patient_id,
                'species': taxon,
                'doc': doc,
                'src_location_id': src_location_id,
                'proxy_src_location_id': proxy_src_location_id,
                'location_name': loc_name.strip(),
                'country': country.strip(),
                'latitude': latitude,
                'longitude': longitude,
                'proxy_latitude': proxy_latitude,
                'proxy_longitude': proxy_longitude,
                'proxy_location_name': proxy_loc_name,
                'proxy_country': proxy_country,
                'manifest': manifest
            }

            sampling_event = self.process_item(values)

            if values['manifest'] not in event_sets:
                self._dao.create_event_set(values['manifest'])
                event_sets.append(values['manifest'])

            if sampling_event:
                if not sampling_event.event_sets or values['manifest'] not in sampling_event.event_sets:
                    self._dao.create_event_set_item(values['manifest'],
                                                    sampling_event.sampling_event_id)
            #print(values)
            #print(sampling_event)

            self.validate(values, sampling_event)


    def validate(self, input_values, output_values):

        if not output_values:
            #Item wasn't processed but should be messages elsewhere
            return

        if 'study_id' not in input_values:
            print("No study id {} {}".format(input_values, output_values))

if __name__ == '__main__':
    el = Upload_ROMA(sys.argv[1])
    el.load_data_file(sys.argv[2])
