import copy
import random

from tests.utils.data_of_enum import locality_scheme


class FinancialSourcePayload:
    def __init__(self, ei_payload, currency):
        self.__currency = currency
        self.__payload = {
            "tender": {
                "procuringEntity": {
                    "name": "create fs: procuringEntity.name",
                    "identifier": {
                        "id": "create fs: procuringEntity.identifier.id",
                        "scheme": "MD-IDNO",
                        "legalName": "create fs: procuringEntity.identifier.legalName",
                        "uri": "create fs: procuringEntity.identifier.uri"
                    },
                    "address": {
                        "streetAddress": "create fs: procuringEntity.address.streetAddress",
                        "postalCode": "create fs: procuringEntity.address.postalCode",
                        "addressDetails": {
                            "country": {
                                "id": "MD"
                            },
                            "region": {
                                "id": "1700000"
                            },
                            "locality": {
                                "scheme": f"{random.choice(locality_scheme)}",
                                "id": "1701000",
                                "description":
                                    "create fs: tender.procuringEntity.address.addressDetails.locality.description"
                            }
                        }
                    },
                    "additionalIdentifiers": [{
                        "id": "create fs: tender.procuringEntity.additionalIdentifiers.id",
                        "scheme": "create fs: tender.procuringEntity.additionalIdentifiers.scheme",
                        "legalName": "create fs: tender.procuringEntity.additionalIdentifiers.legalName",
                        "uri": "create fs: tender.procuringEntity.additionalIdentifiers.uri"
                    }],
                    "contactPoint": {
                        "name": "create fs: tender.procuringEntity.contactPoint.name",
                        "email": "create fs: tender.procuringEntity.contactPoint.email",
                        "telephone": "create fs: tender.procuringEntity.contactPoint.telephone",
                        "faxNumber": "create fs: tender.procuringEntity.contactPoint.faxNumber",
                        "url": "create fs: tender.procuringEntity.contactPoint.url"
                    }
                }
            },
            "planning": {
                "budget": {
                    "id": "create fs: planning.budget.id",
                    "description": "create fs: planning.budget.description",
                    "period": {
                        "startDate": ei_payload['planning']['budget']['period']['startDate'],
                        "endDate": ei_payload['planning']['budget']['period']['endDate']
                    },
                    "amount": {
                        "amount": 88889.89,
                        "currency": self.__currency,
                    },
                    "isEuropeanUnionFunded": True,
                    "europeanUnionFunding": {
                        "projectName": "create fs: planning.budget.europeanUnionFunding.projectName",
                        "projectIdentifier": "create fs: planning.budget.europeanUnionFunding.projectIdentifier",
                        "uri": "create fs: planning.budget.europeanUnionFunding.uri"
                    },
                    "project": "create fs: planning.budget.project",
                    "projectID": "create fs: planning.budget.projectID",
                    "uri": "create fs: planning.budget.uri"
                },
                "rationale": "create fs: planning.rationale"
            },
            "buyer": {
                "name": "create fs: buyer.name",
                "identifier": {
                    "id": "create fs: buyer.identifier.id",
                    "scheme": "MD-IDNO",
                    "legalName": "create fs: buyer.identifier.legalName",
                    "uri": "create fs: buyer.identifier.uri"
                },
                "address": {
                    "streetAddress": "create fs: buyer.address.streetAddress",
                    "postalCode": "create fs: buyer.address.postalCode",
                    "addressDetails": {
                        "country": {
                            "id": "MD"
                        },
                        "region": {
                            "id": "1700000"
                        },
                        "locality": {
                            "scheme": f"{random.choice(locality_scheme)}",
                            "id": "1701000",
                            "description": "create fs: buyer.address.addressDetails.locality.description"
                        }
                    }
                },
                "additionalIdentifiers": [{
                    "id": "create fs: buyer.additionalIdentifiers0.id",
                    "scheme": "create fs: buyer.additionalIdentifiers0.scheme",
                    "legalName": "create fs: buyer.additionalIdentifiers0.legalName",
                    "uri": "create fs: buyer.additionalIdentifiers0.uri"
                }],
                "contactPoint": {
                        "name": "create fs: buyer.contactPoint.name",
                        "email": "create fs: buyer.contactPoint.email",
                        "telephone": "create fs: buyer.contactPoint.telephone",
                        "faxNumber": "create fs: buyer.contactPoint.faxNumber",
                        "url": "create fs: buyer.contactPoint.url"
                    }
            }
        }

    def build_financial_source_payload(self):
        return self.__payload

    def delete_optional_fields(
            self, *args, procuringentity_additionalidentifiers_positionn=0,
            buyer_additionalidentifiers_position=0):
        for a in args:
            if a == "tender.procuringEntity.identifier.uri":
                del self.__payload['tender']['procuringEntity']['identifier']['uri']
            elif a == "tender.procuringEntity.address.postalCode":
                del self.__payload['tender']['procuringEntity']['address']['postalCode']
            elif a == "tender.procuringEntity.additionalIdentifiers":
                del self.__payload['tender']['procuringEntity']['additionalIdentifiers']
            elif a == "tender.procuringEntity.additionalIdentifiers.uri":

                del self.__payload['tender']['procuringEntity'][
                    'additionalIdentifiers'][procuringentity_additionalidentifiers_positionn]['uri']

            elif a == "tender.procuringEntity.contactPoint.faxNumber":
                del self.__payload['tender']['procuringEntity']['contactPoint']['faxNumber']
            elif a == "tender.procuringEntity.contactPoint.url":
                del self.__payload['tender']['procuringEntity']['contactPoint']['url']

            elif a == "planning.budget.id":
                del self.__payload['planning']['budget']['id']
            elif a == "planning.budget.description":
                del self.__payload['planning']['budget']['description']
            elif a == "planning.budget.europeanUnionFunding":
                self.__payload['planning']['budget']['isEuropeanUnionFunded'] = False
                del self.__payload['planning']['budget']['europeanUnionFunding']
            elif a == "planning.budget.europeanUnionFunding.uri":
                del self.__payload['planning']['budget']['europeanUnionFunding']['uri']
            elif a == "planning.budget.project":
                del self.__payload['planning']['budget']['project']
            elif a == "planning.budget.projectID":
                del self.__payload['planning']['budget']['projectID']
            elif a == "planning.budget.uri":
                del self.__payload['planning']['budget']['uri']
            elif a == "planning.rationale":
                del self.__payload['planning']['rationale']

            elif a == "buyer.identifier.uri":
                del self.__payload['buyer']['identifier']['uri']
            elif a == "buyer.address.postalCode":
                del self.__payload['buyer']['address']['postalCode']
            elif a == "buyer.additionalIdentifiers":
                del self.__payload['buyer']['additionalIdentifiers']
            elif a == "buyer.additionalIdentifiers.uri":
                del self.__payload['buyer']['additionalIdentifiers'][buyer_additionalidentifiers_position]['uri']
            elif a == "buyer.contactPoint.faxNumber":
                del self.__payload['buyer']['contactPoint']['faxNumber']
            elif a == "buyer.contactPoint.url":
                del self.__payload['buyer']['contactPoint']['url']

            else:
                raise KeyError(f"Impossible to delete attribute by path {a}.")

    def customize_buyer_additionalidentifiers(self, quantity_of_buyer_additionalidentifiers):
        new_additionalidentifiers_array = list()
        for q in range(quantity_of_buyer_additionalidentifiers):
            new_additionalidentifiers_array.append(copy.deepcopy(self.__payload['buyer']['additionalIdentifiers'][0]))
            new_additionalidentifiers_array[q]['id'] = f"create fs: buyer.additionalIdentifiers{q}.id"
            new_additionalidentifiers_array[q]['scheme'] = f"create fs: buyer.additionalIdentifiers{q}.scheme"
            new_additionalidentifiers_array[q]['legalName'] = f"create fs: buyer.additionalIdentifiers{q}.legalName"
            new_additionalidentifiers_array[q]['uri'] = f"create fs: buyer.additionalIdentifiers{q}.uri"

        self.__payload['buyer']['additionalIdentifiers'] = new_additionalidentifiers_array

    def customize_tender_procuringentity_additionalidentifiers(
            self, quantity_of_tender_procuringentity_additionalidentifiers):
        new_additionalidentifiers_array = list()
        for q in range(quantity_of_tender_procuringentity_additionalidentifiers):

            new_additionalidentifiers_array.append(
                copy.deepcopy(self.__payload['tender']['procuringEntity']['additionalIdentifiers'][0])
            )

            new_additionalidentifiers_array[q]['id'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.id"

            new_additionalidentifiers_array[q]['scheme'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.scheme"

            new_additionalidentifiers_array[q]['legalName'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.legalName"

            new_additionalidentifiers_array[q]['uri'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.uri"

        self.__payload['tender']['procuringEntity']['additionalIdentifiers'] = new_additionalidentifiers_array

    def __del__(self):
        print(f"The instance of class {__name__} was deleted.")
