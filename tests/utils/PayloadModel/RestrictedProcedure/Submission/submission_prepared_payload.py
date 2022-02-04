import random
from tests.utils.data_of_enum import scale


class SubmissionPreparePayload:
    @staticmethod
    def create_submission_moldova_obligatory_data_model():
        payload = {
            "submission": {
                "candidates": [{
                    "name": "create submission: candidates.name 1",
                    "identifier": {
                        "id": "create submission: candidates.identifier.id 1",
                        "legalName": "create submission: candidates.identifier.legalName 1",
                        "scheme": "MD-IDNO"
                    },
                    "address": {
                        "streetAddress": "create submission: candidates.address.streetAddress 1",
                        "addressDetails": {
                            "country": {
                                "id": "MD",
                                "scheme": "ISO-ALPHA2",
                                "description":
                                    "create submission: candidates.address.addressDetails.country.description 1"
                            },
                            "region": {
                                "id": "1700000",
                                "scheme": "CUATM",
                                "description":
                                    "create submission: candidates.address.addressDetails.region.description 1"
                            },
                            "locality": {
                                "id": "1701000",
                                "scheme": "CUATM",
                                "description":
                                    "create submission: candidates.address.addressDetails.locality.description 1"
                            }
                        }
                    },
                    "contactPoint": {
                        "name": "create submission: candidates.contactPoint.name 1",
                        "telephone": "create submission: candidates.contactPoint.telephone 1",
                        "email": "create submission: candidates.contactPoint.email 1"
                    },
                    "details": {
                        "scale": random.choice(scale)
                    }
                },
                    {
                        "name": "create submission: candidates.name 2",
                        "identifier": {
                            "id": "create submission: candidates.identifier.id 2",
                            "legalName": "create submission: candidates.identifier.legalName 2",
                            "scheme": "MD-IDNO"
                        },
                        "address": {
                            "streetAddress": "create submission: candidates.address.streetAddress 2",
                            "addressDetails": {
                                "country": {
                                    "id": "MD",
                                    "scheme": "ISO-ALPHA2",
                                    "description":
                                        "create submission: candidates.address.addressDetails.country.description 2"
                                },
                                "region": {
                                    "id": "1700000",
                                    "scheme": "CUATM",
                                    "description":
                                        "create submission: candidates.address.addressDetails.region.description 2"
                                },
                                "locality": {
                                    "id": "1701000",
                                    "scheme": "CUATM",
                                    "description":
                                        "create submission: candidates.address.addressDetails.locality.description 2"
                                }
                            }
                        },
                        "contactPoint": {
                            "name": "create submission: candidates.contactPoint.name 2",
                            "telephone": "create submission: candidates.contactPoint.telephone 2",
                            "email": "create submission: candidates.contactPoint.email 2"
                        },
                        "details": {
                            "scale": random.choice(scale)
                        }
                    },
                    {
                        "name": "create submission: candidates.name 32",
                        "identifier": {
                            "id": "create submission: candidates.identifier.id 32",
                            "legalName": "create submission: candidates.identifier.legalName 32",
                            "scheme": "MD-IDNO"
                        },
                        "address": {
                            "streetAddress": "create submission: candidates.address.streetAddress 32",
                            "addressDetails": {
                                "country": {
                                    "id": "MD",
                                    "scheme": "ISO-ALPHA2",
                                    "description":
                                        "create submission: candidates.address.addressDetails.country.description 2"
                                },
                                "region": {
                                    "id": "1700000",
                                    "scheme": "CUATM",
                                    "description":
                                        "create submission: candidates.address.addressDetails.region.description 2"
                                },
                                "locality": {
                                    "id": "1701000",
                                    "scheme": "CUATM",
                                    "description":
                                        "create submission: candidates.address.addressDetails.locality.description 2"
                                }
                            }
                        },
                        "contactPoint": {
                            "name": "create submission: candidates.contactPoint.name 32",
                            "telephone": "create submission: candidates.contactPoint.telephone 32",
                            "email": "create submission: candidates.contactPoint.email 32"
                        },
                        "details": {
                            "scale": random.choice(scale)
                        }
                    }
                ]
            }
        }
        return payload

    @staticmethod
    def create_submission_belarus_obligatory_data_model():
        payload = {
            "submission": {
                "candidates": [{
                    "name": "create submission: candidates.name 3",
                    "identifier": {
                        "id": "create submission: candidates.identifier.id 3",
                        "legalName": "create submission: candidates.identifier.legalName 3",
                        "scheme": "BY-ADR"
                    },
                    "address": {
                        "streetAddress": "create submission: candidates.address.streetAddress 3",
                        "addressDetails": {
                            "country": {
                                "id": "BY",
                                "scheme": "ISO-ALPHA2",
                                "description":
                                    "create submission: candidates.address.addressDetails.country.description 3"
                            },
                            "region": {
                                "id": "BY-HR",
                                "scheme": "iso-alpha2",
                                "description":
                                    "create submission: candidates.address.addressDetails.region.description 3"
                            },
                            "locality": {
                                "id": "unknown",
                                "scheme": "other",
                                "description":
                                    "create submission: candidates.address.addressDetails.locality.description 3"
                            }
                        }
                    },
                    "contactPoint": {
                        "name": "create submission: candidates.contactPoint.name 3",
                        "telephone": "create submission: candidates.contactPoint.telephone 3",
                        "email": "create submission: candidates.contactPoint.email 3"
                    },
                    "details": {
                        "scale": random.choice(scale)
                    }
                }]
            }
        }
        return payload
