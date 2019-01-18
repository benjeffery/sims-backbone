from test_base import TestBase


import json

from uploader import Uploader

import swagger_client
from swagger_client.rest import ApiException

class TestSampling_Event(TestBase):

    _locations = []

    """
    """
    @classmethod
    def setUpClass(self):

        super(TestSampling_Event, self).setUpClass()
        sd = Uploader(self._config_file)
        sd.use_message_buffer = True

        json_data = json.loads('''{
            "values": {
                "sample_oxford_id": {
                    "column": 0,
                    "type": "string"
                },
                "study_id": {
                    "column": 1,
                    "type": "string"
                },
                "latitude": {
                    "column": 2,
                    "type": "string"
                },
                "longitude": {
                    "column": 3,
                    "type": "string"
                },
                "location_name": {
                    "column": 4,
                    "type": "string"
                }
            }
        }''')
        sd.load_data_file(json_data, 'multiple_study.tsv')

        self._messages = sd.message_buffer

    """
    """
    @classmethod
    def tearDownClass(self):

        looked_up = TestBase.getDAO().download_sampling_events_by_os_attr('oxford_id', '123456')
        looked_up = looked_up.sampling_events[0]

        TestBase.getDAO().delete_sampling_event(looked_up.sampling_event_id)

        looked_up = TestBase.getDAO().download_original_samples_by_attr('oxford_id', '123456')
        looked_up = looked_up.original_samples[0]

        TestBase.getDAO().delete_original_sample(looked_up.original_sample_id)

        TestBase.deleteEventSets(['multiple_study'], TestSampling_Event._locations)

        TestBase.tearDownLocations(TestSampling_Event._locations)

    """
    """
    def test_multiple_study(self):



        looked_up = self._dao.download_sampling_events_by_os_attr('oxford_id', '123456')
        looked_up = looked_up.sampling_events[0]

        for study in ["9011 Upload test study", "9012 Upload test study 3"]:
            eset = "Additional events: {}".format(study)
            fetched_set = self._dao.download_event_set(eset)
            found = False
            for member in fetched_set.members.sampling_events:
                if member.sampling_event_id == looked_up.sampling_event_id:
                    found = True
            self.assertTrue(found, "Not added to additional events")
            self._dao.delete_event_set(eset)

        self.assertEqual(looked_up.study_name, '9010 Upload test study 2', 'Not lowest study code')

        for study in ["0000-Unknown", "1089 R&D special study"]:
            eset = "Additional events: {}".format(study)
            with self.assertRaises(Exception) as context:
                self._dao.delete_event_set(eset)

            self.assertEqual(context.exception.status, 404)

        messages = [
            "Conflicting Study value\t\t{}\t9011 Upload test study\t9011 Upload test study\t9010 Upload test study 2\t[('sample_oxford_id', '123456'), ('study_id', '9010 Upload test study 2')]",
            "Conflicting Study value\t\t{}\t9010 Upload test study 2\t9010 Upload test study 2\t9012 Upload test study 3\t[('sample_oxford_id', '123456'), ('study_id', '9012 Upload test study 3')]",
            "Conflicting Study value\t\t{}\t9010 Upload test study 2\t9010 Upload test study 2\t1089 R&D special study\t[('sample_oxford_id', '123456'), ('study_id', '1089 R&D special study')]"
            ]
        for msg in messages:
            msg = msg.format(looked_up.sampling_event_id)
            self.assertIn(msg, self._messages)

    """
    """
    def test_location_name_changed_study(self):


        looked_up = self._dao.download_sampling_events_by_os_attr('oxford_id', '123456')

        if looked_up.sampling_events[0].location_id not in TestSampling_Event._locations:
            TestSampling_Event._locations.append(looked_up.sampling_events[0].location_id)

        assert len(looked_up.sampling_events[0].location.attrs) == 1, 'Too many location attrs {}'.format(looked_up)
        assert looked_up.sampling_events[0].location.attrs[0].study_name == '9010 Upload test study 2', 'Study name in location not updated'

