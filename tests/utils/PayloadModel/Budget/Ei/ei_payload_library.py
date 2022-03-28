class PayloadLibrary:
    @staticmethod
    def payload():
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
        return payload

    @staticmethod
    def tender_items_object():
        items = {
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
            "quantity": str,
            "unit": {
                "id": str
            }
        }
        return items

    @staticmethod
    def tender_items_additionalclassifications_object():
        additionalclassifications = {
            "id": str
        }
        return additionalclassifications

    @staticmethod
    def buyer_additionalidentifiers_object():
        additionalidentifiers = {
            "id": str,
            "scheme": str,
            "legalName": str,
            "uri": str
        }
        return additionalidentifiers
