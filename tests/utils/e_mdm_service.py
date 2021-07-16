import uuid
import requests
from tests.conftest import GlobalClassCreateEi, GlobalClassCreateFs
from tests.utils.date_class import Date
from tests.utils.http_manager import HttpManager


class MdmService:
    @staticmethod
    def process_ei_data(country, language):
        time_at_now = Date().time_at_now()
        port = HttpManager().e_mdm_service()[0]
        command = HttpManager().e_mdm_service()[1]
        data = requests.post(
            url=GlobalClassCreateEi.host_for_service + f":{port}/{command}",
            json={
                "id": str(uuid.uuid1()),
                "command": "processEiData",
                "context": {
                    "operationId": str(uuid.uuid4()),
                    "requestId": str(uuid.uuid1()),
                    "stage": "EI",
                    "processType": "ei",
                    "operationType": "createEI",
                    "owner": "445f6851-c908-407d-9b45-14b92f3e964b",
                    "country": country,
                    "language": language,
                    "startDate": time_at_now[0],
                    "timeStamp": time_at_now[1],
                    "isAuction": False,
                    "testMode": False
                },
                "data": {
                    "tender": {
                        "classification": {
                            "id": GlobalClassCreateEi.payload_for_create_ei['tender']['classification']['id']
                        },
                        "items": [{
                            "id": GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0]['id'],
                            "description": GlobalClassCreateEi.payload_for_create_ei['tender'][
                                'items'][0]['description'],
                            "classification": {
                                "id": GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0][
                                    'classification']['id']
                            },
                            "additionalClassifications": [{
                                "id": GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0][
                                    'additionalClassifications'][0]['id']
                            }],
                            "deliveryAddress": {
                                "streetAddress": GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0][
                                    'deliveryAddress']['streetAddress'],
                                "postalCode": GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0][
                                    'deliveryAddress']['postalCode'],
                                "addressDetails": {
                                    "country": {
                                        "id": GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['country']['id']
                                    },
                                    "region": {
                                        "id": GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['region']['id']
                                    },
                                    "locality": {
                                        "id": GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['id'],
                                        "description": GlobalClassCreateEi.payload_for_create_ei['tender'][
                                            'items'][0]['deliveryAddress']['addressDetails'][
                                            'locality']['description'],
                                        "scheme": GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['scheme']
                                    }
                                }
                            },
                            "quantity": GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0]['quantity'],
                            "unit": {
                                "id": GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0]['unit']['id']
                            }
                        }]
                    },
                    "buyer": {
                        "name": GlobalClassCreateEi.payload_for_create_ei['buyer']['name'],
                        "identifier": {
                            "id": GlobalClassCreateEi.payload_for_create_ei['buyer']['identifier']['id'],
                            "scheme": GlobalClassCreateEi.payload_for_create_ei['buyer']['identifier']['scheme'],
                            "legalName": GlobalClassCreateEi.payload_for_create_ei['buyer']['identifier'][
                                'legalName'],
                            "uri": GlobalClassCreateEi.payload_for_create_ei['buyer']['identifier']['uri']
                        },
                        "address": {
                            "streetAddress": GlobalClassCreateEi.payload_for_create_ei['buyer']['address'][
                                'streetAddress'],
                            "postalCode": GlobalClassCreateEi.payload_for_create_ei['buyer']['address']['postalCode'],
                            "addressDetails": {
                                "country": {
                                    "id": GlobalClassCreateEi.payload_for_create_ei['buyer']['address'][
                                        'addressDetails']['country']['id']
                                },
                                "region": {
                                    "id": GlobalClassCreateEi.payload_for_create_ei['buyer']['address'][
                                        'addressDetails']['region']['id']
                                },
                                "locality": {
                                    "scheme": GlobalClassCreateEi.payload_for_create_ei['buyer']['address'][
                                        'addressDetails']['locality']['scheme'],
                                    "id": GlobalClassCreateEi.payload_for_create_ei['buyer']['address'][
                                        'addressDetails']['locality']['id'],
                                    "description": GlobalClassCreateEi.payload_for_create_ei['buyer']['address'][
                                        'addressDetails']['locality']['description']
                                }
                            }
                        },
                        "additionalIdentifiers": [{
                            "id": GlobalClassCreateEi.payload_for_create_ei['buyer'][
                                'additionalIdentifiers'][0]['id'],
                            "scheme": GlobalClassCreateEi.payload_for_create_ei['buyer'][
                                'additionalIdentifiers'][0]['scheme'],
                            "legalName": GlobalClassCreateEi.payload_for_create_ei['buyer'][
                                'additionalIdentifiers'][0]['legalName'],
                            "uri": GlobalClassCreateEi.payload_for_create_ei['buyer'][
                                'additionalIdentifiers'][0]['uri']
                        }],
                        "contactPoint": {
                            "name": GlobalClassCreateEi.payload_for_create_ei['buyer']['contactPoint']['name'],
                            "email": GlobalClassCreateEi.payload_for_create_ei['buyer']['contactPoint']['email'],
                            "telephone": GlobalClassCreateEi.payload_for_create_ei['buyer'][
                                'contactPoint']['telephone'],
                            "faxNumber": GlobalClassCreateEi.payload_for_create_ei['buyer'][
                                'contactPoint']['faxNumber'],
                            "url": GlobalClassCreateEi.payload_for_create_ei['buyer']['contactPoint']['url']
                        },
                        "details": {
                            "typeOfBuyer": GlobalClassCreateEi.payload_for_create_ei['buyer']['details'][
                                'typeOfBuyer'],
                            "mainGeneralActivity": GlobalClassCreateEi.payload_for_create_ei['buyer'][
                                'details']['mainGeneralActivity'],
                            "mainSectoralActivity": GlobalClassCreateEi.payload_for_create_ei['buyer'][
                                'details']['mainSectoralActivity']
                        }
                    }
                },
                "version": "0.0.1"
            })
        return data.json()

    @staticmethod
    def process_fs_data(ei_id, country, language):
        time_at_now = Date().time_at_now()
        port = HttpManager().e_mdm_service()[0]
        command = HttpManager().e_mdm_service()[1]
        data = requests.post(
            url=GlobalClassCreateFs.host_for_service + f":{port}/{command}",
            json={
                "id": str(uuid.uuid1()),
                "command": "processFsData",
                "context": {
                    "operationId": str(uuid.uuid4()),
                    "requestId": str(uuid.uuid1()),
                    "cpid": ei_id,
                    "stage": "FS",
                    "processType": "fs",
                    "operationType": "createFS",
                    "owner": "445f6851-c908-407d-9b45-14b92f3e964b",
                    "country": country,
                    "language": language,
                    "startDate": time_at_now[0],
                    "timeStamp": time_at_now[1],
                    "isAuction": False
                },
                "data": {
                    "planning": {
                        "budget": {
                            "amount": {
                                "currency": GlobalClassCreateFs.payload_for_create_fs['planning']['budget'][
                                    'amount']['currency']
                            }
                        }
                    },
                    "tender": {
                        "procuringEntity": {
                            "name": GlobalClassCreateFs.payload_for_create_fs['tender']['procuringEntity']['name'],
                            "identifier": {
                                "id": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['identifier']['id'],
                                "scheme": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['identifier']['scheme'],
                                "legalName": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['identifier']['legalName'],
                                "uri": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['identifier']['uri']
                            },
                            "additionalIdentifiers": [{
                                "id": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['additionalIdentifiers'][0]['id'],
                                "scheme": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['additionalIdentifiers'][0]['scheme'],
                                "legalName": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['additionalIdentifiers'][0]['legalName'],
                                "uri": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['additionalIdentifiers'][0]['uri']
                            }],
                            "address": {
                                "streetAddress": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['address']['streetAddress'],
                                "postalCode": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['address']['postalCode'],
                                "addressDetails": {
                                    "country": {
                                        "id": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                            'procuringEntity']['address']['addressDetails']['country']['id']
                                    },
                                    "region": {
                                        "id": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                            'procuringEntity']['address']['addressDetails']['region']['id']
                                    },
                                    "locality": {
                                        "scheme": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                            'procuringEntity']['address']['addressDetails']['locality']['scheme'],
                                        "id": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                            'procuringEntity']['address']['addressDetails']['locality']['id'],
                                        "description": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                            'procuringEntity']['address']['addressDetails']['locality']['description']
                                    }
                                }
                            },
                            "contactPoint": {
                                "name": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['contactPoint']['name'],
                                "email": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['contactPoint']['email'],
                                "telephone": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['contactPoint']['telephone'],
                                "faxNumber": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['contactPoint']['faxNumber'],
                                "url": GlobalClassCreateFs.payload_for_create_fs['tender'][
                                    'procuringEntity']['contactPoint']['url']
                            }
                        }
                    },
                    "buyer": {
                        "name": GlobalClassCreateFs.payload_for_create_fs['buyer']['name'],
                        "identifier": {
                            "id": GlobalClassCreateFs.payload_for_create_fs['buyer']['identifier']['id'],
                            "scheme": GlobalClassCreateFs.payload_for_create_fs['buyer']['identifier']['scheme'],
                            "legalName": GlobalClassCreateFs.payload_for_create_fs['buyer']['identifier']['legalName'],
                            "uri": GlobalClassCreateFs.payload_for_create_fs['buyer']['identifier']['uri']
                        },
                        "address": {
                            "streetAddress": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                'address']['streetAddress'],
                            "postalCode": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                'address']['postalCode'],
                            "addressDetails": {
                                "country": {
                                    "id": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                        'address']['addressDetails']['country']['id']
                                },
                                "region": {
                                    "id": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                        'address']['addressDetails']['region']['id']
                                },
                                "locality": {
                                    "scheme": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                        'address']['addressDetails']['locality']['scheme'],
                                    "id": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                        'address']['addressDetails']['locality']['id'],
                                    "description": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                        'address']['addressDetails']['locality']['description']
                                }
                            }
                        },
                        "additionalIdentifiers": [{
                            "id": GlobalClassCreateFs.payload_for_create_fs['buyer']['additionalIdentifiers'][0]['id'],
                            "scheme": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                'additionalIdentifiers'][0]['scheme'],
                            "legalName": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                'additionalIdentifiers'][0]['legalName'],
                            "uri": GlobalClassCreateFs.payload_for_create_fs['buyer']['additionalIdentifiers'][0]['uri']
                        }],
                        "contactPoint": {
                            "name": GlobalClassCreateFs.payload_for_create_fs['buyer']['contactPoint']['name'],
                            "email": GlobalClassCreateFs.payload_for_create_fs['buyer']['contactPoint']['email'],
                            "telephone": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                'contactPoint']['telephone'],
                            "faxNumber": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                'contactPoint']['faxNumber'],
                            "url": GlobalClassCreateFs.payload_for_create_fs['buyer'][
                                'contactPoint']['url']
                        }
                    }
                },
                "version": "0.0.1"
            })
        return data.json()
