import random
from tests.utils.data_of_enum import scale


class SubmissionPreparePayload:
    @staticmethod
    def create_submission_obligatory_data_model():
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
                }]
            }
        }
        return payload
