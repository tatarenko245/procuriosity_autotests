import random
from tests.utils.data_of_enum import locality_scheme, scale


class EnquiryPreparePayload:
    @staticmethod
    def create_enquiry_obligatory_data_model():
        payload = {
            "enquiry": {
                "author": {
                    "name": "create enquiry: enquiry.author.name",
                    "identifier": {
                        "scheme": "MD-IDNO",
                        "id": "create enquiry: enquiry.author.identifier.id",
                        "legalName": "create enquiry: enquiry.author.identifier.legalName"
                    },
                    "address": {
                        "streetAddress": "create enquiry: enquiry.author.address.streetAddress",
                        "addressDetails": {
                            "country": {
                                "id": "MD"
                            },
                            "region": {
                                "id": "1700000",
                            },
                            "locality": {
                                "scheme": random.choice(locality_scheme),
                                "id": "1701000",
                                "description":
                                    "create enquiry: enquiry.author.address.addressDetails.locality.description"
                            }
                        }
                    },
                    "details": {
                        "scale": random.choice(scale),
                    },
                    "contactPoint": {
                        "name": "create enquiry: enquiry.author.contactPoint.name",
                        "email": "create enquiry: enquiry.author.contactPoint.email",
                        "telephone": "create enquiry: enquiry.author.contactPoint.telephone"
                    }
                },
                "title": "create enquiry: enquiry.author.title",
                "description": "create enquiry: enquiry.author.description"
            }
        }
        return payload
