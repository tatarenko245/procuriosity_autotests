class PayloadLibrary:
    @staticmethod
    def tender_object():
        tender_object = {
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
                        }
                }
            }
        return tender_object

    @staticmethod
    def planning_object():
        planning_object = {
            "budget": {
                "id": None,
                "description": None,
                "period": {
                    "startDate": None,
                    "endDate": None
                },
                "amount": {
                    "amount": None,
                    "currency": None,
                },
                "isEuropeanUnionFunded": None,
                "europeanUnionFunding": {
                    "projectName": None,
                    "projectIdentifier": None,
                    "uri": None
                },
                "project": None,
                "projectID": None,
                "uri": None
            },
            "rationale": None
        }
        return planning_object

    @staticmethod
    def buyer_object():
        buyer_object = {
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
            }
        }
        return buyer_object

    @staticmethod
    def additional_identifiers_object():
        additional_identifiers = {
            "id": None,
            "scheme": None,
            "legalName": None,
            "uri": None
        }
        return additional_identifiers
