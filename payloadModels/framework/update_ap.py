update_ap = {
    "tender": {
        "title": "tender title upd",
        "description": "tender description upd",
        "procurementMethodRationale": "tender.procurementMethodRationale upd",
        "value": {
            "currency": "EUR"
        },
        "tenderPeriod": {
            "startDate": "2020-09-01T11:07:00Z"
        },
        "lots": [
            {
                "id": "1",
                ".internalId": "22",
                "title": "lots.titleNew",
                "description": "lots.description",
                "placeOfPerformance": {
                    "address": {
                        ".streetAddress": "street",
                        ".postalCode": "code",
                        "addressDetails": {
                            "country": {
                                "id": "MD"
                            },
                            "region": {
                                "id": "1000000"
                            },
                            "locality": {
                                "id": "1001001",
                                "scheme": "CUATM",
                                "description": "description"
                            }
                        }
                    }
                }
            },
              {
                "id": "2",
                ".internalId": "22",
                "title": "lots.titleNew",
                "description": "lots.description",
                "placeOfPerformance": {
                    "address": {
                        ".streetAddress": "street",
                        ".postalCode": "code",
                        "addressDetails": {
                            "country": {
                                "id": "MD"
                            },
                            "region": {
                                "id": "1000000"
                            },
                            "locality": {
                                "id": "1001001",
                                "scheme": "CUATM",
                                "description": "description"
                            }
                        }
                    }
                }
            }
        ],
        "items": [
            {
                "id": "3",
                "internalId": "123",
                "classification": {
                    "id": "50100000-6"
                },
                "additionalClassifications": [
                    {
                        "id": "TA30-9"
                    }
                ],
                "quantity": 1,
                "unit": {
                    "id": "10"
                },
                "description": "itemdescription.",
                "relatedLot": "1",
                "deliveryAddress": {
                    "streetAddress": "string",
                    "postalCode": "code",
                    "addressDetails": {
                        "country": {
                            "id": "MD"
                        },
                        "region": {
                            "id": "1000000"
                        },
                        "locality": {
                            "id": "string",
                            "description": "string",
                            "scheme": "string"
                        }
                    }
                }
            }
        ],
        "documents": [
            {
                "documentType": "evaluationCriteria",
                "id": "create AP: tender.documents.id",
                "title": "document title upd",
                "description": "document description upd",
                "relatedLots": [
                    "1"
                ]
            },
             {
                "documentType": "evaluationCriteria",
                "id": "new documents id",
                "title": "document title",
                "description": "document description",
                "relatedLots": [
                    "1"
                ]
            }
        ]
    }
}