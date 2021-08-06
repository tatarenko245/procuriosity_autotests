# тут лежать json Тимчасове рішення
import copy
import random
from allure_commons._allure import step

from tests.conftest import GlobalClassCreateEi
from tests.utils.date_class import Date
from tests.utils.data_of_enum import locality_scheme, typeOfBuyer, mainGeneralActivity, mainSectoralActivity, \
    cpv_goods_high_level, cpv_works_high_level, cpv_services_high_level, cpv_category
from tests.utils.functions import generate_items_array, \
    get_value_from_classification_cpv_dictionary_xls, generate_tender_classification_id


class EiPayload:
    def __init__(self):
        self.tender_classification_id = None
        category = random.choice(cpv_category)
        if category == "goods":
            self.tender_classification_id = random.choice(cpv_goods_high_level)
        elif category == "works":
            self.tender_classification_id = random.choice(cpv_works_high_level)
        elif category == "services":
            self.tender_classification_id = random.choice(cpv_services_high_level)
        self.ei_period = Date().expenditure_item_period()
        self.payload = {
            "tender": {
                "title": "create ei: tender.title",
                "description": "create ei: tender.description",
                "classification": {
                    "id": self.tender_classification_id
                },
                "items": [{
                    "id": "1",
                    "description": "create ei: tender.items[0].description",
                    "classification": {
                        "id": self.tender_classification_id
                    },
                    "additionalClassifications": [
                        {
                            "id": "AA12-4"
                        }
                    ],
                    "deliveryAddress": {
                        "streetAddress": "create ei: tender.items[0].deliveryAddress.streetAddress",
                        "postalCode": "create ei: tender.items[0].deliveryAddress.postalCode",
                        "addressDetails": {
                            "country": {
                                "id": "MD"

                            },
                            "region": {
                                "id": "1700000"

                            },
                            "locality": {
                                "id": "1701000",
                                "description": "create ei: tender.items[0].deliveryAddress.addressDetails."
                                               "locality.description",
                                "scheme": f'{random.choice(locality_scheme)}'
                            }

                        }
                    },
                    "quantity": 1,
                    "unit": {
                        "id": "10"

                    }
                }]
            },
            "planning": {
                "budget": {
                    "period": {
                        "startDate": self.ei_period[0],
                        "endDate": self.ei_period[1]
                    }
                },
                "rationale": "create ei: tender.items[0].deliveryAddress.postalCode"
            },
            "buyer": {
                "name": "create ei: buyer.name",
                "identifier": {
                    "id": "create ei: buyer.identifier.id",
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
                            "scheme": "CUATM",
                            "id": "1701000",
                            "description": "create ei: buyer.address.addressDetails.locality.description"
                        }
                    }
                },
                "additionalIdentifiers": [{
                    "id": "create ei buyer.additionalIdentifiers.id",
                    "scheme": "create ei buyer.additionalIdentifiers.scheme",
                    "legalName": "create ei buyer.additionalIdentifiers.description",
                    "uri": "create ei buyer.additionalIdentifiers.uri"
                }],
                "contactPoint": {
                    "name": "create ei: buyer.contactPoint.name",
                    "email": "create ei: buyer.contactPoint.email",
                    "telephone": "create ei: buyer.contactPoint.telephone",
                    "faxNumber": "create ei: buyer.contactPoint.faxNUmber",
                    "url": "create ei: buyer.contactPoint.url"
                },
                "details": {
                    "typeOfBuyer": f'{random.choice(typeOfBuyer)}',
                    "mainGeneralActivity": f'{random.choice(mainGeneralActivity)}',
                    "mainSectoralActivity": f'{random.choice(mainSectoralActivity)}'

                }
            }
        }

    def create_ei_obligatory_model_of_payload(self):
        del self.payload['tender']['description']
        del self.payload['tender']['items']
        del self.payload['planning']['rationale']
        del self.payload['buyer']['identifier']['uri']
        del self.payload['buyer']['address']['postalCode']
        del self.payload['buyer']['additionalIdentifiers']
        del self.payload['buyer']['contactPoint']['faxNumber']
        del self.payload['buyer']['contactPoint']['url']
        del self.payload['buyer']['details']
        return self.payload

    def create_ei_full_data_model_with_one_item_object(self):
        return self.payload

    def add_tender_items(self, quantity=2):
        items_array = generate_items_array(
            quantity_of_object=quantity,
            item_object=self.payload['tender']['items'][0],
            tender_classification_id=self.tender_classification_id
        )
        temp_tender_classification_id = generate_tender_classification_id(items_array)
        new_tender_classification = get_value_from_classification_cpv_dictionary_xls(
            cpv=temp_tender_classification_id,
            language=GlobalClassCreateEi.language
        )
        self.payload['tender']['items'] = items_array
        self.payload['tender']['classification']['id'] = new_tender_classification[0]
        return self.payload

    def update_ei_obligatory_model_of_payload(self):
        # Временно так как не пофиксили баг -> нужно раскомментировать del self.payload['tender']['classification']
        # и # del self.payload['buyer']
        # del self.payload['tender']['classification']
        # del self.payload['buyer']
        self.payload['tender']['title'] = "update ei: tender.title"
        return self.payload

    def update_ei_full_data_model_with_one_item_object(self):
        self.payload['tender']['title'] = "update ei: tender.title"
        self.payload['tender']['description'] = "update ei: tender.description"
        self.payload['tender']['items'][0]['description'] = "update ei: tender.items.description"
        self.payload['tender']['items'][0]['additionalClassifications'][0]['id'] = "AA08-2"
        self.payload['tender']['items'][0]['deliveryAddress']['streetAddress'] = \
            "update ei: tender.items[0].deliveryAddress.streetAddress"
        self.payload['tender']['items'][0]['deliveryAddress']['postalCode'] = \
            "update ei: tender.items[0].deliveryAddress.postalCode"
        self.payload['tender']['items'][0]['deliveryAddress']['addressDetails']['region']['id'] = "3400000"
        self.payload['tender']['items'][0]['deliveryAddress']['addressDetails']['locality']['id'] = "3401000"
        self.payload['tender']['items'][0]['quantity'] = 20
        self.payload['tender']['items'][0]['unit']['id'] = "20"
        self.payload['planning']['rationale'] = "update ei: planning.rationale"

        # Временно так как не пофиксили баг -> нужно раскомментировать del self.payload['tender']['classification']
        # и # del self.payload['buyer']
        # del self.payload['tender']['classification']
        # del self.payload['buyer']
        return self.payload
