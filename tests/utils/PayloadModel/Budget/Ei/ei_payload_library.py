class PayloadLibrary:
    @staticmethod
    def tender_object():
        tender_object = {
            "title": None,
            "description": None,
            "classification": {
                "id": None
            },
            "items": None
        }
        return tender_object

    @staticmethod
    def tender_item_object():
        item_object = {
            "id": "1",
            "description": None,
            "classification": {
                "id": None
            },
            "additionalClassifications": None,
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
                        "scheme": None,
                        "uri": None
                    }
                }
            },
            "quantity": None,
            "unit": {
                "id": None
            }
        }
        return item_object

    @staticmethod
    def tender_item_additional_classifications():
        additional_classifications = {
            "id": None
        }
        return additional_classifications

    @staticmethod
    def planning_object():
        planning_obj = {
            "budget": {
                "period": {
                    "startDate": None,
                    "endDate": None
                }
            },
            "rationale": None
        }
        return planning_obj

    @staticmethod
    def buyer_object():
        buyer_obj = {
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
        return buyer_obj

    @staticmethod
    def buyer_additional_identifiers_object():
        additional_identifiers = {
            "id": None,
            "scheme": None,
            "legalName": None,
            "uri": None
        }
        return additional_identifiers
