import copy
import json

from tests.conftest import GlobalClassMetadata
from tests.utils.ReleaseModel.tenderPeriodEndNoAuction.tender_period_end_no_auction_release_library import \
    ReleaseLibrary
from tests.utils.functions import is_it_uuid, get_value_from_country_csv
from tests.utils.services.e_mdm_service import MdmService


class TenderPeriodExpectedChanges:
    def __init__(self, environment, language):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.metadata_budget_url = None
        self.metadata_tender_url = None
        self.metadata_document_url = None
        self.metadata_auction_url = None
        self.mdm = MdmService(host=GlobalClassMetadata.host_for_services)

        try:
            if environment == "dev":
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"
                self.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
                self.metadata_auction_url = "http://auction.eprocurement.systems/auctions/"

            elif environment == "sandbox":
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://public.eprocurement.systems/tenders"
                self.metadata_document_url = "http://storage.eprocurement.systems/get"
                self.metadata_auction_url = "https://eauction.eprocurement.systems/auctions/"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")
        GlobalClassMetadata.metadata_budget_url = self.metadata_budget_url
        GlobalClassMetadata.metadata_tender_url = self.metadata_tender_url

    def prepare_parties_array(self, payload_tenderers_array, release_parties_array):
        expected_parties_array = []
        try:
            """
            Check how many quantity of object into payload_bid_tenderers_array.
            """
            list_of_payload_tenderer_id = list()
            for tenderer_object in payload_tenderers_array:
                for i in tenderer_object['identifier']:
                    if i == "id":
                        list_of_payload_tenderer_id.append(i)
            quantity_of_tender_object_into_payload = len(list_of_payload_tenderer_id)
        except KeyError:
            raise KeyError("Check payload_tenderers_array['identifier']['id']")

        try:
            """
            Check how many quantity of object into release_parties_array.
            """
            list_of_release_party_id = list()
            for party_object in release_parties_array:
                for i in party_object:
                    if i == "id":
                        list_of_release_party_id.append(i)
            quantity_of_party_object_into_release = len(list_of_release_party_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['parties'][*]['id']")

        try:
            """
            Prepare parties array framework.
            """
            quantity_one = quantity_of_party_object_into_release
            quantity_tenderers = quantity_of_party_object_into_release
            while quantity_one > 0:
                party_object = {}
                party_object.update(self.constructor.ev_release_parties_object())

                expected_parties_array.append(party_object)
                quantity_one -= 1
        except ValueError:
            raise ValueError("Impossible to build expected parties array framework.")

        try:
            """
            Enrich parties array framework by value from payload and MDM.
            """
            quantity_tenderers -= 1
            while quantity_tenderers >= 0:
                tenderer_country_data = self.mdm.get_country(
                    country=payload_tenderers_array[quantity_tenderers]['address']['addressDetails']['country']['id'],
                    language=self.language
                )

                tenderer_country_object = {
                    "scheme": tenderer_country_data['data']['scheme'],
                    "id": tenderer_country_data['data']['id'],
                    "description": tenderer_country_data['data']['description'],
                    "uri": tenderer_country_data['data']['uri']
                }

                tenderer_region_data = self.mdm.get_region(
                    country=payload_tenderers_array[quantity_tenderers]['address']['addressDetails']['country']['id'],
                    region=payload_tenderers_array[quantity_tenderers]['address']['addressDetails']['region']['id'],
                    language=self.language
                )
                tenderer_region_object = {
                    "scheme": tenderer_region_data['data']['scheme'],
                    "id": tenderer_region_data['data']['id'],
                    "description": tenderer_region_data['data']['description'],
                    "uri": tenderer_region_data['data']['uri']
                }

                if payload_tenderers_array[quantity_tenderers]['address']['addressDetails']['locality']['scheme'] == \
                        "CUATM":
                    tenderer_locality_data = self.mdm.get_locality(
                        country=payload_tenderers_array[quantity_tenderers]['address']['addressDetails']['country'][
                            'id'],
                        region=payload_tenderers_array[quantity_tenderers]['address']['addressDetails']['region']['id'],
                        locality=payload_tenderers_array[quantity_tenderers]['address']['addressDetails']['locality'][
                            'id'],
                        language=self.language
                    )

                    tenderer_locality_object = {
                        "scheme": tenderer_locality_data['data']['scheme'],
                        "id": tenderer_locality_data['data']['id'],
                        "description": tenderer_locality_data['data']['description'],
                        "uri": tenderer_locality_data['data']['uri']
                    }
                else:
                    tenderer_locality_object = {
                        "scheme": payload_tenderers_array[quantity_tenderers]['address']['addressDetails']['locality'][
                            'scheme'],
                        "id": payload_tenderers_array[quantity_tenderers]['address']['addressDetails']['locality'][
                            'id'],
                        "description": payload_tenderers_array[quantity_tenderers]['address']['addressDetails'][
                            'locality']['description']
                    }

                expected_parties_array[quantity_tenderers]['additionalIdentifiers'] = \
                    payload_tenderers_array[quantity_tenderers]['additionalIdentifiers']
                expected_parties_array[quantity_tenderers]['id'] = \
                    f"{payload_tenderers_array[quantity_tenderers]['identifier']['scheme']}-" \
                    f"{payload_tenderers_array[quantity_tenderers]['identifier']['id']}"
                expected_parties_array[quantity_tenderers]['name'] = \
                    payload_tenderers_array[quantity_tenderers]['name']
                expected_parties_array[quantity_tenderers]['identifier'] = \
                    payload_tenderers_array[quantity_tenderers]['identifier']
                expected_parties_array[quantity_tenderers]['address']['streetAddress'] = \
                    payload_tenderers_array[quantity_tenderers]['address']['streetAddress']
                expected_parties_array[quantity_tenderers]['address']['postalCode'] = \
                    payload_tenderers_array[quantity_tenderers]['address']['postalCode']
                expected_parties_array[quantity_tenderers]['address']['addressDetails']['country'] = \
                    tenderer_country_object
                expected_parties_array[quantity_tenderers]['address']['addressDetails']['region'] = \
                    tenderer_region_object
                expected_parties_array[quantity_tenderers]['address']['addressDetails']['locality'] = \
                    tenderer_locality_object
                expected_parties_array[quantity_tenderers]['contactPoint'] = \
                    payload_tenderers_array[quantity_tenderers]['contactPoint']
                expected_parties_array[quantity_tenderers]['details'] = \
                    payload_tenderers_array[quantity_tenderers]['details']

                try:
                    """
                    Check how many quantity of object into payload_bid_tenderers_array[´details']['bankAccounts'].
                    """
                    list_of_payload_tenderer_details_bank_accounts_name = list()

                    for i in payload_tenderers_array[quantity_tenderers]['details']['bankAccounts']:
                        for i_1 in i:
                            if i_1 == "bankName":
                                list_of_payload_tenderer_details_bank_accounts_name.append(i_1)
                    quantity_of_tender_details_bank_accounts_objects_into_payload = \
                        len(list_of_payload_tenderer_details_bank_accounts_name)
                except KeyError:
                    raise KeyError("Check payload_tenderers_array[´details']['bankAccounts']['bankName']")

                quantity_of_tender_details_bank_accounts_objects_into_payload -= 1
                while quantity_of_tender_details_bank_accounts_objects_into_payload >= 0:
                    bank_country_data = self.mdm.get_country(
                        country=payload_tenderers_array[quantity_tenderers]['details']['bankAccounts'][
                            quantity_of_tender_details_bank_accounts_objects_into_payload]['address'][
                            'addressDetails']['country']['id'],
                        language=self.language
                    )

                    bank_country_object = {
                        "scheme": bank_country_data['data']['scheme'],
                        "id": bank_country_data['data']['id'],
                        "description": bank_country_data['data']['description'],
                        "uri": bank_country_data['data']['uri']
                    }

                    bank_region_data = self.mdm.get_region(
                        country=payload_tenderers_array[quantity_tenderers]['details']['bankAccounts'][
                            quantity_of_tender_details_bank_accounts_objects_into_payload]['address'][
                            'addressDetails']['country']['id'],
                        region=payload_tenderers_array[quantity_tenderers]['details']['bankAccounts'][
                            quantity_of_tender_details_bank_accounts_objects_into_payload]['address'][
                            'addressDetails']['region']['id'],
                        language=self.language
                    )

                    bank_region_object = {
                        "scheme": bank_region_data['data']['scheme'],
                        "id": bank_region_data['data']['id'],
                        "description": bank_region_data['data']['description'],
                        "uri": bank_region_data['data']['uri']
                    }

                    if payload_tenderers_array[quantity_tenderers]['details']['bankAccounts'][
                        quantity_of_tender_details_bank_accounts_objects_into_payload]['address'][
                        'addressDetails']['locality']['scheme'] == "CUATM":
                        bank_locality_data = self.mdm.get_locality(
                            country=payload_tenderers_array[quantity_tenderers]['details']['bankAccounts'][
                                quantity_of_tender_details_bank_accounts_objects_into_payload]['address'][
                                'addressDetails']['country']['id'],
                            region=payload_tenderers_array[quantity_tenderers]['details']['bankAccounts'][
                                quantity_of_tender_details_bank_accounts_objects_into_payload]['address'][
                                'addressDetails']['region']['id'],
                            locality=payload_tenderers_array[quantity_tenderers]['details']['bankAccounts'][
                                quantity_of_tender_details_bank_accounts_objects_into_payload]['address'][
                                'addressDetails']['locality']['id'],
                            language=self.language
                        )

                        bank_locality_object = {
                            "scheme": bank_locality_data['data']['scheme'],
                            "id": bank_locality_data['data']['id'],
                            "description": bank_locality_data['data']['description'],
                            "uri": bank_locality_data['data']['uri']
                        }
                    else:
                        bank_locality_object = {
                            "scheme": payload_tenderers_array[quantity_tenderers]['details']['bankAccounts'][
                                quantity_of_tender_details_bank_accounts_objects_into_payload]['address'][
                                'addressDetails']['locality']['scheme'],
                            "id": payload_tenderers_array[quantity_tenderers]['details']['bankAccounts'][
                                quantity_of_tender_details_bank_accounts_objects_into_payload]['address'][
                                'addressDetails']['locality']['id'],
                            "description":
                                payload_tenderers_array[quantity_tenderers]['details']['bankAccounts'][
                                    quantity_of_tender_details_bank_accounts_objects_into_payload]['address'][
                                    'addressDetails']['locality']['description']
                        }

                    expected_parties_array[quantity_tenderers]['details']['bankAccounts'][
                        quantity_of_tender_details_bank_accounts_objects_into_payload]['address']['addressDetails'][
                        'country'] = bank_country_object
                    expected_parties_array[quantity_tenderers]['details']['bankAccounts'][
                        quantity_of_tender_details_bank_accounts_objects_into_payload]['address']['addressDetails'][
                        'region'] = bank_region_object
                    expected_parties_array[quantity_tenderers]['details']['bankAccounts'][
                        quantity_of_tender_details_bank_accounts_objects_into_payload]['address']['addressDetails'][
                        'locality'] = bank_locality_object

                    quantity_of_tender_details_bank_accounts_objects_into_payload -= 1

                try:
                    """
                    Check how many quantity of object into release_parties_array['persones'].
                    """
                    list_of_release_party_persones_id = list()
                    for i in payload_tenderers_array[quantity_tenderers]['persones']:
                        for i_1 in i:
                            if i_1 == "identifier":
                                for i_2 in i['identifier']:
                                    if i_2 == "id":
                                        list_of_release_party_persones_id.append(i_2)
                    quantity_of_persones_into_payload = \
                        len(list_of_release_party_persones_id)
                except KeyError:
                    raise KeyError("Check ['releases']['tender']['parties'][*]['persones']['id']")

                expected_parties_array[quantity_tenderers]['persones'] = \
                    payload_tenderers_array[quantity_tenderers]['persones']

                quantity_of_persones_into_payload -= 1
                while quantity_of_persones_into_payload >= 0:
                    expected_parties_array[quantity_tenderers]['persones'][quantity_of_persones_into_payload]['id'] = \
                        payload_tenderers_array[quantity_tenderers]['persones'][
                            quantity_of_persones_into_payload]['identifier']['scheme'] + "-" + \
                        payload_tenderers_array[quantity_tenderers]['persones'][
                            quantity_of_persones_into_payload]['identifier']['id']

                    try:
                        """
                        Check how many quantity of object into release_parties_array['persones']['businessFunctions'].
                        """
                        list_of_release_party_persones_business_functions_id = list()
                        for i in \
                                release_parties_array[quantity_tenderers]['persones'][
                                    quantity_of_persones_into_payload][
                                    'businessFunctions']:
                            for i_1 in i:
                                if i_1 == "id":
                                    list_of_release_party_persones_business_functions_id.append(i_1)
                        quantity_of_business_functions_into_payload = \
                            len(list_of_release_party_persones_business_functions_id)

                    except KeyError:
                        raise KeyError("Check ['releases']['tender']['parties'][*]['persones']['id']")
                    quantity_of_business_functions_into_payload -= 1
                    while quantity_of_business_functions_into_payload >= 0:
                        try:
                            check = is_it_uuid(
                                uuid_to_test=release_parties_array[quantity_tenderers]['persones'][
                                    quantity_of_persones_into_payload]['businessFunctions'][
                                    quantity_of_business_functions_into_payload]['id'],
                                version=4
                            )
                            if check is True:
                                expected_parties_array[quantity_tenderers]['persones'][
                                    quantity_of_persones_into_payload]['businessFunctions'][
                                    quantity_of_business_functions_into_payload]['id'] = \
                                    release_parties_array[quantity_tenderers]['persones'][
                                        quantity_of_persones_into_payload]['businessFunctions'][
                                        quantity_of_business_functions_into_payload]['id']
                            else:
                                raise ValueError("businessFunctions.id in release must be uuid version 4")
                        except Exception:
                            raise Exception("Check your businessFunctions array in release")

                        quantity_of_business_functions_into_payload -= 1
                    quantity_of_persones_into_payload -= 1
                quantity_tenderers -= 1

        except Exception:
            raise Exception("Impossible to enrich parties array framework")
        print("TEST")
        print(json.dumps(expected_parties_array))
        return expected_parties_array
