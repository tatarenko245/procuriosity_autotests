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
    def ev_release_general_attributes():
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
    def ev_release_tender_section():
        tender_section = {
            "id": None,
            "status": None,
            "statusDetails": None,
            "criteria": [None],
            "conversions": [None],
            "items": [None],
            "lots": [None],
            "lotGroups": [{
                "optionToCombine": None
            }],
            "tenderPeriod": {
                "startDate": None,
                "endDate": None
            },
            "enquiryPeriod": {
                "startDate": None,
                "endDate": None
            },
            "auctionPeriod": {
                "startDate": None
            },
            "hasEnquiries": None,
            "documents": [None],
            "awardCriteria": None,
            "awardCriteriaDetails": None,
            "submissionMethod": [None],
            "submissionMethodDetails": None,
            "submissionMethodRationale": [None],
            "requiresElectronicCatalogue": None,
            "procurementMethodModalities": [None],
            "electronicAuctions": {
                "details": None
            }
        }
        return tender_section

    @staticmethod
    def ev_release_tender_electronic_auctions_details():
        details = {
            "id": None,
            "relatedLot": None,
            "auctionPeriod": {
                "startDate": None
            },
            "electronicAuctionModalities": [None]
        }
        return details

    @staticmethod
    def ev_release_tender_electronic_auctions_details_electronic_auction_modalities():
        electronic_auction_modalities = {
            "url": None,
            "eligibleMinimumDifference": {
                "amount": None,
                "currency": None
            }
        }
        return electronic_auction_modalities

    @staticmethod
    def ev_release_tender_criteria_section():
        criteria_section = {
            "id": None,
            "title": None,
            "source": None,
            "description": None,
            "requirementGroups": [None],
            "relatesTo": None,
            "classification": {None}
        }
        return criteria_section

    @staticmethod
    def ev_release_tender_criteria_requirement_groups_object():
        requirement_groups = {
            "id": None,
            "description": None,
            "requirements": [None]
        }
        return requirement_groups

    @staticmethod
    def ev_release_tender_criteria_requirement_groups_requirements_object():
        requirements = {
            "id": None,
            "title": None,
            "dataType": None,
            "status": None,
            "datePublished": None,
            "period": None,
            "eligibleEvidences": [None],
            "expectedValue": None
        }
        return requirements

    @staticmethod
    def ev_release_tender_criteria_requirement_groups_requirements_eligible_evidences_object():
        eligible_evidences = {
            "id": None,
            "title": None,
            "type": None,
            "description": None,
            "relatedDocument": {
                "id": None
            }
        }
        return eligible_evidences

    @staticmethod
    def ev_release_tender_conversions_section():
        criteria_section = {
            "id": None,
            "relatesTo": None,
            "relatedItem": None,
            "rationale": None,
            "description": None,
            "coefficients": [None]
        }

        return criteria_section

    @staticmethod
    def ev_release_tender_conversions_coefficients_section():
        coefficients = {
            "id": None,
            "value": None,
            "coefficient": None
        }

        return coefficients

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
                "budgetBreakdown": None
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
            "hasOptions": None,
            "hasRecurrence": None,
            "hasRenewal": None

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
            "additionalClassifications": [None],
            "quantity": None,
            "unit": {
                "id": None,
                "name": None
            },
            "relatedLot": None
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
