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
            "initiationType": None,
            "hasPreviousNotice": None,
            "purposeOfNotice": {
                "isACallForCompetition": None
            }
        }
        return general_attributes

    @staticmethod
    def release_planning_section():
        planning_section = {
            "budget": {
                "id": None,
                "description": None,
                "period": {
                    "startDate": None,
                    "endDate": None
                },
                "amount": {
                    "amount": None,
                    "currency": None
                },
                "budgetBreakdown": [],
                "europeanUnionFunding": {
                    "projectIdentifier": None,
                    "projectName": None,
                    "uri": None
                },
                "isEuropeanUnionFunded": None,
                "verified": None,
                "sourceEntity": {
                    "id": None,
                    "name": None
                },
                "project": None,
                "projectID": None,
                "uri": None
            },
            "rationale": None
        }
        return planning_section

    @staticmethod
    def release_tender_section():
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
            "lotGroups": [{
                "optionToCombine": None
            }],
            "tenderPeriod": {
                "startDate": None
            },
            "hasEnquiries": None,
            "acceleratedProcedure": {
                "isAcceleratedProcedure": None
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
            "dynamicPurchasingSystem": {
                "hasDynamicPurchasingSystem": None
            },
            "framework": {
                "isAFramework": None
            },
            "eligibilityCriteria": None,
            "procuringEntity": {},
            "submissionMethod": [None],
            "submissionMethodDetails": None,
            "submissionMethodRationale": [None],
            "requiresElectronicCatalogue": None,
            "mainProcurementCategory": None,
            "classification": {
                "scheme": None,
                "id": None,
                "description": None
            },
            "lots": None,
            "items": None
        }
        return tender_section

    @staticmethod
    def ei_release_tender_item_object():
        ei_item_object = {
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
                "id": None,
                "name": None
            }
        }
        return ei_item_object

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
                "id": None,
                "name": None
            },
            "relatedLot": None
        }
        return item_object

    @staticmethod
    def release_buyer_section():
        buyer_section = {
            "id": None,
            "name": None
        }
        return buyer_section

    @staticmethod
    def release_procuring_entity_section():
        procuring_entity_section = {
            "id": None,
            "name": None
        }
        return procuring_entity_section

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
        }
        return parties_section

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
    def pn_stage_ms_release_planning_section():
        planning_section = {
            "budget": {
                "description": None,
                "amount": {
                    "amount": None,
                    "currency": None
                },
                "isEuropeanUnionFunded": None,
                "budgetBreakdown": None,
                "rationale": None
            }
        }
        return planning_section

    @staticmethod
    def release_planning_budget_budget_breakdown_obj():
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
