class PayloadLibrary:
    @staticmethod
    def tender_object():
        tender_object = {
            "title": None,
            "description": None,
            "legalBasis": None,
            "procurementMethodRationale": None,
            "procurementMethodAdditionalInfo": None,
            "tenderPeriod":
                {
                    "startDate": None
                },
            "procuringEntity": {
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
                "additionalIdentifiers": None,
                "contactPoint":
                    {
                        "name": None,
                        "email": None,
                        "telephone": None,
                        "faxNumber": None,
                        "url": None
                    }},
            "lots": None,
            "items": None,
            "documents": None
        }
        return tender_object

    @staticmethod
    def tender_lots_object():
        lot_object = {
            "id": None,
            "internalId": None,
            "title": None,
            "description": None,
            "value": {
                "amount": None,
                "currency": None
            },
            "contractPeriod": {
                "startDate": None,
                "endDate": None
            },
            "placeOfPerformance": {
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
                "description": None
            }
        }
        return lot_object

    @staticmethod
    def tender_item_object():
        item_object = {
            "id": None,
            "internalId": None,
            "classification": {
                "id": None
            },
            "additionalClassifications": None,
            "quantity": None,
            "unit": {
                "id": None
            },
            "description": None,
            "relatedLot": None
        }
        return item_object

    @staticmethod
    def tender_item_additional_classifications_object():
        additional_classifications_object = {
            "id": None
        }
        return additional_classifications_object

    @staticmethod
    def tender_document_object():
        document_object = {
            "documentType": None,
            "id": None,
            "title": None,
            "description": None,
            "relatedLots": [None]
        }
        return document_object

    @staticmethod
    def planning_object():
        planning_object = {
            "rationale": None,
            "budget": {
                "description": None,
                "budgetBreakdown": None
            }
        }
        return planning_object

    @staticmethod
    def planning_budget_budget_breakdown_object():
        budget_breakdown = {
            "id": None,
            "amount": {
                "amount": None,
                "currency": None
            }
        }
        return budget_breakdown

    @staticmethod
    def buyer_additional_identifiers_object():
        additional_identifiers = {
            "id": None,
            "scheme": None,
            "legalName": None,
            "uri": None
        }
        return additional_identifiers
