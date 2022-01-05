class PayloadLibrary:
    @staticmethod
    def enquiry_object():
        enquiry_object = {
            "enquiry": {
                "author": {
                    "name": None,
                    "identifier": {
                        "scheme": None,
                        "id": None,
                        "legalName": None,
                        "uri": None
                    },
                    "additionalIdentifiers": [None],
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
                    "details": {
                        "scale": None
                    },
                    "contactPoint": {
                        "name": None,
                        "email": None,
                        "telephone": None,
                        "faxNumber": None,
                        "url": None
                    }
                },
                "title": None,
                "description": None,
                "relatedLot": None
            }
        }
        return enquiry_object

    @staticmethod
    def enquiry_author_additional_identifiers_object():
        additional_identifier = {
            "scheme": None,
            "id": None,
            "legalName": None,
            "uri": None
        }
        return additional_identifier
