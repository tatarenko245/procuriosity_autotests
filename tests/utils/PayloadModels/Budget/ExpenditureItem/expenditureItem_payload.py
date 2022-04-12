import copy
import random

from tests.utils.functions_collection.functions import generate_items_array, get_locality_id_according_with_region_id
from tests.utils.data_of_enum import locality_scheme_tuple, typeOfBuyer_tuple, mainGeneralActivity_tuple, \
    mainSectoralActivity_tuple, region_id_tuple, cpvs_tuple, unit_id_tuple
from tests.utils.date_class import Date


class ExpenditureItemPayload:
    def __init__(self, buyer_id, tenderClassificationId):

        __ei_period = Date().expenditureItem_period()
        self.__tenderClassificationId = tenderClassificationId

        self.__payload = {
            "tender": {
                "title": "create ei: tender.title",
                "description": "create ei: tender.description",
                "classification": {
                    "id": self.__tenderClassificationId
                },
                "items": [
                    {
                        "id": "0",
                        "description": f"create ei: tender.items0.description",
                        "classification": {
                            "id": self.__tenderClassificationId
                        },
                        "additionalClassifications": [
                            {
                                "id": "AA12-4"
                            }
                        ],
                        "deliveryAddress": {
                            "streetAddress": "create ei: tender.items0.deliveryAddress.streetAddress",
                            "postalCode": "create ei: tender.items0.deliveryAddress.postalCode",
                            "addressDetails": {
                                "country": {
                                    "id": "MD"
                                },
                                "region": {
                                    "id": "3400000"
                                },
                                "locality": {
                                    "id": "3401000",
                                    "description":
                                        "create ei: tender.items0.deliveryAddress.addressDetails.locality.uri",
                                    "scheme": f"{random.choice(locality_scheme_tuple)}",
                                    "uri": "create ei: tender.items0.deliveryAddress.addressDetails.locality.uri"
                                }
                            }
                        },
                        "quantity": "10",
                        "unit": {
                            "id": "10"
                        }
                    }
                ]
            },
            "planning": {
                "budget": {
                    "period": {
                        "startDate": __ei_period[0],
                        "endDate": __ei_period[1]
                    }
                },
                "rationale": "create ei: planning.rationale"
            },
            "buyer": {
                "name": "create ei: buyer.name",
                "identifier": {
                    "id": f"{buyer_id}",
                    "scheme": "MD-IDNO",
                    "legalName": "create ei: buyer.identifier.legalName",
                    "uri": "create ei: buyer.identifier.uri"
                },
                "address": {
                    "streetAddress": "create ei: buyer.address.streetAddress",
                    "postalCode": "create ei: buyer.address.postalCode",
                    "addressDetails": {
                        "country": {
                            "id": "MD"
                        },
                        "region": {
                            "id": "1700000"
                        },
                        "locality": {
                            "scheme": f"{random.choice(locality_scheme_tuple)}",
                            "id": "1701000",
                            "description": "create ei: buyer.address.addressDetails.locality.description"
                        }
                    }
                },
                "additionalIdentifiers": [
                    {
                        "id": "create ei buyer.additionalIdentifiers0.id",
                        "scheme": "create ei buyer.additionalIdentifiers0.scheme",
                        "legalName": "create ei buyer.additionalIdentifiers0.legalName",
                        "uri": "create ei buyer.additionalIdentifiers0.uri"
                    }
                ],
                "contactPoint": {
                    "name": "create ei: buyer.contactPoint.name",
                    "email": "create ei: buyer.contactPoint.email",
                    "telephone": "create ei: buyer.contactPoint.telephone",
                    "faxNumber": "create ei: buyer.contactPoint.faxNumber",
                    "url": "create ei: buyer.contactPoint.url"
                },
                "details": {
                    "typeOfBuyer": f"{random.choice(typeOfBuyer_tuple)}",
                    "mainGeneralActivity": f"{random.choice(mainGeneralActivity_tuple)}",
                    "mainSectoralActivity": f"{random.choice(mainSectoralActivity_tuple)}"

                }
            }
        }

    def build_expenditure_item_payload(self):
        return self.__payload

    def get_tender_classification_id(self):
        return self.__tenderClassificationId

    def delete_optional_fields(self, *args, item_position=0, additionalClassification_position=0,
                               buyer_additionalIdentifiers_position=0):

        for a in args:
            if a == "tender.description":
                del self.__payload['tender']['description']

            elif a == "tender.items":
                del self.__payload['tender']['items']
            elif a == "tender.items.additionalClassifications":
                del self.__payload['tender']['items'][item_position]['additionalClassifications']
            elif a == f"tender.items.additionalClassifications[{additionalClassification_position}]":

                del self.__payload['tender']['items'][item_position][
                    'additionalClassifications'][additionalClassification_position]

            elif a == "tender.items.deliveryAddress.postalCode":
                del self.__payload['tender']['items'][item_position]['deliveryAddress']['postalCode']
            elif a == "tender.items.deliveryAddress.addressDetails.locality.uri":
                del self.__payload['tender']['items'][item_position]['deliveryAddress']['addressDetails']['locality'][
                    'uri']

            elif a == "planning.rationale":
                del self.__payload['planning']['rationale']

            elif a == "buyer.identifier.uri":
                del self.__payload['buyer']['identifier']['uri']
            elif a == "buyer.address.postalCode":
                del self.__payload['buyer']['address']['postalCode']
            elif a == "buyer.additionalIdentifiers":
                del self.__payload['buyer']['additionalIdentifiers']
            elif a == "buyer.additionalIdentifiers.uri":
                del self.__payload['buyer']['additionalIdentifiers'][buyer_additionalIdentifiers_position]['uri']
            elif a == "buyer.contactPoint.faxNumber":
                del self.__payload['buyer']['contactPoint']['faxNumber']
            elif a == "buyer.contactPoint.url":
                del self.__payload['buyer']['contactPoint']['url']
            elif a == "buyer.details":
                del self.__payload['buyer']['details']
            elif a == "buyer.details.typeOfBuyer":
                del self.__payload['buyer']['details']['typeOfBuyer']
            elif a == "buyer.details.mainGeneralActivity":
                del self.__payload['buyer']['details']['mainGeneralActivity']
            elif a == "buyer.details.mainSectoralActivity":
                del self.__payload['buyer']['details']['mainSectoralActivity']

            else:
                raise KeyError(f"Impossible to delete attribute by path {a}.")

    def customize_tender_items(self, quantity_of_items, quantity_of_items_additionalClassifications):
        """
        The max quantity of items must be 5, because it depends on cpvs_tuple from data_of_enum.
        """
        new_items_array = generate_items_array(
            quantity_of_object=quantity_of_items,
            item_object=copy.deepcopy(self.__payload['tender']['items'][0]),
            tender_classification_id=self.__tenderClassificationId
        )

        for q_0 in range(quantity_of_items):

            new_items_array[q_0]['description'] = f"create ei: tender.items{q_0}.description"

            new_items_array[q_0]['deliveryAddress']['streetAddress'] = \
                f"create ei: tender.items{q_0}.deliveryAddress.streetAddress"

            new_items_array[q_0]['deliveryAddress']['postalCode'] = \
                f"create ei: tender.items{q_0}.deliveryAddress.postalCode"

            new_items_array[q_0]['deliveryAddress']['addressDetails']['region']['id'] = \
                f"{random.choice(region_id_tuple)}"

            new_items_array[q_0]['deliveryAddress']['addressDetails']['locality']['id'] = \
                get_locality_id_according_with_region_id(
                    new_items_array[q_0]['deliveryAddress']['addressDetails']['region']['id'])

            new_items_array[q_0]['deliveryAddress']['addressDetails']['locality']['scheme'] = \
                f"{random.choice(locality_scheme_tuple)}"

            new_items_array[q_0]['deliveryAddress']['addressDetails']['locality']['description'] = \
                f"create ei: tender.items{q_0}.deliveryAddress.addressDetails.locality.description"

            new_items_array[q_0]['deliveryAddress']['addressDetails']['locality']['uri'] = \
                f"create ei: tender.items{q_0}.deliveryAddress.addressDetails.locality.uri"

            new_items_array[q_0]['unit']['id'] = f"{random.choice(unit_id_tuple)}"

            list_of_additionalclassification_id = list()
            for q_1 in range(quantity_of_items_additionalClassifications):
                new_items_array[q_0]['additionalClassifications'].append(
                    copy.deepcopy(self.__payload['tender']['items'][0]['additionalClassifications'][0]))

                while len(list_of_additionalclassification_id) < quantity_of_items_additionalClassifications:
                    additionalclassification_id = f"{random.choice(cpvs_tuple)}"
                    if additionalclassification_id not in list_of_additionalclassification_id:
                        list_of_additionalclassification_id.append(additionalclassification_id)

            for q_1 in range(quantity_of_items_additionalClassifications):

                new_items_array[q_0]['additionalClassifications'][q_1]['id'] = \
                    list_of_additionalclassification_id[q_1]

        self.__payload['tender']['items'] = new_items_array

    def customize_buyer_additionalidentifiers(self, quantity_of_buyer_additionalIdentifiers):
        new_additionalidentifiers_array = list()
        for q in range(quantity_of_buyer_additionalIdentifiers):
            new_additionalidentifiers_array.append(copy.deepcopy(self.__payload['buyer']['additionalIdentifiers'][0]))
            new_additionalidentifiers_array[q]['id'] = f"create ei: buyer.additionalIdentifiers{q}.id"
            new_additionalidentifiers_array[q]['scheme'] = f"create ei: buyer.additionalIdentifiers{q}.scheme"
            new_additionalidentifiers_array[q]['legalName'] = f"create ei: buyer.additionalIdentifiers{q}.legalName"
            new_additionalidentifiers_array[q]['uri'] = f"create ei: buyer.additionalIdentifiers{q}.uri"

        self.__payload['buyer']['additionalIdentifiers'] = new_additionalidentifiers_array

    def __del__(self):
        print(f"The instance of ExpenditureItemPayload class: {__name__} was deleted.")
