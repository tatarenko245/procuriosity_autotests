class PayloadLibrary:
    @staticmethod
    def payload():
        payload = {
            "tender": {
                "procuringEntity": {
                    "name": str,
                    "identifier": {
                        "id": str,
                        "scheme": str,
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
            },
            "planning": {
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
            },
            "buyer": {
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
        }

    @staticmethod
    def additional_identifiers_object():
        additional_identifiers = {
            "id": None,
            "scheme": None,
            "legalName": None,
            "uri": None
        }
        return additional_identifiers
