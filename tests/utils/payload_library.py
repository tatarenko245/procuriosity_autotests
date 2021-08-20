class PayloadLibrary:
    def __init__(self, language='ro'):
        self.language = language

    def tender_object(self):
        tender_object = {
            "title": None,
            "description": None,
            "legalBasis": None,
            "tenderPeriod": {
                "startDate": None
            },
            "classification": {
                "id": None
            },
            "lots": [{
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

            }],
            "items": [{
                "id": "1",
                "internalId": None,
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
        return tender_object

    def planning_obj(self):
        planning_obj = {
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
                "uri": None,
                "budgetBreakdown": []
            },
            "rationale": None
        }
        return planning_obj

    def planning_budget_budget_breakdown_obj(self):
        budget_breakdown = {
            "id": None,
            "amount": {
                "amount": None,
                "currency": None
            }
        }
        return budget_breakdown

    def buyer_obj(self):
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
        return buyer_obj

    def procuring_entity_obj(self):
        procuring_entity_obj = {
            "procuringEntity": {
                "name": None,
                "identifier":
                    {
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
                "additionalIdentifiers":
                    [{
                        "id": None,
                        "scheme": None,
                        "legalName": None,
                        "uri": None
                    }],
                "contactPoint":
                    {
                        "name": None,
                        "email": None,
                        "telephone": None,
                        "faxNumber": None,
                        "url": None
                    }
            }}
        return procuring_entity_obj
