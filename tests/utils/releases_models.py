import copy
from tests.utils.functions import is_it_uuid, get_value_from_classification_cpv_dictionary_xls, \
    get_value_from_cpvs_dictionary_csv, get_value_from_classification_unit_dictionary_csv, get_value_from_country_csv, \
    get_value_from_region_csv, get_value_from_locality_csv, generate_tender_classification_id


class EiRelease:
    def __init__(self, operation_date, release_id, tender_id, ei_id, environment, payload_for_create_ei, language):
        self.tender_id = tender_id
        self.language = language
        self.payload_for_create_ei = payload_for_create_ei
        self.release = None
        metadata_budget_url = None
        try:
            if environment == "dev":
                metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
            elif environment == "sandbox":
                metadata_budget_url = "http://public.eprocurement.systems/budgets"
        except ValueError:
            print("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")
        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            print("Check your tender_id in EI release: tender_id in EI release must be uuid version 4")
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

        tender_classification_id = get_value_from_classification_cpv_dictionary_xls(
            payload_for_create_ei['tender']['classification']['id'], self.language)

        buyer_country_data = get_value_from_country_csv(
            country=payload_for_create_ei['buyer']['address']['addressDetails']['country']['id'],
            language=self.language
        )

        buyer_region_data = get_value_from_region_csv(
            region=payload_for_create_ei['buyer']['address']['addressDetails']['region']['id'],
            country=payload_for_create_ei['buyer']['address']['addressDetails']['country']['id'],
            language=self.language
        )

        buyer_locality_data = get_value_from_locality_csv(
            locality=payload_for_create_ei['buyer']['address']['addressDetails']['locality']['id'],
            region=payload_for_create_ei['buyer']['address']['addressDetails']['region']['id'],
            country=payload_for_create_ei['buyer']['address']['addressDetails']['country']['id'],
            language=self.language
        )
        self.release = {
            "uri": f"{metadata_budget_url}/{ei_id}/{ei_id}",
            "version": "1.1",
            "extensions": [
                "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"],
            "publisher": {
                "name": "M-Tender",
                "uri": "https://www.mtender.gov.md"
            },
            "license": "http://opendefinition.org/licenses/",
            "publicationPolicy": "http://opendefinition.org/licenses/",
            "publishedDate": operation_date,
            "releases": [{
                "ocid": ei_id,
                # timestamp в release_id формируется системой произвольно -> невозможно ни на что завязаться
                "id": f"{ei_id}-{release_id[29:42]}",
                "date": operation_date,
                "tag": ["compiled"],
                "language": self.language,
                "initiationType": "tender",
                "tender": {
                    "id": tender_id,
                    "title": payload_for_create_ei['tender']['title'],
                    "status": "planning",
                    "statusDetails": "empty",
                    "mainProcurementCategory": main_procurement_category,
                    "classification": {
                        "scheme": "CPV",
                        "id": payload_for_create_ei['tender']['classification']['id'],
                        "description": tender_classification_id[1]
                    }
                },
                "buyer": {
                    "id": f"{payload_for_create_ei['buyer']['identifier']['scheme']}-"
                          f"{payload_for_create_ei['buyer']['identifier']['id']}",
                    "name": payload_for_create_ei['buyer']['name']
                },
                "parties": [{
                    "id": f"{payload_for_create_ei['buyer']['identifier']['scheme']}-"
                          f"{payload_for_create_ei['buyer']['identifier']['id']}",
                    "name": payload_for_create_ei['buyer']['name'],
                    "identifier": {
                        "scheme": payload_for_create_ei['buyer']['identifier']['scheme'],
                        "id": payload_for_create_ei['buyer']['identifier']['id'],
                        "legalName": payload_for_create_ei['buyer']['identifier']['legalName']
                    },
                    "address": {
                        "streetAddress": payload_for_create_ei['buyer']['address']['streetAddress'],
                        "addressDetails": {
                            "country": {
                                "scheme": buyer_country_data[2],
                                "id": payload_for_create_ei['buyer']['address'][
                                    'addressDetails']['country']['id'],
                                "description": buyer_country_data[1],
                                "uri": buyer_country_data[3]
                            },
                            "region": {
                                "scheme": buyer_region_data[2],
                                "id": payload_for_create_ei['buyer']['address'][
                                    'addressDetails']['region']['id'],
                                "description": buyer_region_data[1],
                                "uri": buyer_region_data[3]
                            },
                            "locality": {
                                "scheme": buyer_locality_data[2],
                                "id": payload_for_create_ei['buyer']['address'][
                                    'addressDetails']['locality']['id'],
                                "description": buyer_locality_data[1],
                                "uri": buyer_locality_data[3]
                            }
                        }
                    },
                    "contactPoint": {
                        "name": payload_for_create_ei['buyer']['contactPoint']['name'],
                        "email": payload_for_create_ei['buyer']['contactPoint']['email'],
                        "telephone": payload_for_create_ei['buyer']['contactPoint']['telephone']
                    },
                    "roles": ["buyer"]
                }],
                "planning": {
                    "budget": {
                        "id": payload_for_create_ei['tender']['classification']['id'],
                        "period": {
                            "startDate": payload_for_create_ei['planning']['budget']['period'][
                                'startDate'],
                            "endDate": payload_for_create_ei['planning']['budget']['period'][
                                'endDate']
                        }
                    }
                }
            }]
        }

    def for_create_ei_obligatory_data_model(self):
        release_ei_obligatory_data_model = copy.deepcopy(self.release)
        return release_ei_obligatory_data_model

    def for_create_ei_obligatory_data_model_with_items_array(self, actual_items_array):
        release_ei_obligatory_with_items_array_data_model = copy.deepcopy(self.release)
        main_procurement_category = None
        if self.payload_for_create_ei['tender']['classification']['id'][0:2] == "03" or \
                self.payload_for_create_ei['tender']['classification']['id'][0] == "1" or \
                self.payload_for_create_ei['tender']['classification']['id'][0] == "2" or \
                self.payload_for_create_ei['tender']['classification']['id'][0] == "3" or \
                self.payload_for_create_ei['tender']['classification']['id'][0:2] == "44" or \
                self.payload_for_create_ei['tender']['classification']['id'][0:2] == "48":
            main_procurement_category = "goods"
        elif self.payload_for_create_ei['tender']['classification']['id'][0:2] == "45":
            main_procurement_category = "works"
        elif self.payload_for_create_ei['tender']['classification']['id'][0] == "5" or \
                self.payload_for_create_ei['tender']['classification']['id'][0] == "6" or \
                self.payload_for_create_ei['tender']['classification']['id'][0] == "7" or \
                self.payload_for_create_ei['tender']['classification']['id'][0] == "8" or \
                self.payload_for_create_ei['tender']['classification']['id'][0:2] == "92" or \
                self.payload_for_create_ei['tender']['classification']['id'][0:2] == "98":
            main_procurement_category = "services"
        tender_classification_id = get_value_from_classification_cpv_dictionary_xls(
            generate_tender_classification_id(actual_items_array), self.language)
        release_ei_obligatory_with_items_array_data_model['releases'][0]['tender'] = {
            "id": self.tender_id,
            "title": self.payload_for_create_ei['tender']['title'],
            "status": "planning",
            "statusDetails": "empty",
            "mainProcurementCategory": main_procurement_category,
            "classification": {
                "scheme": "CPV",
                "id": tender_classification_id[0],
                "description": tender_classification_id[1]
            },
            "items": actual_items_array
        }
        list_of_keys = list()
        for o in self.payload_for_create_ei['tender']['items']:
            for id_ in o['classification']:
                if id_ == "id":
                    list_of_keys.append(id_)
        quantity = len(list_of_keys)

        for o in release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items']:
            for i in o['classification']:
                if i == "id":
                    try:
                        is_it_uuid(
                            uuid_to_test=o['classification']['id'],
                            version=4
                        )
                    except ValueError:
                        print("Check your item_id in EI release: item_id in EI release must be uuid version 4")
        item_country_data = get_value_from_country_csv(
            country=self.payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                'addressDetails']['country']['id'],
            language=self.language
        )
        item_region_data = get_value_from_region_csv(
            region=self.payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                'addressDetails']['region']['id'],
            country=self.payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                'addressDetails']['country']['id'],
            language=self.language
        )
        item_locality_data = get_value_from_locality_csv(
            locality=self.payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                'addressDetails']['locality']['id'],
            region=self.payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                'addressDetails']['region']['id'],
            country=self.payload_for_create_ei['tender']['items'][quantity - 1]['deliveryAddress'][
                'addressDetails']['country']['id'],
            language=self.language
        )
        cpv_data = get_value_from_classification_cpv_dictionary_xls(
            cpv=self.payload_for_create_ei['tender']['items'][quantity - 1]['classification']['id'],
            language=self.language
        )
        cpvs_data = get_value_from_cpvs_dictionary_csv(
            cpvs=self.payload_for_create_ei['tender']['items'][quantity - 1][
                'additionalClassifications'][0]['id'],
            language=self.language
        )
        unit_data = get_value_from_classification_unit_dictionary_csv(
            unit_id=self.payload_for_create_ei['tender']['items'][quantity - 1]['unit']['id'],
            language=self.language
        )
        while quantity > 0:
            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'description'] = \
                self.payload_for_create_ei['tender']['items'][quantity - 1]['description']

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'quantity'] = \
                self.payload_for_create_ei['tender']['items'][quantity - 1]['quantity']

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['streetAddress'] = \
                self.payload_for_create_ei['tender']['items'][quantity - 1][
                    'deliveryAddress']['streetAddress']

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['postalCode'] = \
                self.payload_for_create_ei['tender']['items'][quantity - 1][
                    'deliveryAddress']['postalCode']

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['country']['id'] = \
                self.payload_for_create_ei['tender']['items'][quantity - 1][
                    'deliveryAddress']['addressDetails']['country']['id']

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['country']['scheme'] = \
                item_country_data[2]

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['country']['description'] = \
                item_country_data[1]

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['country']['uri'] = \
                item_country_data[4]

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['region']['id'] = \
                self.payload_for_create_ei['tender']['items'][quantity - 1][
                    'deliveryAddress']['addressDetails']['region']['id']

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['region']['scheme'] = item_region_data[2]

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['region']['description'] = item_region_data[1]

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['region']['uri'] = item_region_data[4]

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['locality']['id'] = \
                self.payload_for_create_ei['tender']['items'][quantity - 1][
                    'deliveryAddress']['addressDetails']['locality']['id']

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['locality']['scheme'] = item_locality_data[2]

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['locality']['description'] = item_locality_data[1]

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'deliveryAddress']['addressDetails']['locality']['uri'] = item_locality_data[4]

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'classification']['id'] = \
                self.payload_for_create_ei['tender']['items'][quantity - 1][
                    'classification']['id']

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'classification']['scheme'] = "CPV"

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'classification']['description'] = cpv_data[1]

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'additionalClassifications'][0]['id'] = \
                self.payload_for_create_ei['tender']['items'][quantity - 1][
                    'additionalClassifications'][0]['id']

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'additionalClassifications'][0]['scheme'] = "CPVS"

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1][
                'additionalClassifications'][0]['description'] = cpvs_data[2]

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1]['unit'][
                'id'] = \
                self.payload_for_create_ei['tender']['items'][quantity - 1]['unit']['id']

            release_ei_obligatory_with_items_array_data_model['releases'][0]['tender']['items'][quantity - 1]['unit'][
                'description'] = unit_data[1]
            quantity -= 1
        return release_ei_obligatory_with_items_array_data_model

    def for_create_ei_obligatory_data_model_with_buyer_details(self):
        release_ei_obligatory_with_buyer_details_data_model = copy.deepcopy(self.release)
        buyer_role_in_parties = list()
        for p in release_ei_obligatory_with_buyer_details_data_model["releases"][0]["parties"]:
            if p["roles"] == ["buyer"]:
                p['details'] = self.payload_for_create_ei['buyer']['details']
                buyer_role_in_parties.append(p)
        return release_ei_obligatory_with_buyer_details_data_model
