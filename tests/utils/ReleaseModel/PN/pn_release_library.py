

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
    def pn_release_general_attributes():
        general_attributes = {
            "ocid": None,
            "id": None,
            "date": None,
            "tag": [None],
            "language": None,
            "initiationType": None,
            "hasPreviousNotice": None,
            "purposeOfNotice": {
                "isACallForCompetition": None
            }
        }
        return general_attributes

    @staticmethod
    def ms_release_general_attributes():
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
    def pn_release_tender_section():
        tender_section = {
            "id": None,
            "title": None,
            "description": None,
            "status": None,
            "statusDetails": None,
            "items": [],
            "lots": [],
            "lotGroups": [],
            "tenderPeriod": {
                "startDate": None
            },
            "hasEnquiries": None,
            "documents": None,
            "submissionMethod": [None],
            "submissionMethodDetails": None,
            "submissionMethodRationale": [None],
            "requiresElectronicCatalogue": None
        }
        return tender_section

    @staticmethod
    def ms_release_tender_section():
        tender_section = {
            "id": None,
            "title": None,
            "description": None,
            "status": None,
            "statusDetails": None,
            "value": {
                "amount": None,
                "currency": None
            },
            "procurementMethod": None,
            "procurementMethodDetails": None,
            "procurementMethodRationale": None,
            "mainProcurementCategory": None,
            "hasEnquiries": None,
            "eligibilityCriteria": None,
            "contractPeriod": {
                "startDate": None,
                "endDate": None
            },
            "procuringEntity": {
                "id": None,
                "name": None
            },
            "acceleratedProcedure": {
                "isAcceleratedProcedure": None
            },
            "classification": {
                "scheme": None,
                "id": None,
                "description": None
            },
            "designContest": {
                "serviceContractAward": None
            },
            "electronicWorkflows": {
                "useOrdering": None,
                "usePayment": None,
                "acceptInvoicing": None
            },
            "jointProcurement": {
                "isJointProcurement": None
            },
            "legalBasis": None,
            "procedureOutsourcing": {
                "procedureOutsourced": None
            },
            "procurementMethodAdditionalInfo": None,
            "dynamicPurchasingSystem": {
                "hasDynamicPurchasingSystem": None
            },
            "framework": {
                "isAFramework": None
            }
        }
        return tender_section

    @staticmethod
    def pn_release_tender_lot_group_option_to_combine():
        option_to_combine = {
            "optionToCombine": None
        }
        return option_to_combine

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
            "additionalIdentifiers": [],
            "contactPoint": {
                "name": None,
                "email": None,
                "telephone": None,
                "faxNumber": None,
                "url": None
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
    def ms_release_planning_section():
        planning_section = {
            "budget": {
                "description": None,
                "amount": {
                    "amount": None,
                    "currency": None
                },
                "isEuropeanUnionFunded": None,
                "budgetBreakdown": []
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

    @staticmethod
    def ms_release_planning_budget_budget_breakdown_obj():
        budget_breakdown = {
            "id": None,
            "description": None,
            "amount": {
                "amount": None,
                "currency": None
            },
            "period": {
                "startDate": None,
                "endDate": None
            },
            "sourceParty": {
                "id": None,
                "name": None
            },
            "europeanUnionFunding": {
                "projectIdentifier": None,
                "projectName": None,
                "uri": None
            }
        }
        return budget_breakdown

    @staticmethod
    def release_tender_lot_object():
        lot_object = {
            "id": None,
            "internalId": None,
            "title": None,
            "description": None,
            "status": None,
            "statusDetails": None,
            "value": {
                "amount": None,
                "currency": None
            },
            "recurrentProcurement": [{
                "isRecurrent": None
            }],
            "renewals": [{
                "hasRenewals": None
            }],
            "variants": [
                {
                    "hasVariants": None
                }],
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
                            "id": None,
                            "scheme": None,
                            "description": None,
                            "uri": None
                        },
                        "region": {
                            "id": None,
                            "scheme": None,
                            "description": None,
                            "uri": None
                        },
                        "locality": {
                            "id": None,
                            "scheme": None,
                            "description": None,
                            "uri": None
                        }
                    }
                },
                "description": None
            },
            "options": [
                {
                    "hasOptions": None
                }]

        }
        return lot_object

    @staticmethod
    def release_tender_item_object():
        item_object = {
            "id": None,
            "internalId": None,
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
            "quantity": None,
            "unit": {
                "id": None,
                "name": None
            },
            "relatedLot": None
        }
        return item_object

    @staticmethod
    def release_tender_document_object():
        document_object = {
            "documentType": None,
            "id": None,
            "title": None,
            "description": None,
            "url": None,
            "relatedLots": [None],
            "datePublished": None
        }
        return document_object
