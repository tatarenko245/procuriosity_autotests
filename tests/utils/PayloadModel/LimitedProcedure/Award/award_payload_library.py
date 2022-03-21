class PayloadLibrary:

    @staticmethod
    def create_award_object():
        award = {
            "award": {
                "internalId": str,
                "description": str,
                "value": {
                    "amount": str,
                    "currency": str
                },
                "suppliers": list,
                "documents": list
            }
        }
        return award

    @staticmethod
    def create_award_suppliers_object():
        suppliers = {
            "name": str,
            "identifier": {
                "id": str,
                "legalName": str,
                "scheme": str,
                "uri": str
            },
            "additionalIdentifiers": list,
            "address": {
                "streetAddress": str,
                "postalCode": str,
                "addressDetails": {
                    "country": {
                        "id": str,
                        "description": str,
                        "scheme": str
                    },
                    "region": {
                        "id": str,
                        "description": str,
                        "scheme": str
                    },
                    "locality": {
                        "id": str,
                        "description": str,
                        "scheme": str
                    }
                }
            },
            "contactPoint": {
                "name": str,
                "email": str,
                "telephone": str,
                "faxNumber": str,
                "url": str
            },
            "persones": list,
            "details": {
                "typeOfSupplier": str,
                "mainEconomicActivities": list,
                "scale": str,
                "permits": list,
                "bankAccounts": list,
                "legalForm": {
                    "scheme": str,
                    "id": str,
                    "description": str,
                    "uri": str

                }

            }
        }
        return suppliers

    @staticmethod
    def create_award_suppliers_additionalIdentifiers_object():
        additionalIdentifiers = {
            "id": str,
            "legalName": str,
            "scheme": str,
            "uri": str
        }
        return additionalIdentifiers

    @staticmethod
    def create_award_suppliers_persones_object():
        persones = {
            "title": str,
            "name": str,
            "identifier": {
                "scheme": str,
                "id": str,
                "uri": str
            },
            "businessFunctions": list

        }
        return persones

    @staticmethod
    def create_award_suppliers_persones_businessFunctions_object():
        businessFunctions = {
            "id": str,
            "type": str,
            "jobTitle": str,
            "period": {
                "startDate": str
            },
            "documents": list
        }
        return businessFunctions

    @staticmethod
    def create_award_suppliers_persones_businessFunctions_documents_object():
        documents = {
            "documentType": str,
            "id": str,
            "title": str,
            "description": str
        }
        return documents

    @staticmethod
    def create_award_suppliers_details_mainEconomicActivities_object():
        mainEconomicActivities = {
            "id": str,
            "scheme": str,
            "description": str,
            "uri": str
        }
        return mainEconomicActivities

    @staticmethod
    def create_award_suppliers_details_permits_object():
        permits = {
            "scheme": str,
            "id": str,
            "url": str,
            "permitDetails": {
                "issuedBy": {
                    "id": str,
                    "name": str
                },
                "issuedThought": {
                    "id": str,
                    "name": str
                },
                "validityPeriod": {
                    "startDate": str,
                    "endDate": str
                }
            }
        }
        return permits

    @staticmethod
    def create_award_suppliers_details_bankAccounts_object():
        bankAccounts = {
            "description": str,
            "bankName": str,
            "address": {
                "streetAddress": str,
                "postalCode": str,
                "addressDetails": {
                    "country": {
                        "id": str,
                        "description": str,
                        "scheme": str
                    },
                    "region": {
                        "id": str,
                        "description": str,
                        "scheme": str
                    },
                    "locality": {
                        "id": str,
                        "description": str,
                        "scheme": str
                    }
                }
            },
            "identifier": {
                "scheme": str,
                "id": str
            },
            "accountIdentification": {
                "scheme": str,
                "id": str
            },
            "additionalAccountIdentifiers": list
        }
        return bankAccounts

    @staticmethod
    def create_award_suppliers_details_bankAccounts_additionalAccountIdentifiers_object():
        additionalAccountIdentifiers = {
            "scheme": str,
            "id": str
        }
        return additionalAccountIdentifiers

    @staticmethod
    def create_award_documents_object():
        documents = {
            "id": str,
            "title": str,
            "description": str,
            "documentType": str
        }
        return documents

    @staticmethod
    def evaluate_award_object():
        award = {
            "award": {
                "statusDetails": str,
                "description": str,
                "documents": list
            }
        }
        return award

    @staticmethod
    def evaluate_award_documents_object():
        documents = {
            "id": str,
            "title": str,
            "description": str,
            "documentType": str,
            "relatedLots": list
        }
        return documents
