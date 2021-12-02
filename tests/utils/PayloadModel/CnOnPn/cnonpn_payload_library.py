class PayloadLibrary:
    @staticmethod
    def planning_object():
        planning_object = {
            "rationale": None,
            "budget": {
                "description": None
            }
        }
        return planning_object

    @staticmethod
    def tender_object():
        tender_object = {
            "procurementMethodRationale": None,
            "procurementMethodAdditionalInfo": None,
            "tenderPeriod":
                {
                    "endDate": None
                },
            "enquiryPeriod":
                {
                    "endDate": None
                },
            "procurementMethodModalities":
                [
                    "electronicAuction"
                ],
            "electronicAuctions":
                {
                    "details": []
                },
            "procuringEntity":
                {
                    "id": None,
                    "persones": []

                },
            "criteria": [],
            "conversions": [],
            "lots": [],
            "items": [],
            "documents": []
        }
        return tender_object

    @staticmethod
    def tender_conversion_coefficient_object():
        coefficient_object = {
            "id": None,
            "value": None,
            "coefficient": None
        }
        return coefficient_object

    @staticmethod
    def tender_conversion_object():
        conversion_object = {
            "id": None,
            "relatesTo": None,
            "relatedItem": None,
            "rationale": None,
            "description": None,
            "coefficients": []
        }
        return conversion_object

    @staticmethod
    def tender_criteria_object():
        criteria_object = {
            "id": None,
            "title": None,
            "classification": {
                "id": None,
                "scheme": None
            },
            "description": None,
            "relatesTo": None,
            "relatedItem": None,
            "requirementGroups": []
        }
        return criteria_object

    @staticmethod
    def tender_criteria_requirement_groups_requirements_eligible_evidences_object():
        eligible_evidences_object = {
            "id": None,
            "title": None,
            "description": None,
            "type": None,
            "relatedDocument": {
                "id": None
            }
        }
        return eligible_evidences_object

    @staticmethod
    def tender_criteria_requirement_groups_requirements_object():
        requirement_object = {
            "id": None,
            "title": None,
            "dataType": None,
            "expectedValue": None,
            "minValue": None,
            "maxValue": None,
            "period": {
                "startDate": None,
                "endDate": None
            },
            "eligibleEvidences": []
        }
        return requirement_object

    @staticmethod
    def tender_criteria_requirement_groups_object():
        requirement_group_object = {
            "id": None,
            "description": None,
            "requirements": []
        }
        return requirement_group_object

    @staticmethod
    def tender_procuring_entity_persones():
        persones_object = {
            "title": None,
            "name": None,
            "identifier": {
                "scheme": None,
                "id": None,
                "uri": None
            },
            "businessFunctions": []
        }
        return persones_object

    @staticmethod
    def tender_procuring_entity_persones_business_functions_object():
        business_function_object = {
            "id": None,
            "type": None,
            "jobTitle": None,
            "period": {
                "startDate": None
            },
            "documents": []
        }
        return business_function_object

    @staticmethod
    def tender_electronic_auctions_details_object():
        details_object = {
            "id": None,
            "relatedLot": None,
            "electronicAuctionModalities": []
        }
        return details_object

    @staticmethod
    def tender_electronic_auctions_details_electronic_auction_modalities_object():
        electronic_auction_modalities_object = {
            "eligibleMinimumDifference": {
                "amount": None,
                "currency": None
            }
        }
        return electronic_auction_modalities_object

    @staticmethod
    def tender_lots_option_object():
        option_object = {
            "description": None,
            "period": {
                "durationInDays": None,
                "startDate": None,
                "endDate": None,
                "maxExtentDate": None
            }
        }
        return option_object

    @staticmethod
    def tender_lots_recurrence_dates_object():
        date_object = {
            "startDate": None
        }
        return date_object

    @staticmethod
    def tender_lots_object():
        lot_object = {
            "id": None,
            "internalId": None,
            "title": None,
            "description": None,
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
                "description": None
            },
            "hasOptions": None,
            "options": [],
            "hasRecurrence": None,
            "recurrence": {
                "dates": [],
                "description": None
            },
            "hasRenewal": None,
            "renewal": {
                "description": None,
                "minimumRenewals": None,
                "maximumRenewals": None,
                "period": {
                    "durationInDays": None,
                    "startDate": None,
                    "endDate": None,
                    "maxExtentDate": None
                }
            }
        }
        return lot_object

    @staticmethod
    def tender_item_object():
        item_object = {
            "id": None,
            "internalId": None,
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
            "description": None,
            "relatedLot": None
        }
        return item_object

    @staticmethod
    def tender_item_additional_classifications_object():
        additional_classifications_object = {
            "id": None,
            "scheme": None,
            "description": None
        }
        return additional_classifications_object

    @staticmethod
    def tender_document_object():
        document_object = {
            "documentType": None,
            "id": None,
            "title": None,
            "description": None,
            "relatedLots": []
        }
        return document_object

    @staticmethod
    def tender_procuring_entity_persones_business_document_object():
        document_object = {
            "documentType": None,
            "id": None,
            "title": None,
            "description": None
        }
        return document_object

    @staticmethod
    def planning_budget_budget_breakdown_object():
        budget_breakdown = {
            "id": None,
            "amount": {
                "amount": None,
                "currency": None
            }
        }
        return budget_breakdown

    @staticmethod
    def buyer_additional_identifiers_object():
        additional_identifiers = {
            "id": None
        }
        return additional_identifiers
