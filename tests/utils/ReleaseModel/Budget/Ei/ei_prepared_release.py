import copy

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi
from tests.utils.ReleaseModel.Budget.Ei.ei_release_library import ReleaseLibrary
from tests.utils.functions import is_it_uuid, get_value_from_cpvs_dictionary_csv, get_value_from_country_csv, \
    get_value_from_region_csv, get_value_from_locality_csv, get_value_from_classification_cpv_dictionary_xls, \
    get_value_from_classification_unit_dictionary_csv


class EiExpectedRelease:
    def __init__(self, environment, language):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.metadata_budget_url = None
        self.main_procurement_category = None
        try:
            if environment == "dev":
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
                self.publisher_name = "M-Tender"
                self.publisher_uri = "https://www.mtender.gov.md"
                self.extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"]
            elif environment == "sandbox":
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
                self.publisher_name = "Viešųjų pirkimų tarnyba"
                self.publisher_uri = "https://vpt.lrv.lt"
                self.extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.json"]
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")
        GlobalClassMetadata.metadata_budget_url = self.metadata_budget_url

    def prepare_expected_items_array(self, payload_items_array, release_items_array):
        expected_items_array = []
        try:
            """
            Check how many quantity of object into payload_items_array.
            """
            list_of_payload_item_id = list()
            for item_object in payload_items_array:
                for i in item_object:
                    if i == "id":
                        list_of_payload_item_id.append(i)
            quantity_of_item_object_into_payload = len(list_of_payload_item_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['items'][*]['id']")

        try:
            """
            Check how many quantity of object into release_items_array.
            Check release_items_array[*]['id'] -> is it uuid.
            """
            list_of_release_item_id = list()
            for item_object in release_items_array:
                for i in item_object:
                    if i == "id":
                        list_of_release_item_id.append(i)
                        try:
                            is_it_uuid(
                                uuid_to_test=item_object['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your items array in release: "
                                             "release_items_array.id in release must be uuid version 4")
            quantity_of_item_object_into_release = len(list_of_release_item_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['items'][*]['id']")

        try:
            """
            Compare quantity of item objects into payload_items_array and release_items_array.
            """
            if quantity_of_item_object_into_payload == quantity_of_item_object_into_release:
                pass
        except KeyError:
            raise KeyError("Quantity of item objects into payload_items_array != "
                           "quantity of item objects into and release_items_array")

        try:
            """
            Prepare items array framework.
            """
            quantity_one = quantity_of_item_object_into_release

            while quantity_one > 0:
                item_object = {}
                item_object.update(self.constructor.release_tender_item_object())
                item_object['additionalClassifications'] = [{}]
                item_object['additionalClassifications'][0].update(
                    self.constructor.release_tender_items_additional_classifications())
                expected_items_array.append(item_object)
                quantity_one -= 1
        except ValueError:
            raise ValueError("Impossible to build expected items array framework.")

        try:
            """
            Enrich items array by value.
            """
            quantity_two = quantity_of_item_object_into_release - 1
            while quantity_two >= 0:
                expected_items_array[quantity_two]['id'] = release_items_array[quantity_two]['id']
                """
                Enrich or delete optional fields: 
                - "additionalClassifications";
                - "deliveryAddress";
                """

                if "additionalClassifications" in payload_items_array[quantity_two]:
                    cpvs_data = get_value_from_cpvs_dictionary_csv(
                        cpvs=payload_items_array[quantity_two]['additionalClassifications'][0]['id'],
                        language=self.language
                    )

                    expected_items_array[quantity_two]['additionalClassifications'][0]['id'] = cpvs_data[0]
                    expected_items_array[quantity_two]['additionalClassifications'][0]['scheme'] = "CPVS"
                    expected_items_array[quantity_two]['additionalClassifications'][0]['description'] = cpvs_data[2]
                else:
                    del expected_items_array[quantity_two]['additionalClassifications']

                if "deliveryAddress" in payload_items_array[quantity_two]:
                    item_country_data = get_value_from_country_csv(
                        country=payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['country']['id'],
                        language=self.language
                    )
                    item_country_object = {
                        "scheme": item_country_data[2],
                        "id": payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['country']['id'],
                        "description": item_country_data[1],
                        "uri": item_country_data[3]
                    }

                    item_region_data = get_value_from_region_csv(
                        region=payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['region']['id'],
                        country=payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['country']['id'],
                        language=self.language
                    )
                    item_region_object = {
                        "scheme": item_region_data[2],
                        "id": payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['region']['id'],
                        "description": item_region_data[1],
                        "uri": item_region_data[3]
                    }

                    if payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['locality']['scheme'] \
                            == "CUATM":
                        item_locality_data = get_value_from_locality_csv(
                            locality=payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'locality']['id'],
                            region=payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'region']['id'],
                            country=payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'country']['id'],
                            language=self.language
                        )
                        item_locality_object = {
                            "scheme": item_locality_data[2],
                            "id": payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'locality']['id'],
                            "description": item_locality_data[1],
                            "uri": item_locality_data[3]
                        }
                    else:
                        item_locality_object = {
                            "scheme":
                                payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                    'locality']['scheme'],
                            "id": payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'locality']['id'],
                            "description": payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'locality']['description']
                        }

                    expected_items_array[quantity_two]['deliveryAddress']['addressDetails']['country'] = \
                        item_country_object
                    expected_items_array[quantity_two]['deliveryAddress']['addressDetails']['region'] = \
                        item_region_object
                    expected_items_array[quantity_two]['deliveryAddress']['addressDetails']['locality'] = \
                        item_locality_object
                    expected_items_array[quantity_two]['deliveryAddress']['streetAddress'] = \
                        payload_items_array[quantity_two]['deliveryAddress']['streetAddress']
                    if "postalCode" in payload_items_array[quantity_two]['deliveryAddress']:
                        expected_items_array[quantity_two]['deliveryAddress']['postalCode'] = \
                            payload_items_array[quantity_two]['deliveryAddress']['postalCode']
                    else:
                        del expected_items_array[quantity_two]['deliveryAddress']['postalCode']
                else:
                    del expected_items_array[quantity_two]['deliveryAddress']

                """
                Enrich obligatory fields:
                - "description";
                - "classification";
                - "unit";
                - "quantity"
                """
                expected_items_array[quantity_two]['description'] = payload_items_array[quantity_two]['description']
                cpv_data = get_value_from_classification_cpv_dictionary_xls(
                    cpv=payload_items_array[quantity_two]['classification']['id'],
                    language=self.language
                )
                expected_items_array[quantity_two]['classification']['id'] = cpv_data[0]
                expected_items_array[quantity_two]['classification']['scheme'] = "CPV"
                expected_items_array[quantity_two]['classification']['description'] = cpv_data[1]

                unit_data = get_value_from_classification_unit_dictionary_csv(
                    unit_id=payload_items_array[quantity_two]['unit']['id'],
                    language=self.language
                )
                expected_items_array[quantity_two]['unit']['id'] = unit_data[0]
                expected_items_array[quantity_two]['unit']['name'] = unit_data[1]

                expected_items_array[quantity_two]['quantity'] = float(payload_items_array[quantity_two]['quantity'])
                quantity_two -= 1
        except ValueError:
            raise ValueError("Impossible to enrich expected items array framework.")
        return expected_items_array

    def ei_release_full_data_model(self):

        release_id = GlobalClassCreateEi.actual_ei_release['releases'][0]['id']
        tender_id = GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['id']

        release = {
            "releases": [{
                "tender": {},
                "buyer": {},
                "parties": [{}],
                "planning": {}
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.release_tender_section())

        release['releases'][0]['tender']['items'].append(self.constructor.release_tender_item_object())

        release['releases'][0]['tender']['items'][0]['additionalClassifications'].append(
            self.constructor.release_tender_items_additional_classifications())
        release['releases'][0]['buyer'].update(self.constructor.release_buyer_section())
        release['releases'][0]['parties'][0].update(self.constructor.release_parties_section())
        release['releases'][0]['planning'].update(self.constructor.release_planning_section())

        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in Ei release: tender_id in Ei release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in Ei release: release_id in Ei release must be uuid version 4")

        try:
            if GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "03" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "1" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "2" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "3" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "44" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "48":
                self.main_procurement_category = "goods"
            elif GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "45":
                self.main_procurement_category = "works"
            elif GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "5" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "6" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "7" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "8" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "92" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "98":
                self.main_procurement_category = "services"
        except ValueError:
            raise ValueError("main_procurement_category was not defined")

        try:
            buyer_country_data = get_value_from_country_csv(
                country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            buyer_country_object = {
                "scheme": buyer_country_data[2],
                "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                "description": buyer_country_data[1],
                "uri": buyer_country_data[3]
            }

            buyer_region_data = get_value_from_region_csv(
                region=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            buyer_region_object = {
                "scheme": buyer_region_data[2],
                "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                "description": buyer_region_data[1],
                "uri": buyer_region_data[3]
            }

            if GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":
                buyer_locality_data = get_value_from_locality_csv(
                    locality=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    region=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                    country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                    language=self.language
                )
                buyer_locality_object = {
                    "scheme": buyer_locality_data[2],
                    "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": buyer_locality_data[1],
                    "uri": buyer_locality_data[3]
                }
            else:
                buyer_locality_object = {
                    "scheme": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['scheme'],
                    "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality'][
                        'description']
                }
        except ValueError:
            raise ValueError("Check 'buyer.address.addressDetails' object")

        try:
            tender_classification_id = get_value_from_classification_cpv_dictionary_xls(
                GlobalClassCreateEi.payload['tender']['classification']['id'], self.language)
        except ValueError:
            raise ValueError("Check tender.classification.id")

        release['uri'] = f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateEi.ei_ocid}"
        release['version'] = "1.1"
        release['extensions'] = self.extensions

        release['publisher']['name'] = self.publisher_name
        release['publisher']['uri'] = self.publisher_uri
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = GlobalClassCreateEi.feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = GlobalClassCreateEi.ei_ocid
        release['releases'][0]['id'] = f"{GlobalClassCreateEi.ei_ocid}-{release_id[29:42]}"
        release['releases'][0]['date'] = GlobalClassCreateEi.feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "compiled"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = GlobalClassCreateEi.payload['tender']['title']
        release['releases'][0]['tender']['description'] = GlobalClassCreateEi.payload['tender']['description']
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "empty"
        release['releases'][0]['tender']['items'] = self.prepare_expected_items_array(
            payload_items_array=GlobalClassCreateEi.payload['tender']['items'],
            release_items_array=GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['items']
        )
        release['releases'][0]['tender']['mainProcurementCategory'] = self.main_procurement_category
        release['releases'][0]['tender']['classification']['id'] = tender_classification_id[0]
        release['releases'][0]['tender']['classification']['description'] = tender_classification_id[1]
        release['releases'][0]['tender']['classification']['scheme'] = "CPV"
        release['releases'][0]['buyer']['id'] = \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}"
        release['releases'][0]['buyer']['name'] = GlobalClassCreateEi.payload['buyer']['name']
        release['releases'][0]['parties'][0]['id'] = \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = GlobalClassCreateEi.payload['buyer']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['legalName']
        release['releases'][0]['parties'][0]['identifier']['uri'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['uri']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            GlobalClassCreateEi.payload['buyer']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['postalCode'] = \
            GlobalClassCreateEi.payload['buyer']['address']['postalCode']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = buyer_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = buyer_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = buyer_locality_object
        release['releases'][0]['parties'][0]['additionalIdentifiers'] = \
            GlobalClassCreateEi.payload['buyer']['additionalIdentifiers']
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['email']
        release['releases'][0]['parties'][0]['contactPoint']['faxNumber'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['faxNumber']
        release['releases'][0]['parties'][0]['contactPoint']['url'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['url']
        release['releases'][0]['parties'][0]['details'] = GlobalClassCreateEi.payload['buyer']['details']
        release['releases'][0]['parties'][0]['roles'][0] = "buyer"
        release['releases'][0]['planning']['budget']['id'] = tender_classification_id[0]
        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            GlobalClassCreateEi.payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            GlobalClassCreateEi.payload['planning']['budget']['period']['endDate']
        release['releases'][0]['planning']['rationale'] = GlobalClassCreateEi.payload['planning']['rationale']
        return release

    def ei_release_obligatory_data_model(self):

        release_id = GlobalClassCreateEi.actual_ei_release['releases'][0]['id']
        tender_id = GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['id']

        release = {
            "releases": [{
                "tender": {},
                "buyer": {},
                "parties": [{}],
                "planning": {}
            }]
        }

        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.release_tender_section())
        release['releases'][0]['buyer'].update(self.constructor.release_buyer_section())
        release['releases'][0]['parties'][0].update(self.constructor.release_parties_section())
        release['releases'][0]['planning'].update(self.constructor.release_planning_section())

        del release['releases'][0]['tender']['description']
        del release['releases'][0]['tender']['items']
        del release['releases'][0]['parties'][0]['identifier']['uri']
        del release['releases'][0]['parties'][0]['address']['postalCode']
        del release['releases'][0]['parties'][0]['additionalIdentifiers']
        del release['releases'][0]['parties'][0]['contactPoint']['faxNumber']
        del release['releases'][0]['parties'][0]['contactPoint']['url']
        del release['releases'][0]['parties'][0]['details']
        del release['releases'][0]['planning']['rationale']

        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in Ei release: tender_id in Ei release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in Ei release: release_id in Ei release must be uuid version 4")

        try:

            if GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "03" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "1" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "2" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "3" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "44" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "48":
                self.main_procurement_category = "goods"
            elif GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "45":
                self.main_procurement_category = "works"
            elif GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "5" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "6" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "7" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "8" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "92" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "98":
                self.main_procurement_category = "services"
        except ValueError:
            raise ValueError("main_procurement_category was not defined")

        try:
            buyer_country_data = get_value_from_country_csv(
                country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            buyer_country_object = {
                "scheme": buyer_country_data[2],
                "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                "description": buyer_country_data[1],
                "uri": buyer_country_data[3]
            }

            buyer_region_data = get_value_from_region_csv(
                region=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            buyer_region_object = {
                "scheme": buyer_region_data[2],
                "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                "description": buyer_region_data[1],
                "uri": buyer_region_data[3]
            }

            if GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":
                buyer_locality_data = get_value_from_locality_csv(
                    locality=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    region=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                    country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                    language=self.language
                )
                buyer_locality_object = {
                    "scheme": buyer_locality_data[2],
                    "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": buyer_locality_data[1],
                    "uri": buyer_locality_data[3]
                }
            else:
                buyer_locality_object = {
                    "scheme": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['scheme'],
                    "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality'][
                        'description']
                }
        except ValueError:
            raise ValueError("Check 'buyer.address.addressDetails' object")

        try:
            tender_classification_id = get_value_from_classification_cpv_dictionary_xls(
                GlobalClassCreateEi.payload['tender']['classification']['id'], self.language)
        except ValueError:
            raise ValueError("Check tender.classification.id")

        release['uri'] = f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateEi.ei_ocid}"
        release['version'] = "1.1"
        release['extensions'] = self.extensions

        release['publisher']['name'] = self.publisher_name
        release['publisher']['uri'] = self.publisher_uri
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = GlobalClassCreateEi.feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = GlobalClassCreateEi.ei_ocid
        release['releases'][0]['id'] = f"{GlobalClassCreateEi.ei_ocid}-{release_id[29:42]}"
        release['releases'][0]['date'] = GlobalClassCreateEi.feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "compiled"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = GlobalClassCreateEi.payload['tender']['title']
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "empty"
        release['releases'][0]['tender']['mainProcurementCategory'] = self.main_procurement_category
        release['releases'][0]['tender']['classification']['id'] = tender_classification_id[0]
        release['releases'][0]['tender']['classification']['description'] = tender_classification_id[1]
        release['releases'][0]['tender']['classification']['scheme'] = "CPV"
        release['releases'][0]['buyer']['id'] = \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}"
        release['releases'][0]['buyer']['name'] = GlobalClassCreateEi.payload['buyer']['name']
        release['releases'][0]['parties'][0]['id'] = \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = GlobalClassCreateEi.payload['buyer']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['legalName']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            GlobalClassCreateEi.payload['buyer']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = buyer_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = buyer_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = buyer_locality_object
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['email']
        release['releases'][0]['parties'][0]['roles'][0] = "buyer"
        release['releases'][0]['planning']['budget']['id'] = tender_classification_id[0]
        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            GlobalClassCreateEi.payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            GlobalClassCreateEi.payload['planning']['budget']['period']['endDate']
        return release
