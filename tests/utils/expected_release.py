import copy

from tests.utils.functions import is_it_uuid, get_value_from_country_csv, get_value_from_region_csv, \
    get_value_from_locality_csv, get_value_from_classification_cpv_dictionary_xls, get_value_from_cpvs_dictionary_csv, \
    get_value_from_classification_unit_dictionary_csv
from tests.utils.release_library import ReleaseLibrary


class ExpectedRelease:
    def __init__(self, environment, language):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.metadata_budget_url = None
        try:
            if environment == "dev":
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
            elif environment == "sandbox":
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

    def ei_release_full_data_model(self, operation_date, release_id, tender_id, ei_id, payload_for_create_ei,
                                   actual_items_array):
        release = {
            "releases": [{}]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.ei_release())
        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in EI release: tender_id in EI release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in EI release: release_id in EI release must be uuid version 4")

        try:
            main_procurement_category = None
            if payload_for_create_ei['tender']['classification']['id'][0:2] == "03" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "1" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "2" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "3" or \
                    payload_for_create_ei['tender']['classification']['id'][0:2] == "44" or \
                    payload_for_create_ei['tender']['classification']['id'][0:2] == "48":
                main_procurement_category = "goods"
            elif payload_for_create_ei['tender']['classification']['id'][0:2] == "45":
                main_procurement_category = "works"
            elif payload_for_create_ei['tender']['classification']['id'][0] == "5" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "6" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "7" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "8" or \
                    payload_for_create_ei['tender']['classification']['id'][0:2] == "92" or \
                    payload_for_create_ei['tender']['classification']['id'][0:2] == "98":
                main_procurement_category = "services"
        except ValueError:
            raise ValueError("main_procurement_category was not defined")

        try:
            buyer_country_data = get_value_from_country_csv(
                country=payload_for_create_ei['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            buyer_region_data = get_value_from_region_csv(
                region=payload_for_create_ei['buyer']['address']['addressDetails']['region']['id'],
                country=payload_for_create_ei['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            if payload_for_create_ei['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":
                buyer_locality_data = get_value_from_locality_csv(
                    locality=payload_for_create_ei['buyer']['address']['addressDetails']['locality']['id'],
                    region=payload_for_create_ei['buyer']['address']['addressDetails']['region']['id'],
                    country=payload_for_create_ei['buyer']['address']['addressDetails']['country']['id'],
                    language=self.language
                )
                buyer_locality_object = {
                    "scheme": buyer_locality_data[2],
                    "id": payload_for_create_ei['buyer']['address']['addressDetails']['locality']['id'],
                    "description": buyer_locality_data[1],
                    "uri": buyer_locality_data[3]
                }
            else:
                buyer_locality_object = {
                    "scheme": payload_for_create_ei['buyer']['address']['addressDetails']['locality']['scheme'],
                    "id": payload_for_create_ei['buyer']['address']['addressDetails']['locality']['id'],
                    "description": payload_for_create_ei['buyer']['address']['addressDetails']['locality'][
                        'description']
                }
        except ValueError:
            raise ValueError("Check 'buyer.address.addressDetails' object")

        try:
            tender_classification_id = get_value_from_classification_cpv_dictionary_xls(
                payload_for_create_ei['tender']['classification']['id'], self.language)
        except ValueError:
            raise ValueError("Check tender.classification.id")

        expected_items_array = None
        try:
            for o in actual_items_array:
                for i in o['classification']:
                    if i == "id":
                        try:
                            is_it_uuid(
                                uuid_to_test=o['classification']['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your item_id in EI release: "
                                             "item_id in EI release must be uuid version 4")
            list_of_item_classification_id = list()
            for o in payload_for_create_ei['tender']['items']:
                for id_ in o['classification']:
                    if id_ == "id":
                        list_of_item_classification_id.append(id_)
            quantity = len(list_of_item_classification_id)
            while quantity > 0:
                try:
                    tender_item_country_data = get_value_from_country_csv(
                        country=payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['country']['id'],
                        language=self.language
                    )
                    tender_item_country_object = {
                        "scheme": tender_item_country_data[2],
                        "id": payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['country']['id'],
                        "description": tender_item_country_data[1],
                        "uri": tender_item_country_data[3]
                    }

                    tender_item_region_data = get_value_from_region_csv(
                        region=payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['region']['id'],
                        country=payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['country']['id'],
                        language=self.language
                    )
                    tender_item_region_object = {
                        "scheme": tender_item_region_data[2],
                        "id": payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['region']['id'],
                        "description": tender_item_region_data[1],
                        "uri": tender_item_region_data[3]
                    }

                    if payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['scheme'] == "CUATM":
                        tender_item_locality_data = get_value_from_locality_csv(
                            locality=payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            region=payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['region']['id'],
                            country=payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['country']['id'],
                            language=self.language
                        )
                        tender_item_locality_object = {
                            "scheme": tender_item_locality_data[2],
                            "id": payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            "description": tender_item_locality_data[1],
                            "uri": tender_item_locality_data[3]
                        }
                    else:
                        tender_item_locality_object = {
                            "scheme": payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['scheme'],
                            "id": payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            "description": payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['description']
                        }
                except ValueError:
                    raise ValueError("Check 'tender.items.deliveryAddress.addressDetails' object")
                cpv_data = get_value_from_classification_cpv_dictionary_xls(
                    cpv=payload_for_create_ei['tender']['items'][quantity - 1]['classification']['id'],
                    language=self.language
                )
                cpvs_data = get_value_from_cpvs_dictionary_csv(
                    cpvs=payload_for_create_ei['tender']['items'][quantity - 1][
                        'additionalClassifications'][0]['id'],
                    language=self.language
                )
                unit_data = get_value_from_classification_unit_dictionary_csv(
                    unit_id=payload_for_create_ei['tender']['items'][quantity - 1]['unit']['id'],
                    language=self.language
                )

                expected_items_array = payload_for_create_ei['tender']['items']
                expected_items_array[quantity - 1]['id'] = actual_items_array[quantity - 1]['id']
                expected_items_array[quantity - 1]['quantity'] = float(payload_for_create_ei['tender']['items'][quantity - 1]['quantity'])
                expected_items_array[quantity - 1]['classification']['id'] = cpv_data[0]
                expected_items_array[quantity - 1]['classification']['scheme'] = "CPV"
                expected_items_array[quantity - 1]['classification']['description'] = cpv_data[1]
                expected_items_array[quantity - 1]['additionalClassifications'][0]['id'] = cpvs_data[0]
                expected_items_array[quantity - 1]['additionalClassifications'][0]['scheme'] = "CPVS"
                expected_items_array[quantity - 1]['additionalClassifications'][0]['description'] = cpvs_data[2]
                expected_items_array[quantity - 1]['unit']['id'] = unit_data[0]
                expected_items_array[quantity - 1]['unit']['name'] = unit_data[1]
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails']['country'] = tender_item_country_object
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails']['region'] = tender_item_region_object
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails']['locality'] = tender_item_locality_object
                quantity -= 1
        except ValueError:
            raise ValueError("Expected items array was not prepared")

        del release['releases'][0]['planning']['budget']['amount']
        del release['releases'][0]['relatedProcesses']

        release['uri'] = f"{self.metadata_budget_url}/{ei_id}/{ei_id}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"

        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = operation_date
        release['releases'][0]['ocid'] = ei_id
        release['releases'][0]['id'] = release_id
        release['releases'][0]['date'] = operation_date
        release['releases'][0]['tag'][0] = "compiled"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = payload_for_create_ei['tender']['title']
        release['releases'][0]['tender']['description'] = payload_for_create_ei['tender']['description']
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "empty"
        release['releases'][0]['tender']['items'] = expected_items_array
        release['releases'][0]['tender']['mainProcurementCategory'] = main_procurement_category
        release['releases'][0]['tender']['classification']['id'] = tender_classification_id[0]
        release['releases'][0]['tender']['classification']['description'] = tender_classification_id[1]
        release['releases'][0]['tender']['classification']['scheme'] = "CPV"
        release['releases'][0]['buyer']['id'] = \
            f"{payload_for_create_ei['buyer']['identifier']['scheme']}-" \
            f"{payload_for_create_ei['buyer']['identifier']['id']}"
        release['releases'][0]['buyer']['name'] = payload_for_create_ei['buyer']['name']
        release['releases'][0]['parties'][0]['id'] = \
            f"{payload_for_create_ei['buyer']['identifier']['scheme']}-" \
            f"{payload_for_create_ei['buyer']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = payload_for_create_ei['buyer']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = payload_for_create_ei['buyer']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = payload_for_create_ei['buyer']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = payload_for_create_ei['buyer']['identifier']['legalName']
        release['releases'][0]['parties'][0]['identifier']['uri'] = payload_for_create_ei['buyer']['identifier']['uri']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = payload_for_create_ei['buyer']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['postalCode'] = payload_for_create_ei['buyer']['address']['postalCode']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country']['id'] = buyer_country_data[0]
        release['releases'][0]['parties'][0]['address']['addressDetails']['country']['description'] = buyer_country_data[1]
        release['releases'][0]['parties'][0]['address']['addressDetails']['country']['scheme'] = buyer_country_data[2]
        release['releases'][0]['parties'][0]['address']['addressDetails']['country']['uri'] = buyer_country_data[3]
        release['releases'][0]['parties'][0]['address']['addressDetails']['region']['id'] = buyer_region_data[0]
        release['releases'][0]['parties'][0]['address']['addressDetails']['region']['description'] = buyer_region_data[1]
        release['releases'][0]['parties'][0]['address']['addressDetails']['region']['scheme'] = buyer_region_data[2]
        release['releases'][0]['parties'][0]['address']['addressDetails']['region']['uri'] = buyer_region_data[3]
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = buyer_locality_object
        release['releases'][0]['parties'][0]['additionalIdentifiers'] = payload_for_create_ei['buyer']['additionalIdentifiers']
        release['releases'][0]['parties'][0]['contactPoint']['name'] = payload_for_create_ei['buyer']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = payload_for_create_ei['buyer']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = payload_for_create_ei['buyer']['contactPoint']['email']
        release['releases'][0]['parties'][0]['contactPoint']['faxNumber'] = payload_for_create_ei['buyer']['contactPoint']['faxNumber']
        release['releases'][0]['parties'][0]['contactPoint']['url'] = payload_for_create_ei['buyer']['contactPoint']['url']
        release['releases'][0]['parties'][0]['details'] = payload_for_create_ei['buyer']['details']
        release['releases'][0]['parties'][0]['roles'][0] = "buyer"
        release['releases'][0]['planning']['budget']['id'] = tender_classification_id[0]
        release['releases'][0]['planning']['budget']['period']['startDate'] = payload_for_create_ei['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = payload_for_create_ei['planning']['budget']['period']['endDate']
        release['releases'][0]['planning']['rationale'] = payload_for_create_ei['planning']['rationale']
        return release

    def ei_release_obligatory_data_model(self, operation_date, release_id, tender_id, ei_id, payload_for_create_ei):
        release = {
            "releases": [{}]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.ei_release())
        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in EI release: tender_id in EI release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in EI release: release_id in EI release must be uuid version 4")

        try:
            main_procurement_category = None
            if payload_for_create_ei['tender']['classification']['id'][0:2] == "03" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "1" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "2" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "3" or \
                    payload_for_create_ei['tender']['classification']['id'][0:2] == "44" or \
                    payload_for_create_ei['tender']['classification']['id'][0:2] == "48":
                main_procurement_category = "goods"
            elif payload_for_create_ei['tender']['classification']['id'][0:2] == "45":
                main_procurement_category = "works"
            elif payload_for_create_ei['tender']['classification']['id'][0] == "5" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "6" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "7" or \
                    payload_for_create_ei['tender']['classification']['id'][0] == "8" or \
                    payload_for_create_ei['tender']['classification']['id'][0:2] == "92" or \
                    payload_for_create_ei['tender']['classification']['id'][0:2] == "98":
                main_procurement_category = "services"
        except ValueError:
            raise ValueError("main_procurement_category was not defined")

        try:
            buyer_country_data = get_value_from_country_csv(
                country=payload_for_create_ei['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            buyer_region_data = get_value_from_region_csv(
                region=payload_for_create_ei['buyer']['address']['addressDetails']['region']['id'],
                country=payload_for_create_ei['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            if payload_for_create_ei['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":
                buyer_locality_data = get_value_from_locality_csv(
                    locality=payload_for_create_ei['buyer']['address']['addressDetails']['locality']['id'],
                    region=payload_for_create_ei['buyer']['address']['addressDetails']['region']['id'],
                    country=payload_for_create_ei['buyer']['address']['addressDetails']['country']['id'],
                    language=self.language
                )
                buyer_locality_object = {
                    "scheme": buyer_locality_data[2],
                    "id": payload_for_create_ei['buyer']['address']['addressDetails']['locality']['id'],
                    "description": buyer_locality_data[1],
                    "uri": buyer_locality_data[3]
                }
            else:
                buyer_locality_object = {
                    "scheme": payload_for_create_ei['buyer']['address']['addressDetails']['locality']['scheme'],
                    "id": payload_for_create_ei['buyer']['address']['addressDetails']['locality']['id'],
                    "description": payload_for_create_ei['buyer']['address']['addressDetails']['locality'][
                        'description']
                }
        except ValueError:
            raise ValueError("Check 'buyer.address.addressDetails' object")

        try:
            tender_classification_id = get_value_from_classification_cpv_dictionary_xls(
                payload_for_create_ei['tender']['classification']['id'], self.language)
        except ValueError:
            raise ValueError("Check tender.classification.id")

        del release['releases'][0]['planning']['budget']['amount']
        del release['releases'][0]['relatedProcesses']
        del release['releases'][0]['tender']['description']
        del release['releases'][0]['tender']['items']
        del release['releases'][0]['parties'][0]['identifier']['uri']
        del release['releases'][0]['parties'][0]['address']['postalCode']
        del release['releases'][0]['parties'][0]['additionalIdentifiers']
        del release['releases'][0]['parties'][0]['contactPoint']['faxNumber']
        del release['releases'][0]['parties'][0]['contactPoint']['url']
        del release['releases'][0]['parties'][0]['details']
        del release['releases'][0]['planning']['rationale']
        release['uri'] = f"{self.metadata_budget_url}/{ei_id}/{ei_id}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"

        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = operation_date
        release['releases'][0]['ocid'] = ei_id
        release['releases'][0]['id'] = release_id
        release['releases'][0]['date'] = operation_date
        release['releases'][0]['tag'][0] = "compiled"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = payload_for_create_ei['tender']['title']
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "empty"
        release['releases'][0]['tender']['mainProcurementCategory'] = main_procurement_category
        release['releases'][0]['tender']['classification']['id'] = tender_classification_id[0]
        release['releases'][0]['tender']['classification']['description'] = tender_classification_id[1]
        release['releases'][0]['tender']['classification']['scheme'] = "CPV"
        release['releases'][0]['buyer']['id'] = \
            f"{payload_for_create_ei['buyer']['identifier']['scheme']}-" \
            f"{payload_for_create_ei['buyer']['identifier']['id']}"
        release['releases'][0]['buyer']['name'] = payload_for_create_ei['buyer']['name']
        release['releases'][0]['parties'][0]['id'] = \
            f"{payload_for_create_ei['buyer']['identifier']['scheme']}-" \
            f"{payload_for_create_ei['buyer']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = payload_for_create_ei['buyer']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = payload_for_create_ei['buyer']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = payload_for_create_ei['buyer']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = payload_for_create_ei['buyer']['identifier']['legalName']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = payload_for_create_ei['buyer']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country']['id'] = buyer_country_data[0]
        release['releases'][0]['parties'][0]['address']['addressDetails']['country']['description'] = buyer_country_data[1]
        release['releases'][0]['parties'][0]['address']['addressDetails']['country']['scheme'] = buyer_country_data[2]
        release['releases'][0]['parties'][0]['address']['addressDetails']['country']['uri'] = buyer_country_data[3]
        release['releases'][0]['parties'][0]['address']['addressDetails']['region']['id'] = buyer_region_data[0]
        release['releases'][0]['parties'][0]['address']['addressDetails']['region']['description'] = buyer_region_data[1]
        release['releases'][0]['parties'][0]['address']['addressDetails']['region']['scheme'] = buyer_region_data[2]
        release['releases'][0]['parties'][0]['address']['addressDetails']['region']['uri'] = buyer_region_data[3]
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = buyer_locality_object
        release['releases'][0]['parties'][0]['contactPoint']['name'] = payload_for_create_ei['buyer']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = payload_for_create_ei['buyer']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = payload_for_create_ei['buyer']['contactPoint']['email']
        release['releases'][0]['parties'][0]['roles'][0] = "buyer"
        release['releases'][0]['planning']['budget']['id'] = tender_classification_id[0]
        release['releases'][0]['planning']['budget']['period']['startDate'] = payload_for_create_ei['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = payload_for_create_ei['planning']['budget']['period']['endDate']
        return release

    def ei_tender_items_array_release(self, actual_items_array, payload):
        expected_items_array = None
        try:
            for o in actual_items_array:
                for i in o['classification']:
                    if i == "id":
                        try:
                            is_it_uuid(
                                uuid_to_test=o['classification']['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your item_id in EI release: "
                                             "item_id in EI release must be uuid version 4")
            list_of_item_classification_id = list()
            for o in payload['tender']['items']:
                for id_ in o['classification']:
                    if id_ == "id":
                        list_of_item_classification_id.append(id_)
            quantity = len(list_of_item_classification_id)
            while quantity > 0:
                try:
                    tender_item_country_data = get_value_from_country_csv(
                        country=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['country']['id'],
                        language=self.language
                    )
                    tender_item_country_object = {
                        "scheme": tender_item_country_data[2],
                        "id": payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['country']['id'],
                        "description": tender_item_country_data[1],
                        "uri": tender_item_country_data[3]
                    }

                    tender_item_region_data = get_value_from_region_csv(
                        region=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['region']['id'],
                        country=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['country']['id'],
                        language=self.language
                    )
                    tender_item_region_object = {
                        "scheme": tender_item_region_data[2],
                        "id": payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['region']['id'],
                        "description": tender_item_region_data[1],
                        "uri": tender_item_region_data[3]
                    }

                    if payload['tender']['items'][quantity - 1]['deliveryAddress'][
                        'addressDetails']['locality']['scheme'] == "CUATM":
                        tender_item_locality_data = get_value_from_locality_csv(
                            locality=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            region=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['region']['id'],
                            country=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['country']['id'],
                            language=self.language
                        )
                        tender_item_locality_object = {
                            "scheme": tender_item_locality_data[2],
                            "id": payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            "description": tender_item_locality_data[1],
                            "uri": tender_item_locality_data[3]
                        }
                    else:
                        tender_item_locality_object = {
                            "scheme": payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['scheme'],
                            "id": payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            "description": payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['description']
                        }
                except ValueError:
                    raise ValueError("Check 'tender.items.deliveryAddress.addressDetails' object")
                cpv_data = get_value_from_classification_cpv_dictionary_xls(
                    cpv=payload['tender']['items'][quantity - 1]['classification']['id'],
                    language=self.language
                )
                cpvs_data = get_value_from_cpvs_dictionary_csv(
                    cpvs=payload['tender']['items'][quantity - 1][
                        'additionalClassifications'][0]['id'],
                    language=self.language
                )
                unit_data = get_value_from_classification_unit_dictionary_csv(
                    unit_id=payload['tender']['items'][quantity - 1]['unit']['id'],
                    language=self.language
                )

                expected_items_array = payload['tender']['items']
                expected_items_array[quantity - 1]['id'] = actual_items_array[quantity - 1]['id']
                expected_items_array[quantity - 1]['quantity'] = float(
                    payload['tender']['items'][quantity - 1]['quantity'])
                expected_items_array[quantity - 1]['classification']['id'] = cpv_data[0]
                expected_items_array[quantity - 1]['classification']['scheme'] = "CPV"
                expected_items_array[quantity - 1]['classification']['description'] = cpv_data[1]
                expected_items_array[quantity - 1]['additionalClassifications'][0]['id'] = cpvs_data[0]
                expected_items_array[quantity - 1]['additionalClassifications'][0]['scheme'] = "CPVS"
                expected_items_array[quantity - 1]['additionalClassifications'][0]['description'] = cpvs_data[2]
                expected_items_array[quantity - 1]['unit']['id'] = unit_data[0]
                expected_items_array[quantity - 1]['unit']['name'] = unit_data[1]
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails'][
                    'country'] = tender_item_country_object
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails'][
                    'region'] = tender_item_region_object
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails'][
                    'locality'] = tender_item_locality_object
                quantity -= 1
        except ValueError:
            raise ValueError("Expected items array was not prepared")
        return expected_items_array