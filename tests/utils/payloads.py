# тут лежать json

import random
from allure_commons._allure import step

from tests.utils.date_class import Date
from tests.utils.data_of_enum import locality_scheme, typeOfBuyer, mainGeneralActivity, mainSectoralActivity


class Payload:
    @staticmethod
    def for_create_ei_full_data_model():
        ei_period = Date().expenditure_item_period()
        with step('Create payload for EI'):
            json = {
                "tender": {
                    "title": "EI_FULL_WORKS",
                    "description": "description of finansical sourse",
                    "classification": {
                        "id": "45100000-8"
                    },
                    "items": [
                        {
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
                    ]
                },
                "planning": {
                    "budget": {

                        "period": {
                            "startDate": ei_period[0],
                            "endDate": ei_period[1]
                        }
                    },
                    "rationale": "planning.rationale"
                },
                "buyer": {
                    "name": "LLC Petrusenko",
                    "identifier": {
                        "id": "380632074071",
                        "scheme": "MD-IDNO",
                        "legalName": "LLC Petrusenko",
                        "uri": "http://petrusenko.com/fop"
                    },
                    "address": {
                        "streetAddress": "Zakrevskogo",
                        "postalCode": "02217",
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
                    "additionalIdentifiers": [
                        {
                            "id": "string",
                            "scheme": "MD-IDNO",
                            "legalName": "380935103469",
                            "uri": "http://petrusenko.com/svetlana"
                        }
                    ],
                    "contactPoint": {
                        "name": "Petrusenko Svitlana",
                        "email": "svetik@gmail.com",
                        "telephone": "888999666",
                        "faxNumber": "5552233",
                        "url": "http://petrusenko.com/svetlana"
                    },
                    "details": {
                        "typeOfBuyer": f'{random.choice(typeOfBuyer)}',
                        "mainGeneralActivity": f'{random.choice(mainGeneralActivity)}',
                        "mainSectoralActivity": f'{random.choice(mainSectoralActivity)}'

                    }
                }
            }
        return json

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
