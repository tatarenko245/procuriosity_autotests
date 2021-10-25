class ReleaseLibrary:
    @staticmethod
    def ev_release_parties_object():
        parties_object = {
            "id": None,
            "name": None,
            "identifier": {
                "scheme": None,
                "id": None,
                "legalName": None,
                "uri": None
            },
            "address": {
                "streetAddress": None,
                "postalCode": None,
                "addressDetails": {
                    "country": {
                        "scheme": None,
                        "id": None,
                        "description": None,
                        "uri": None
                    },
                    "region": {
                        "scheme": None,
                        "id": None,
                        "description": None,
                        "uri": None
                    },
                    "locality": {
                        "scheme": None,
                        "id": None,
                        "description": None,
                        "uri": None
                    }
                }
            },
            "additionalIdentifiers": [None],
            "contactPoint": {
                "name": None,
                "email": None,
                "telephone": None,
                "faxNumber": None,
                "url": None
            },
            "details": {
                "typeOfSupplier": None,
                "mainEconomicActivities": [None],
                "permits": [None],
                "bankAccounts": [None],
                "legalForm": {
                    "id": None,
                    "scheme": None,
                    "description": None,
                    "uri": None
                },
                "scale": None
            },
            "persones": [None]
        }
        return parties_object

    @staticmethod
    def ev_release_parties_additional_identifiers_object():
        additional_identifiers_object = {
            "scheme": "tenderers.additionalIdentifiers.scheme: 0.0",
            "id": "tenderers.additionalIdentifiers.id: 0.0",
            "uri": "tenderers.additionalIdentifiers.uri: 0.0"
        }
        return additional_identifiers_object

    @staticmethod
    def ev_release_parties_details_main_economic_activity_object():
        main_economic_activity_object = {
            "scheme": "tenderers.details.mainEconomicActivities.scheme': 1.0",
            "id": "tenderers.details.mainEconomicActivities.id': 1.0",
            "description": "tenderers.details.mainEconomicActivities.description': 1.0",
            "uri": "tenderers.details.mainEconomicActivities.uri': 1.0"
        }
        return main_economic_activity_object

    @staticmethod
    def ev_release_parties_details_permit_object():
        permit_object = {
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
        return permit_object

    @staticmethod
    def ev_release_parties_details_bank_account_object():
        bank_account_object = {
            "description": None,
            "bankName": None,
            "address": {
                "streetAddress": None,
                "postalCode": None,
                "addressDetails": {
                    "country": {
                        "scheme": None,
                        "id": "MD",
                        "description": None,
                        "uri": None
                    },
                    "region": {
                        "scheme": None,
                        "id": "MD",
                        "description": None,
                        "uri": None
                    },
                    "locality": {
                        "scheme": None,
                        "id": "MD",
                        "description": None,
                        "uri": None
                    }
                }
            },
            "identifier": {
                "id": None,
                "scheme": None
            },
            "accountIdentification": {
                "id": None,
                "scheme": None
            },
            "additionalAccountIdentifiers": [None]
        }
        return bank_account_object

    @staticmethod
    def ev_release_parties_details_bank_account_additional_account_identifier_object():
        additional_account_identifier_object = {
            "id": None,
            "scheme": None
        }
        return additional_account_identifier_object

    @staticmethod
    def ev_release_parties_person_object():
        person_object = {
            "id": None,
            "title": None,
            "name": None,
            "identifier": {
                "scheme": None,
                "id": None,
                "uri": None
            },
            "businessFunctions": [None]
        }
        return person_object

    @staticmethod
    def ev_release_parties_person_business_function_object():
        business_function_object = {
            "id": None,
            "type": None,
            "jobTitle": None,
            "period": {
                "startDate": None
            },
            "documents": [None]
        }
        return business_function_object

    @staticmethod
    def ev_release_parties_person_business_function_document_object():
        document_object = {
            "id": None,
            "documentType": None,
            "title": None,
            "description": None,
            "url": None,
            "datePublished": None
        }
        return document_object
