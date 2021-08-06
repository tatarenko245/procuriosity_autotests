class ReleaseLibrary:
    def metadata_release(self):
        metadata_release = {
            "uri": None,
            "version": None,
            "extensions": [
                None,
                None],
            "publisher": {
                "name": None,
                "uri": None
            },
            "license": None,
            "publicationPolicy": None,
            "publishedDate": None
        }
        return metadata_release

    def ei_release(self):
        ei_release = {

                "ocid": None,
                "id": None,
                "date": None,
                "tag": [None],
                "language": None,
                "initiationType": None,
                "tender": {
                    "id": None,
                    "title": None,
                    "description": None,
                    "status": None,
                    "statusDetails": None,
                    "mainProcurementCategory": None,
                    "classification": {
                        "scheme": None,
                        "id": None,
                        "description": None
                    },
                    "items": [{
                        "id": None,
                        "description": None,
                        "classification": {
                            "id": None,
                            "scheme": None,
                            "description": None
                        },
                        "additionalClassifications": [{
                            "id": None,
                            "scheme": None,
                            "description": None
                        }],
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
                },
                "buyer": {
                    "id": None,
                    "name": None
                },
                "parties": [{
                    "id": None,
                    "name": None,
                    "identifier": {
                        "scheme": None,
                        "id": None,
                        "legalName": None,
                        "uri": None
                    },
                    "additionalIdentifiers": [{
                        "id": None,
                        "scheme": None,
                        "legalName": None,
                        "uri": None
                    }],
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
                    },
                    "roles": [None]
                }],
                "planning": {
                    "budget": {
                        "id": None,
                        "period": {
                            "startDate": None,
                            "endDate": None
                        },
                        "amount": {
                            "amount": None,
                            "currency": None
                        }
                    },
                    "rationale": None
                },
                "relatedProcesses": [{
                    "id": None,
                    "relationship": [None],
                    "scheme": None,
                    "identifier": None,
                    "uri": None
                }]
            }
        return ei_release
