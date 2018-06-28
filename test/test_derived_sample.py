import swagger_client
from swagger_client.rest import ApiException

from test_base import TestBase
from datetime import date
import urllib

import uuid
import pytest

class TestDerivedSample(TestBase):


    """
    """
    def test_ds_create(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:

            samp = swagger_client.DerivedSample(None)
            created = api_instance.create_derived_sample(samp)
            if not api_factory.is_authorized(None):
                pytest.fail('Unauthorized call to create_derived_sample succeeded')

            fetched = api_instance.download_derived_sample(created.derived_sample_id)
            assert created == fetched, "create response != download response"
            fetched.derived_sample_id = None
            assert samp == fetched, "upload != download response"
            api_instance.delete_derived_sample(created.derived_sample_id)

        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->create_derived_sample", error)

    """
    """
    def test_ds_delete(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:

            samp = swagger_client.DerivedSample(None)
            created = api_instance.create_derived_sample(samp)
            api_instance.delete_derived_sample(created.derived_sample_id)
            with pytest.raises(ApiException, status=404):
                fetched = api_instance.download_derived_sample(created.derived_sample_id)

        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->create_derived_sample", error)


    """
    """
    def test_ds_delete_missing(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:

            if api_factory.is_authorized(None):
                with pytest.raises(ApiException, status=404):
                    api_instance.delete_derived_sample(str(uuid.uuid4()))
            else:
                with pytest.raises(ApiException, status=403):
                    api_instance.delete_derived_sample(str(uuid.uuid4()))

        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->delete_derived_sample", error)

    """
    """
    def test_ds_duplicate_key(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:

            samp = swagger_client.DerivedSample(None)
            samp.attrs = [
                swagger_client.Attr (attr_type='oxford', attr_value='1234',
                                           attr_source='same')
            ]
            created = api_instance.create_derived_sample(samp)

            with pytest.raises(ApiException, status=422):
                created = api_instance.create_derived_sample(samp)

            api_instance.delete_derived_sample(created.derived_sample_id)

        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->create_derived_sample", error)


    """
    """
    def test_ds_attr_lookup(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:

            samp = swagger_client.DerivedSample(None)
            samp.attrs = [
                swagger_client.Attr (attr_type='oxford', attr_value='123456')
            ]
            created = api_instance.create_derived_sample(samp)
            results = api_instance.download_derived_samples_by_attr('oxford', '123456')
            looked_up = results.derived_samples[0]

            fetched = api_instance.download_derived_sample(looked_up.derived_sample_id)

            assert created == fetched, "create response != download response"

            fetched.derived_sample_id = None
            assert samp == fetched, "upload != download response"

            api_instance.delete_derived_sample(created.derived_sample_id)

        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->create_derived_sample", error)

    """
    """
    def test_ds_attr_merge(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:

            ident1 = swagger_client.Attr(attr_type='oxford_id', attr_value='1234')
            ident2 = swagger_client.Attr(attr_type='roma_id', attr_value='12345')
            ident3 = swagger_client.Attr(attr_type='lims_id', attr_value='123456')
            samp1 = swagger_client.DerivedSample(None)
            samp1.attrs = [
                ident1
            ]
            created1 = api_instance.create_derived_sample(samp1)

            samp2 = swagger_client.DerivedSample(None)
            samp2.attrs = [
                ident2
            ]
            created2 = api_instance.create_derived_sample(samp2)


            samp3 = swagger_client.DerivedSample(None)
            samp3.attrs = [
                ident1,
                ident2,
                ident3
            ]
            with pytest.raises(ApiException, status=422):
                created3 = api_instance.create_derived_sample(samp3)

            api_instance.delete_derived_sample(created1.derived_sample_id)
            api_instance.delete_derived_sample(created2.derived_sample_id)


        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->create_derived_sample", error)

    """
    """
    def test_ds_update(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:

            samp = swagger_client.DerivedSample(None)
            samp.attrs = [
                swagger_client.Attr (attr_type='oxford', attr_value='1234567')
            ]
            created = api_instance.create_derived_sample(samp)
            looked_up = api_instance.download_derived_samples_by_attr('oxford', '1234567')
            looked_up = looked_up.derived_samples[0]
            new_samp = swagger_client.DerivedSample(None)
            updated = api_instance.update_derived_sample(looked_up.derived_sample_id, new_samp)
            fetched = api_instance.download_derived_sample(looked_up.derived_sample_id)
            assert updated == fetched, "update response != download response"
            fetched.derived_sample_id = None
            assert new_samp == fetched, "update != download response"
            api_instance.delete_derived_sample(looked_up.derived_sample_id)

        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->create_derived_sample", error)

    """
    """
    def test_ds_update_duplicate(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:

            samp = swagger_client.DerivedSample(None)
            samp.attrs = [
                swagger_client.Attr (attr_type='oxford', attr_value='12345678',
                                           attr_source='upd')
            ]
            created = api_instance.create_derived_sample(samp)
            looked_up = api_instance.download_derived_samples_by_attr('oxford', '12345678')
            looked_up = looked_up.derived_samples[0]
            new_samp = swagger_client.DerivedSample(None)
            new_samp.attrs = [
                swagger_client.Attr (attr_type='oxford', attr_value='123456789',
                                          attr_source='upd')
            ]
            new_created = api_instance.create_derived_sample(new_samp)
            with pytest.raises(ApiException, status=422):
                updated = api_instance.update_derived_sample(looked_up.derived_sample_id, new_samp)

            api_instance.delete_derived_sample(looked_up.derived_sample_id)
            api_instance.delete_derived_sample(new_created.derived_sample_id)

        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->create_derived_sample", error)

    """
    """
    def test_ds_update_missing(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:

            new_samp = swagger_client.DerivedSample(None)
            fake_id = uuid.uuid4()
            new_samp.derived_sample_id = str(fake_id)


            if api_factory.is_authorized(None):
                with pytest.raises(ApiException, status=404):
                    updated = api_instance.update_derived_sample(new_samp.derived_sample_id, new_samp)
            else:
                with pytest.raises(ApiException, status=403):
                    updated = api_instance.update_derived_sample(new_samp.derived_sample_id, new_samp)

        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->update_derived_sample", error)

    """
    """
    def test_ds_attr_lookup_encode(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:

            test_id = 'MDG/DK_0005'
            samp = swagger_client.DerivedSample(None)
            samp.attrs = [
                swagger_client.Attr (attr_type='partner_id', attr_value=test_id,
                                          attr_source='encode')
            ]
            created = api_instance.create_derived_sample(samp)

            fetched = api_instance.download_derived_sample(created.derived_sample_id)

            assert created == fetched, "create response != download response"
            fetched.derived_sample_id = None
            assert samp == fetched, "upload != download response"

            results = api_instance.download_derived_samples_by_attr('partner_id',
                                                                      urllib.parse.quote_plus(test_id))
            looked_up = results.derived_samples[0]
            fetched = api_instance.download_derived_sample(looked_up.derived_sample_id)

            assert created == fetched, "create response != download response"
            fetched.derived_sample_id = None
            assert samp == fetched, "upload != download response"

            api_instance.delete_derived_sample(created.derived_sample_id)

        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->create_derived_sample", error)




    """
    """
    def test_ds_download_derived_sample_permission(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:
            if not api_factory.is_authorized(None):
                with pytest.raises(ApiException, status=403):
                    api_instance.download_derived_sample(str(uuid.uuid4()))
        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->download_derived_sample", error)

    """
    """
    def test_ds_download_derived_sample_by_attr_permission(self, api_factory):

        api_instance = api_factory.DerivedSampleApi()

        try:
            if not api_factory.is_authorized(None):
                with pytest.raises(ApiException, status=403):
                    api_instance.download_derived_samples_by_attr('partner_id','404')
        except ApiException as error:
            self.check_api_exception(api_factory, "DerivedSampleApi->download_derived_samples_by_attr", error)

