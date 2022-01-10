class ReleaseLibrary:
    @staticmethod
    def metadata_release():
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

    @staticmethod
    def release_general_attributes():
        general_attributes = {
            "ocid": None,
            "id": None,
            "date": None,
            "tag": [None],
            "language": None,
            "initiationType": None
        }
        return general_attributes

    @staticmethod
    def release_tender_section():
        tender_section = {
            "id": None,
            "title": None,
            "description": None,
            "status": None,
            "statusDetails": None,
            "items": [],
            "mainProcurementCategory": None,
            "classification": {
                "scheme": None,
                "id": None,
                "description": None
            }
        }
        return tender_section

    @staticmethod
    def release_tender_item_object():
        item_object = {
            "id": None,
            "description": None,
            "classification": {
                "id": None,
                "scheme": None,
                "description": None
            },
            "additionalClassifications": [],
            "quantity": None,
            "unit": {
                "id": None,
                "name": None
            },
            "deliveryAddress": {
                "streetAddress": None,
                "postalCode": None,
                "addressDetails": {
                    "country": {
                        "id": None,
                        "description": None,
                        "scheme": None,
                        "uri": None
                    },
                    "region": {
                        "id": None,
                        "description": None,
                        "scheme": None,
                        "uri": None
                    },
                    "locality": {
                        "id": None,
                        "description": None,
                        "scheme": None,
                        "uri": None
                    }
                }
            }
        }
        return item_object

    @staticmethod
    def release_tender_items_additional_classifications():
        additional_classifications = {
            "id": None,
            "scheme": None,
            "description": None
        }
        return additional_classifications

    @staticmethod
    def release_buyer_section():
        buyer_section = {
            "id": None,
            "name": None
        }
        return buyer_section

    @staticmethod
    def release_parties_section():
        parties_section = {
            "id": None,
            "name": None,
            "identifier": {
                "scheme": None,
                "id": None,
                "legalName": None,
                "uri": None
            },
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
            "additionalIdentifiers": None,
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
        }
        return parties_section

    @staticmethod
    def release_parties_additional_identifiers():
        additional_identifiers = {
            "id": None,
            "scheme": None,
            "legalName": None,
            "uri": None
        }
        return additional_identifiers

    @staticmethod
    def release_planning_section():
        planning_section = {
            "budget": {
                "id": None,
                "period": {
                    "startDate": None,
                    "endDate": None
                }
            },
            "rationale": None
        }
        return planning_section

    @staticmethod
    def release_related_processes_section():
        related_processes_section = {
            "id": None,
            "relationship": [None],
            "scheme": None,
            "identifier": None,
            "uri": None
        }
        return related_processes_section
