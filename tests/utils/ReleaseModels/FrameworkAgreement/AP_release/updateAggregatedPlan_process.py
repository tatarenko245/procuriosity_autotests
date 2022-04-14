"""Prepare the expected releases of the update aggregated plan process, framework agreement procedures."""
import copy

from tests.utils.functions_collection.functions import get_value_from_country_csv, \
    get_value_from_region_csv, get_value_from_locality_csv, is_it_uuid, get_value_from_cpvs_dictionary_csv, \
    get_value_from_cpv_dictionary_xls, get_value_from_classification_unit_dictionary_csv


class UpdateAggregatedPlanRelease:
    """This class creates instance of release."""

    def __init__(self, language, ap_payload, actual_ap_release, actual_ms_release, tenderClassificationId):

        self.__language = language
        self.__ap_payload = ap_payload
        self.__actual_ap_release = actual_ap_release
        self.__actual_ms_release = actual_ms_release
        self.__tenderClassificationId = tenderClassificationId

        self.__expected_lots_array = [
            {
                "id": "",
                "internalId": "",
                "title": "",
                "description": "",
                "status": "planning",
                "statusDetails": "empty",
                "placeOfPerformance": {
                    "address": {
                        "streetAddress": "",
                        "postalCode": "",
                        "addressDetails": {
                            "country": {
                                "scheme": "",
                                "id": "",
                                "description": "",
                                "uri": ""
                            },
                            "region": {
                                "scheme": "",
                                "id": "",
                                "description": "",
                                "uri": ""
                            },
                            "locality": {
                                "scheme": "",
                                "id": "",
                                "description": "",
                                "uri": ""
                            }
                        }
                    }
                }
            }
        ]

        self.__expected_items_array = [
            {
                "id": "",
                "internalId": "",
                "description": "",
                "classification": {
                    "scheme": "",
                    "id": "",
                    "description": ""
                },
                "additionalClassifications": [
                    {
                        "scheme": "",
                        "id": "",
                        "description": ""
                    }
                ],
                "quantity": "",
                "unit": {
                    "name": "",
                    "id": ""
                },
                "relatedLot": "",
                "deliveryAddress": {
                    "streetAddress": "",
                    "postalCode": "",
                    "addressDetails": {
                        "country": {
                            "scheme": "",
                            "id": "",
                            "description": "",
                            "uri": ""
                        },
                        "region": {
                            "scheme": "",
                            "id": "",
                            "description": "",
                            "uri": ""
                        },
                        "locality": {
                            "scheme": "",
                            "id": "",
                            "description": "",
                            "uri": ""
                        }
                    }
                }
            }
        ]

    def build_expected_lots_array(self):
        """Build expected lots array."""

        new_lots_array = list()

        for q_0 in range(len(self.__ap_payload['tender']['lots'])):
            new_lots_array.append(copy.deepcopy(self.__expected_lots_array[0]))

            # Enrich or delete optional fields:
            if "internalId" in self.__ap_payload['tender']['lots'][q_0]:
                new_lots_array[q_0]['internalId'] = self.__ap_payload['tender']['lots'][q_0]['internalId']
            else:
                del new_lots_array[q_0]['internalId']

            if "placeOfPerformance" in self.__ap_payload['tender']['lots'][q_0]:
                if "postalCode" in self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address']:

                    new_lots_array[q_0]['placeOfPerformance']['address']['postalCode'] = \
                        self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address']['postalCode']
                else:
                    del new_lots_array[q_0]['placeOfPerformance']['address']['postalCode']

                if "streetAddress" in self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address']:

                    new_lots_array[q_0]['placeOfPerformance']['address']['streetAddress'] = \
                        self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address']['streetAddress']
                else:
                    del new_lots_array[q_0]['placeOfPerformance']['address']['postalCode']

                try:
                    """
                    "Prepare releases[0].tender.lots[*].placeOfPerformance.address.addressDetails object".
                    """
                    lot_country_data = get_value_from_country_csv(
                        country=self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                            'addressDetails']['country']['id'],

                        language=self.__language
                    )
                    expected_lot_country_object = {
                        "scheme": lot_country_data[2],

                        "id": self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                            'addressDetails']['country']['id'],

                        "description": lot_country_data[1],
                        "uri": lot_country_data[3]
                    }

                    lot_region_data = get_value_from_region_csv(
                        region=self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                            'addressDetails']['region']['id'],

                        country=self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                            'addressDetails']['country']['id'],

                        language=self.__language
                    )
                    expected_lot_region_object = {
                        "scheme": lot_region_data[2],

                        "id": self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                            'addressDetails']['region']['id'],

                        "description": lot_region_data[1],
                        "uri": lot_region_data[3]
                    }

                    if "locality" in self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                            'addressDetails']:
                        if self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                'addressDetails']['locality']['scheme'] == "CUATM":

                            lot_locality_data = get_value_from_locality_csv(

                                locality=self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['locality']['id'],

                                region=self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['region']['id'],

                                country=self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['country']['id'],

                                language=self.__language
                            )
                            expected_lot_locality_object = {
                                "scheme": lot_locality_data[2],

                                "id": self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['locality']['id'],

                                "description": lot_locality_data[1],
                                "uri": lot_locality_data[3]
                            }
                        else:
                            expected_lot_locality_object = {
                                "scheme": self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['locality']['scheme'],

                                "id": self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails'][
                                    'locality']['id'],

                                "description": self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance'][
                                    'address']['addressDetails']['locality']['description'],

                                "uri": self.__ap_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['locality']['uri']
                            }
                        new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['locality'] = \
                            expected_lot_locality_object
                    else:
                        del new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['locality']

                    new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['country'] = \
                        expected_lot_country_object

                    new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['region'] = \
                        expected_lot_region_object

                except ValueError:
                    raise ValueError(
                        "Impossible to prepare the expected releases[0].tender.lots[*].placeOfPerformance.address."
                        "addressDetails object.")
            else:
                del new_lots_array[q_0]['placeOfPerformance']
            # Enrich required fields:
            is_permanent_lot_id_correct = is_it_uuid(
                self.__actual_ap_release['releases'][0]['tender']['lots'][q_0]['id'])

            if is_permanent_lot_id_correct is True:
                new_lots_array[q_0]['id'] = self.__actual_ap_release['releases'][0]['tender']['lots'][q_0]['id']
            else:
                raise ValueError(f"releases[0].tender.lots[{q_0}].id must be uuid.")

            new_lots_array[q_0]['title'] = self.__ap_payload['tender']['lots'][q_0]['title']
            new_lots_array[q_0]['description'] = self.__ap_payload['tender']['lots'][q_0]['description']

        final_lots_array = list()
        if len(self.__actual_ap_release['releases'][0]['tender']['lots']) == len(new_lots_array):
            for act in range(len(self.__actual_ap_release['releases'][0]['tender']['lots'])):
                for exp in range(len(new_lots_array)):

                    if new_lots_array[exp]['id'] == \
                            self.__actual_ap_release['releases'][0]['tender']['lots'][act]['id']:
                        final_lots_array.append(new_lots_array[exp])
        else:
            raise ValueError("Quantity of objects into actual ap release doesn't equal "
                             "quantity of objects into prepared lots array")

        self.__expected_lots_array = final_lots_array
        return self.__expected_lots_array

    def build_expected_items_array(self):
        """Build expected items array."""

        new_items_array = list()

        for q_0 in range(len(self.__ap_payload['tender']['items'])):
            new_items_array.append(copy.deepcopy(self.__expected_items_array[0]))

            # Enrich or delete optional fields:
            if "internalId" in self.__ap_payload['tender']['items'][q_0]:
                new_items_array[q_0]['internalId'] = self.__ap_payload['tender']['items'][q_0]['internalId']
            else:
                del new_items_array[q_0]['internalId']

            if "additionalClassifications" in self.__ap_payload['tender']['items'][q_0]:
                new_items_additionalClassifications_array = list()
                for q_1 in range(len(self.__ap_payload['tender']['items'][q_0]['additionalClassifications'])):
                    new_items_additionalClassifications_array.append(copy.deepcopy(
                        self.__expected_items_array[0]['additionalClassifications'][0]))

                    expected_cpvs_data = get_value_from_cpvs_dictionary_csv(
                        cpvs=self.__ap_payload['tender']['items'][q_0]['additionalClassifications'][q_1]['id'],
                        language=self.__language
                    )

                    new_items_additionalClassifications_array[q_1]['scheme'] = "CPVS"
                    new_items_additionalClassifications_array[q_1]['id'] = expected_cpvs_data[0]
                    new_items_additionalClassifications_array[q_1]['description'] = expected_cpvs_data[2]

                new_items_array[q_0]['additionalClassifications'] = new_items_additionalClassifications_array
            else:
                del new_items_array[q_0]['additionalClassifications']

            if "deliveryAddress" in self.__ap_payload['tender']['items'][q_0]:
                if "streetAddress" in self.__ap_payload['tender']['items'][q_0]['deliveryAddress']:

                    new_items_array[q_0]['deliveryAddress']['streetAddress'] = \
                        self.__ap_payload['tender']['items'][q_0]['deliveryAddress']['streetAddress']
                else:
                    del new_items_array[q_0]['deliveryAddress']['streetAddress']

                if "postalCode" in self.__ap_payload['tender']['items'][q_0]['deliveryAddress']:

                    new_items_array[q_0]['deliveryAddress']['postalCode'] = \
                        self.__ap_payload['tender']['items'][q_0]['deliveryAddress']['postalCode']
                else:
                    del new_items_array[q_0]['deliveryAddress']['postalCode']

                try:
                    """
                    "Prepare releases[0].tender.items[*].deliveryAddress.addressDetails object".
                    """
                    item_country_data = get_value_from_country_csv(
                        country=self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                            'addressDetails']['country']['id'],

                        language=self.__language
                    )
                    expected_item_country_object = {
                        "scheme": item_country_data[2],

                        "id": self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                            'addressDetails']['country']['id'],

                        "description": item_country_data[1],
                        "uri": item_country_data[3]
                    }

                    item_region_data = get_value_from_region_csv(
                        region=self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                            'addressDetails']['region']['id'],

                        country=self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                            'addressDetails']['country']['id'],

                        language=self.__language
                    )
                    expected_item_region_object = {
                        "scheme": item_region_data[2],

                        "id": self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                            'addressDetails']['region']['id'],

                        "description": item_region_data[1],
                        "uri": item_region_data[3]
                    }

                    if "locality" in self.__ap_payload['tender']['items'][q_0]['deliveryAddress']['addressDetails']:
                        if self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                                'addressDetails']['locality']['scheme'] == "CUATM":

                            item_locality_data = get_value_from_locality_csv(

                                locality=self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                                    'addressDetails']['locality']['id'],

                                region=self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                                    'addressDetails']['region']['id'],

                                country=self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                                    'addressDetails']['country']['id'],

                                language=self.__language
                            )
                            expected_item_locality_object = {
                                "scheme": item_locality_data[2],

                                "id": self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                                    'addressDetails']['locality']['id'],

                                "description": item_locality_data[1],
                                "uri": item_locality_data[3]
                            }
                        else:
                            expected_item_locality_object = {
                                "scheme": self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                                    'addressDetails']['locality']['scheme'],

                                "id": self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                                    'addressDetails']['locality']['id'],

                                "description": self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                                    'addressDetails']['locality']['description'],

                                "uri": self.__ap_payload['tender']['items'][q_0]['deliveryAddress'][
                                    'addressDetails']['locality']['uri']
                            }

                        new_items_array[q_0]['deliveryAddress']['addressDetails'][
                            'locality'] = expected_item_locality_object
                    else:
                        del new_items_array[q_0]['deliveryAddress']['addressDetails']['locality']

                    new_items_array[q_0]['deliveryAddress']['addressDetails']['country'] = expected_item_country_object

                    new_items_array[q_0]['deliveryAddress']['addressDetails']['region'] = expected_item_region_object
                except ValueError:
                    raise ValueError(
                        "Impossible to prepare the expected releases[0].tender.items[*].deliveryAddress."
                        "addressDetails object.")
            else:
                del new_items_array[q_0]['deliveryAddress']

            # Enrich required fields:
            is_permanent_item_id_correct = is_it_uuid(
                self.__actual_ap_release['releases'][0]['tender']['items'][q_0]['id'])

            if is_permanent_item_id_correct is True:
                new_items_array[q_0]['id'] = self.__actual_ap_release['releases'][0]['tender']['items'][q_0]['id']
            else:
                raise ValueError(f"releases[0].tender.items[{q_0}].id must be uuid.")

            new_items_array[q_0]['description'] = self.__ap_payload['tender']['items'][q_0]['description']

            expected_cpv_data = get_value_from_cpv_dictionary_xls(
                cpv=self.__ap_payload['tender']['items'][q_0]['classification']['id'],
                language=self.__language
            )

            new_items_array[q_0]['classification']['scheme'] = "CPV"
            new_items_array[q_0]['classification']['id'] = expected_cpv_data[0]
            new_items_array[q_0]['classification']['description'] = expected_cpv_data[1]
            new_items_array[q_0]['quantity'] = float(self.__ap_payload['tender']['items'][q_0]['quantity'])

            expected_unit_data = get_value_from_classification_unit_dictionary_csv(
                unit_id=self.__ap_payload['tender']['items'][q_0]['unit']['id'],
                language=self.__language
            )

            new_items_array[q_0]['unit']['id'] = expected_unit_data[0]
            new_items_array[q_0]['unit']['name'] = expected_unit_data[1]

            new_items_array[q_0]['relatedLot'] = \
                self.__actual_ap_release['releases'][0]['tender']['lots'][q_0]['id']

        final_items_array = list()
        if len(self.__actual_ap_release['releases'][0]['tender']['items']) == len(new_items_array):
            for act in range(len(self.__actual_ap_release['releases'][0]['tender']['items'])):
                for exp in range(len(new_items_array)):

                    if new_items_array[exp]['id'] == \
                            self.__actual_ap_release['releases'][0]['tender']['items'][act]['id']:
                        final_items_array.append(new_items_array[exp])
        else:
            raise ValueError("Quantity of objects into actual ap release doesn't equal "
                             "quantity of objects into prepared items array")

        self.__expected_items_array = final_items_array
        return self.__expected_items_array

    def build_expected_mainProcurementCategory(self):
        """Build expected mainProcurementCategory."""

        try:
            """
           Enrich mainProcurementCategory, depends on tender.classification.id.
           """
            if \
                    self.__tenderClassificationId[0:2] == "03" or \
                    self.__tenderClassificationId[0] == "1" or \
                    self.__tenderClassificationId[0] == "2" or \
                    self.__tenderClassificationId[0] == "3" or \
                    self.__tenderClassificationId[0:2] == "44" or \
                    self.__tenderClassificationId[0:2] == "48":
                expected_mainProcurementCategory = "goods"

            elif \
                    self.__tenderClassificationId[0:2] == "45":
                expected_mainProcurementCategory = "works"

            elif \
                    self.__tenderClassificationId[0] == "5" or \
                    self.__tenderClassificationId[0] == "6" or \
                    self.__tenderClassificationId[0] == "7" or \
                    self.__tenderClassificationId[0] == "8" or \
                    self.__tenderClassificationId[0:2] == "92" or \
                    self.__tenderClassificationId[0:2] == "98":
                expected_mainProcurementCategory = "services"

            else:
                raise ValueError("Check your classification.id")

        except KeyError:
            raise KeyError("Could not parse classification.id.")
        return expected_mainProcurementCategory
