# тут лежать json
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
        ei_period = Date().expenditure_item_period()
        category = random.choice(cpv_category)
        self.tender_classification_id = None
        if category == "goods":
            self.tender_classification_id = random.choice(cpv_goods_high_level)
        elif category == "works":
            self.tender_classification_id = random.choice(cpv_works_high_level)
        elif category == "services":
            self.tender_classification_id = random.choice(cpv_services_high_level)
        self.payload = {
            "tender": {
                "title": "EI_FULL_WORKS",
                "classification": {
                    "id": self.tender_classification_id
                },

            },
            "planning": {
                "budget": {

                    "period": {
                        "startDate": ei_period[0],
                        "endDate": ei_period[1]
                    }
                }
            },
            "buyer": {
                "name": "LLC Petrusenko",
                "identifier": {
                    "id": "380632074071",
                    "scheme": "MD-IDNO",
                    "legalName": "LLC Petrusenko"
                },
                "address": {
                    "streetAddress": "Zakrevskogo",
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
                            "description": "description"
                        }
                    }
                },
                "contactPoint": {
                    "name": "Petrusenko Svitlana",
                    "email": "svetik@gmail.com",
                    "telephone": "888999666"
                }
            }
        }

    def add_optionals_fields(self):

        self.payload['tender']['description'] = "create ei description"
        self.payload['tender']['items'] = [{
            "id": "1",
            "description": "item 1",
            "classification": {
                "id": self.tender_classification_id
            },
            "additionalClassifications": [
                {
                    "id": "AA12-4"
                }
            ],
            "deliveryAddress": {
                "streetAddress": "хрещатик",
                "postalCode": "02235",
                "addressDetails": {
                    "country": {
                        "id": "MD"

                    },
                    "region": {
                        "id": "1700000"

                    },
                    "locality": {
                        "id": "1701000",
                        "description": "ОПИСАНИЕ33pizza",
                        "scheme": f'{random.choice(locality_scheme)}'
                    }

                }
            },
            "quantity": 1,
            "unit": {
                "id": "10"

            }
        }]
        self.payload['planning']['rationale'] = "create ei planning.rationale"
        self.payload['buyer']['identifier']['uri'] = "create ei buyer.identifier.uri"
        self.payload['buyer']['address']['postalCode'] = "create ei buyer.address.postalCode"
        self.payload['buyer']['additionalIdentifiers'] = [{
            "id": "create ei buyer.additionalIdentifiers.id",
            "scheme": "create ei buyer.additionalIdentifiers.scheme",
            "legalName": "create ei buyer.additionalIdentifiers.description",
            "uri": "create ei buyer.additionalIdentifiers.uri"
        }]
        self.payload['buyer']['contactPoint']['faxNumber'] = "create ei buyer.contactPoint.faxNumber"
        self.payload['buyer']['contactPoint']['url'] = "create ei buyer.contactPoint.url"
        self.payload['buyer']['details'] = {
            "typeOfBuyer": f'{random.choice(typeOfBuyer)}',
            "mainGeneralActivity": f'{random.choice(mainGeneralActivity)}',
            "mainSectoralActivity": f'{random.choice(mainSectoralActivity)}'

        }
        return self.payload

    def obligatory_model_of_payload(self):
        return self.payload

    def add_tender_items(self, quantity=2):

        item_object = {
            "id": "1",
            "description": "item 1",
            "classification": {
                "id": "45100000-8"
            },
            "additionalClassifications": [
                {
                    "id": "AA12-4"
                }
            ],
            "deliveryAddress": {
                "streetAddress": "хрещатик",
                "postalCode": "02235",
                "addressDetails": {
                    "country": {
                        "id": "MD"

                    },
                    "region": {
                        "id": "1700000"

                    },
                    "locality": {
                        "id": "1701000",
                        "description": "ОПИСАНИЕ33pizza",
                        "scheme": f'{random.choice(locality_scheme)}'
                    }

                }
            },
            "quantity": 1,
            "unit": {
                "id": "10"

            }
        }
        items_array = generate_items_array(
            quantity_of_object=quantity,
            item_object=item_object,
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

    def add_buyer_details(self):

        buyer_details = {
            "typeOfBuyer": f'{random.choice(typeOfBuyer)}',
            "mainGeneralActivity": f'{random.choice(mainGeneralActivity)}',
            "mainSectoralActivity": f'{random.choice(mainSectoralActivity)}'

        }
        self.payload['buyer']['details'] = buyer_details
        return self.payload

