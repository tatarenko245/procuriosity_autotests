class PayloadLibrary:
    @staticmethod
    def bid_object():
        bid_object = {
            "value": {
                "amount": None,
                "currency": None
            },
            "requirementResponses": [None],
            "tenderers": [None],
            "relatedLots": [None],
            "documents": [None],
            "items": [None]

        }
        return bid_object

    @staticmethod
    def requirement_response():
        requirement_response_object = {
            "id": None,
            "value": None,
            "requirement": {
                "id": None
            },
            "relatedTenderer": {
                "name": None,
                "identifier": {
                    "id": None,
                    "scheme": None
                }
            },
            "evidences": [None],
            "period": {
                "startDate": None,
                "endDate": None
            }
        }
        return requirement_response_object

    @staticmethod
    def tenderers_object():
        tenderers = {
            "name": None,
            "identifier": {
                "id": None,
                "legalName": None,
                "scheme": None,
                "uri": None
            },
            "additionalIdentifiers": [None],
            "address": {
                "streetAddress": None,
                "postalCode": None,
                "addressDetails": {
                    "country": {
                        "id": None,
                        "description": None,
                        "scheme": None
                    },
                    "region": {
                        "id": None,
                        "description": None,
                        "scheme": None
                    },
                    "locality": {
                        "id": None,
                        "description": None,
                        "scheme": None
                    }
                }
            },
            "contactPoint": {
                "name": None,
                "email": None,
                "telephone": None,
                "faxNumber": None,
                "url": None
            },
            "persones": [None],
            "details": {
                "typeOfSupplier": None,
                "mainEconomicActivities": [None],
                "scale": None,
                "permits": [None],
                "bankAccounts": [None],
                "legalForm": {
                    "scheme": None,
                    "id": None,
                    "description": None,
                    "uri": None

                }
            }

        }
        return tenderers

    @staticmethod
    def additional_identifiers_object():
        additional_identifiers = {
            "id": None,
            "legalName": None,
            "scheme": None,
            "uri": None
        }
        return additional_identifiers

    @staticmethod
    def business_function_object():
        business_function = {
            "id": None,
            "type": None,
            "jobTitle": None,
            "period": {
                "startDate": None
            },
            "documents": None
        }
        return business_function

    @staticmethod
    def document_object():
        document = {
            "documentType": None,
            "id": None,
            "title": None,
            "description": None
        }
        return document

    @staticmethod
    def bank_account_object():
        bank_account = {
            "description": None,
            "bankName": None,
            "address": {
                "streetAddress": None,
                "postalCode": None,
                "addressDetails": {
                    "country": {
                        "id": None,
                        "description": None,
                        "scheme": None
                    },
                    "region": {
                        "id": None,
                        "description": None,
                        "scheme": None
                    },
                    "locality": {
                        "id": None,
                        "description": None,
                        "scheme": None
                    }
                },

            },
            "identifier": {
                "scheme": None,
                "id": None
            },
            "accountIdentification": {
                "scheme": None,
                "id": None
            },
            "additionalAccountIdentifiers": [None]
        }
        return bank_account

    @staticmethod
    def permit_object():
        permit = {
            "id": None,
            "scheme": None,
            "url": None,
            "permitDetails": {
                "issuedBy": {
                    "id": None,
                    "name": None
                },
                "issuedThought": {
                    "id": None,
                    "name": None
                },
                "validityPeriod": {
                    "startDate": None,
                    "endDate": None
                }
            }
        }
        return permit

    @staticmethod
    def main_economic_activities_object():
        main_economic_activities = {
            "id": None,
            "scheme": None,
            "description": None,
            "uri": None
        }
        return main_economic_activities

    @staticmethod
    def item_object():
        item = {
            "id": None,
            "unit": {
                "value": {
                    "amount": None,
                    "currency": None
                },
                "id": None
            }
        }
        return item

    @staticmethod
    def evidence_object():
        evidence = {
            "id": None,
            "title": None,
            "description": None,
            "relatedDocument": {
                "id": None
            }
        }
        return evidence

    @staticmethod
    def person_object():
        person = {
            "title": None,
            "name": None,
            "identifier": {
                "scheme": None,
                "id": None,
                "uri": None
            },
            "businessFunctions": None
        }
        return person

    @staticmethod
    def additional_account_identifier_object():
        additional_account_identifier = {
            "scheme": None,
            "id": None
        }
        return additional_account_identifier
