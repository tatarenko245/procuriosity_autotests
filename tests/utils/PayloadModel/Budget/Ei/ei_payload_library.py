class PayloadLibrary:
    @staticmethod
    def payload_model():
        payload = {
            "tender": {
                "title": str,
                "description": str,
                "classification": {
                    "id": str
                },
                "items": list
            },
            "planning": {
                "budget": {
                    "period": {
                        "startDate": str,
                        "endDate": str
                    }
                },
                "rationale": str
            },
            "buyer": {
                "name": str,
                "identifier": {
                    "id": str,
                    "scheme": str,
                    "legalName": str,
                    "uri": str
                },
                "address": {
                    "streetAddress": str,
                    "postalCode": str,
                    "addressDetails": {
                        "country": {
                            "id": str
                        },
                        "region": {
                            "id": str
                        },
                        "locality": {
                            "scheme": str,
                            "id": str,
                            "description": str
                        }
                    }
                },
                "additionalIdentifiers": list,
                "contactPoint": {
                    "name": str,
                    "email": str,
                    "telephone": str,
                    "faxNumber": str,
                    "url": str
                },
                "details": {
                    "typeOfBuyer": str,
                    "mainGeneralActivity": str,
                    "mainSectoralActivity": str

                }
            }
        }

    @staticmethod
    def tender_items_object():
        items_object = {
            "id": str,
            "description": str,
            "classification": {
                "id": str
            },
            "additionalClassifications": list,
            "deliveryAddress": {
                "streetAddress": str,
                "postalCode": str,
                "addressDetails": {
                    "country": {
                        "id": str
                    },
                    "region": {
                        "id": str
                    },
                    "locality": {
                        "id": str,
                        "description": str,
                        "scheme": str,
                        "uri": str
                    }
                }
            },
            "quantity": float,
            "unit": {
                "id": str
            }
        }
        return items_object

    @staticmethod
    def tender_items_additional_classifications_object():
        additional_classifications = {
            "id": str
        }
        return additional_classifications

    @staticmethod
    def buyer_additional_identifiers_object():
        additional_identifiers = {
            "id": str,
            "scheme": str,
            "legalName": str,
            "uri": str
        }
        return additional_identifiers
