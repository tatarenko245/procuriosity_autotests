import random

from tests.utils.data_of_enum import legalBasis
from tests.utils.date_class import Date
from tests.utils.iStorage import Document


class PnPreparePayload:
    def __init__(self, fs_payload, fs_feed_point_message):
        self.pn_period = Date().planning_notice_period()
        self.fs_payload = fs_payload
        self.fs_feed_point_message = fs_feed_point_message

    def create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs(self):
        payload = {
            "tender": {
                "title": "create pn: tender.title",
                "description": "create pn: tender.description",
                "legalBasis": f"{random.choice(legalBasis)}",
                "tenderPeriod": {
                    "startDate": self.pn_period
                },
                "procuringEntity": {
                    "name": "create pn: tender.procuringEntity.name",
                    "identifier": {
                        "id": "create pn: tender.procuringEntity.identifier.id",
                        "scheme": "MD-IDNO",
                        "legalName": "create pn: tender.procuringEntity.identifier.legalName"
                    },
                    "address": {
                        "streetAddress": "create pn: tender.procuringEntity.address.streetAddress",
                        "addressDetails": {
                            "country": {
                                "id": "MD"
                            },
                            "region": {
                                "id": "1700000"
                            },
                            "locality": {
                                "scheme": "CUATM",
                                "id": "1701000",
                                "description":
                                    "create pn: tender.procuringEntity.address.addressDetails.locality.description"
                            }
                        }
                    },
                    "contactPoint": {
                        "name": "create pn: tender.procuringEntity.contactPoint.name",
                        "email": "create pn: tender.procuringEntity.contactPoint.email",
                        "telephone": "create pn: tender.procuringEntity.contactPoint.telephone"
                    }
                }
            },
            "planning": {
                "budget": {
                    "budgetBreakdown": [{
                        "id": self.fs_feed_point_message['data']['outcomes']['fs'][0]['id'],
                        "amount": {
                            "amount": self.fs_payload['planning']['budget']['amount']['amount'],
                            "currency": self.fs_payload['planning']['budget']['amount']['currency']
                        }
                    }]
                }
            }
        }
        return payload

    def update_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs(self):
        payload = {
            "planning": {
                "budget": {
                }
            },
            "tender": {
                "tenderPeriod": {
                    "startDate": self.pn_period
                }
            }
        }
        return payload
