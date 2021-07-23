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

    def obligatory_model_of_payload(self):
        payload = copy.deepcopy(self.payload)
        return payload

    def add_tender_items(self, quantity=2):
        payload = copy.deepcopy(self.payload)
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
        payload['tender']['items'] = items_array
        payload['tender']['classification']['id'] = new_tender_classification[0]
        return payload

    def add_buyer_details(self):
        payload = copy.deepcopy(self.payload)
        buyer_details = {
            "typeOfBuyer": f'{random.choice(typeOfBuyer)}',
            "mainGeneralActivity": f'{random.choice(mainGeneralActivity)}',
            "mainSectoralActivity": f'{random.choice(mainSectoralActivity)}'

        }
        payload['buyer']['details'] = buyer_details
        return payload


class Payload:
    @staticmethod
    def for_create_fs_full_own_money_data_model():
        fs_period = Date().financial_source_period()
        with step('Create payload for FS'):
            json = {
                "planning": {
                    "budget": {
                        "id": "IBAN - 102030",
                        "description": "description",
                        "period": {
                            "startDate": fs_period[0],
                            "endDate": fs_period[1]
                        },
                        "amount": {
                            "amount": 2000.0,
                            "currency": "EUR"
                        },
                        "isEuropeanUnionFunded": True,
                        "europeanUnionFunding": {
                            "projectName": "Name of this project",
                            "projectIdentifier": "projectIdentifier",
                            "uri": "http://uriuri.th"
                        },
                        "project": "project",
                        "projectID": "projectID",
                        "uri": "http://uri.ur"
                    },
                    "rationale": "reason for the budget"
                },
                "tender": {
                    "procuringEntity": {
                        "name": "Procuring Entity Name",
                        "identifier": {
                            "id": "123456789000",
                            "scheme": "MD-IDNO",
                            "legalName": "Legal Name",
                            "uri": "http://454.to"
                        },
                        "additionalIdentifiers": [
                            {
                                "id": "additional identifier",
                                "scheme": "MD-K",
                                "legalName": "legalname",
                                "uri": "http://k.to"
                            }
                        ],
                        "address": {
                            "streetAddress": "street",
                            "postalCode": "785412",
                            "addressDetails": {
                                "country": {
                                    "id": "MD"
                                },
                                "region": {
                                    "id": "3400000"
                                },
                                "locality": {
                                    "scheme": "CUATM",
                                    "id": "3401000",
                                    "description": "ssf"
                                }
                            }
                        },
                        "contactPoint": {
                            "name": "contact person",
                            "email": "string@mail.ccc",
                            "telephone": "98-79-87",
                            "faxNumber": "78-56-55",
                            "url": "http://url.com"
                        }
                    }
                },
                "buyer": {
                    "name": "buyer's name",
                    "identifier": {
                        "id": "123654789000",
                        "scheme": "MD-IDNO",
                        "legalName": "legal Name",
                        "uri": "http://buyer.com"
                    },
                    "address": {
                        "streetAddress": "street address of buyer",
                        "postalCode": "02054",
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
                                "description": "description of locality"
                            }
                        }
                    },
                    "additionalIdentifiers": [
                        {
                            "id": "additional identifier",
                            "scheme": "scheme",
                            "legalName": "legal name",
                            "uri": "http://addtIdent.com"
                        }
                    ],
                    "contactPoint": {
                        "name": "contact point of buyer",
                        "email": "email.com",
                        "telephone": "32-22-23",
                        "faxNumber": "12-22-21",
                        "url": "http://url.com"
                    }
                }
            }
        return json
