class ReleaseLibrary:
    @staticmethod
    def np_release_parties_object():
        parties = {
            "id": str,
            "name": str,
            "identifier": {
                "scheme": str,
                "id": str,
                "legalName": str,
                "uri": str
            },
            "address": {
                "streetAddress": str,
                "postalCode": str,
                "addressDetails": {
                    "country": {
                        "scheme": str,
                        "id": str,
                        "description": str,
                        "uri": str
                    },
                    "region": {
                        "scheme": str,
                        "id": str,
                        "description": str,
                        "uri": str
                    },
                    "locality": {
                        "scheme": str,
                        "id": str,
                        "description": str,
                        "uri": str
                    }
                }
            },
            "additionalIdentifiers": list,
            "contactPoint": {
                "name": str,
                "email": str,
                "telephone": str,
                "faxNumber": str,
                "url": str
            },
            "details": {
                "typeOfSupplier": str,
                "mainEconomicActivities": list,
                "permits": list,
                "bankAccounts": list,
                "legalForm": {
                    "id": str,
                    "scheme": str,
                    "description": str,
                    "uri": str
                },
                "scale": str
            },
            "persones": list,
            "roles": list
        }
        return parties

    @staticmethod
    def np_release_parties_additionalIdentifiers_object():
        additionalIdentifiers = {
            "id": str,
            "legalName": str,
            "scheme": str,
            "uri": str
        }
        return additionalIdentifiers

    @staticmethod
    def np_release_parties_details_mainEconomicActivity_object():
        mainEconomicActivity = {
            "id": str,
            "scheme": str,
            "description": str,
            "uri": str
        }
        return mainEconomicActivity

    @staticmethod
    def np_release_parties_details_permits_object():
        permits = {
            "id": str,
            "scheme": str,
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
    def np_release_parties_details_bankAccounts_object():
        bankAccounts = {
            "description": str,
            "bankName": str,
            "address": {
                "streetAddress": str,
                "postalCode": str,
                "addressDetails": {
                    "country": {
                        "scheme": str,
                        "id": str,
                        "description": str,
                        "uri": str
                    },
                    "region": {
                        "scheme": str,
                        "id": str,
                        "description": str,
                        "uri": str
                    },
                    "locality": {
                        "scheme": str,
                        "id": str,
                        "description": str,
                        "uri": str
                    }
                }
            },
            "identifier": {
                "id": str,
                "scheme": str
            },
            "accountIdentification": {
                "id": str,
                "scheme": str
            },
            "additionalAccountIdentifiers": list
        }
        return bankAccounts

    @staticmethod
    def np_release_parties_details_bankAccounts_additionalAccountIdentifiers_object():
        additionalAccountIdentifiers = {
            "id": str,
            "scheme": str
        }
        return additionalAccountIdentifiers

    @staticmethod
    def np_release_parties_persones_object():
        persones = {
            "id": str,
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
    def np_release_parties_persones_businessFunctions_object():
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
    def np_release_parties_persones_businessFunctions_documents_object():
        documents = {
            "id": str,
            "documentType": str,
            "title": str,
            "description": str,
            "url": str,
            "datePublished": str
        }
        return documents

    @staticmethod
    def np_release_awards_object():
        awards = {
            "id": str,
            "internalId": str,
            "description": str,
            "status": str,
            "statusDetails": str,
            "date": str,
            "value": {
                "amount": float,
                "currency": str
            },
            "suppliers": list,
            "documents": list,
            "relatedLots": list
        }
        return awards

    @staticmethod
    def np_release_awards_suppliers_object():
        suppliers = {
            "id": str,
            "name": str
        }
        return suppliers

    @staticmethod
    def np_release_awards_documents_object():
        documents = {
            "id": str,
            "documentType": str,
            "title": str,
            "description": str,
            "url": str,
            "datePublished": str
        }
        return documents
