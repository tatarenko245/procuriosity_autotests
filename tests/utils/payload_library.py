class PayloadLibrary:
    def __init__(self, language='ro'):
        self.language = language

    def ei_tender_object(self):
        ei_tender_object = {
            "title": None,
            "description": None,
            "classification": {
                "id": None
            },
            "items": [{
                "id": "1",
                "description": None,
                "classification": {
                    "id": None
                },
                "additionalClassifications": [
                    {
                        "id": None
                    }
                ],
                "deliveryAddress": {
                    "streetAddress": None,
                    "postalCode": None,
                    "addressDetails": {
                        "country": {
                            "id": None
                        },
                        "region": {
                            "id": None
                        },
                        "locality": {
                            "id": None,
                            "description": None,
                            "scheme": None
                        }
                    }
                },
                "quantity": None,
                "unit": {
                    "id": None
                }
            }]
        }
        return ei_tender_object

    def ei_planning_obj(self):
        ei_planning_obj = {
            "budget": {
                "period": {
                    "startDate": None,
                    "endDate": None
                }
            },
            "rationale": None
        }

        return ei_planning_obj

    def ei_buyer_obj(self):
        ei_buyer_obj = {
            "name": None,
            "identifier": {
                "id": None,
                "scheme": None,
                "legalName": None,
                "uri": None
            },
            "address": {
                "streetAddress": None,
                "postalCode": None,
                "addressDetails": {
                    "country": {
                        "id": None
                    },
                    "region": {
                        "id": None
                    },
                    "locality": {
                        "scheme": None,
                        "id": None,
                        "description": None
                    }
                }
            },
            "additionalIdentifiers": [{
                "id": None,
                "scheme": None,
                "legalName": None,
                "uri": None
            }],
            "contactPoint": {
                "name": None,
                "email": None,
                "telephone": None,
                "faxNumber": None,
                "url": None
            },
            "details": {
                "typeOfBuyer": None,
                "mainGeneralActivity": None,
                "mainSectoralActivity": None

            }
        }
        return ei_buyer_obj
