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
            "additionalIdentifiers": [],
            "contactPoint": {
                "name": None,
                "email": None,
                "telephone": None,
                "faxNumber": None,
                "url": None
            },
            "details": {
                "typeOfSupplier": None,
                "mainEconomicActivities": [],
                "permits": [],
                "bankAccounts": [],
                "legalForm": {
                    "id": None,
                    "scheme": None,
                    "description": None,
                    "uri": None
                },
                "scale": None
            },
            "persones": [],
            "roles": []
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
            "additionalAccountIdentifiers": []
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
            "businessFunctions": []
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
            "documents": []
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

    @staticmethod
    def ev_release_bid_object():
        bid_object = {
            "details": []
        }
        return bid_object

    @staticmethod
    def ev_release_bid_details_object():
        details_object = {
            "id": None,
            "date": None,
            "status": None,
            "tenderers": [],
            "value": {
                "amount": None,
                "currency": None
            },
            "documents": [],
            "relatedLots": [],
            "requirementResponses": []
        }
        return details_object

    @staticmethod
    def ev_release_bid_details_tenderer_object():
        tenderer_object = {
            "id": None,
            "name": None
        }
        return tenderer_object

    @staticmethod
    def ev_release_bid_details_document_object():
        document_object = {
            "id": None,
            "documentType": None,
            "title": None,
            "description": None,
            "url": None,
            "datePublished": None,
            "relatedLots": []
        }
        return document_object

    @staticmethod
    def ev_release_bid_details_requirement_response_object():
        requirement_response_object = {
            "id": None,
            "value": None,
            "period": {
                "startDate": None,
                "endDate": None
            },
            "requirement": {
                "id": None
            },
            "relatedTenderer": {
                "id": None,
                "name": None
            },
            "evidences": []
        }
        return requirement_response_object

    @staticmethod
    def ev_release_bid_details_requirement_response_evidences_object():
        evidences_object = {
            "id": None,
            "title": None,
            "description": None,
            "relatedDocument": {
                "id": None
            }
        }
        return evidences_object

    @staticmethod
    def ev_release_unsuccessful_award_object():
        award_object = {
            "id": None,
            "title": None,
            "description": None,
            "status": None,
            "statusDetails": None,
            "date": None,
            "relatedLots": []
        }
        return award_object

    @staticmethod
    def ev_release_successful_award_object():
        award_object = {
            "id": None,
            "status": None,
            "statusDetails": None,
            "date": None,
            "value": {
                "amount": None,
                "currency": None
            },
            "suppliers": [],
            "relatedLots": [],
            "relatedBid": None,
            "weightedValue": {
                "amount": None,
                "currency": None
            }
        }
        return award_object

    @staticmethod
    def ev_release_successful_award_supplier_object():
        supplier_object = {
            "id": None,
            "name": None
        }
        return supplier_object
