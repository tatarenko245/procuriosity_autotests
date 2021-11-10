import copy
import uuid
import requests
from tests.conftest import GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassMetadata
from tests.utils.date_class import Date
from tests.utils.http_manager import HttpManager


class MdmService:
    def __init__(self, host):
        self.port = HttpManager().e_mdm_service()[0]
        self.host = host
        print(self.host)

    def process_ei_data(self, country, language):
        time_at_now = Date().time_at_now()
        command = HttpManager().e_mdm_service()[1]
        data = requests.post(
            url=f"{self.host}:{self.port}/{command}",
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
                            "id": GlobalClassCreateEi.payload['tender']['classification']['id']
                        },
                        "items": [{
                            "id": GlobalClassCreateEi.payload['tender']['items'][0]['id'],
                            "description": GlobalClassCreateEi.payload['tender'][
                                'items'][0]['description'],
                            "classification": {
                                "id": GlobalClassCreateEi.payload['tender']['items'][0][
                                    'classification']['id']
                            },
                            "additionalClassifications": [{
                                "id": GlobalClassCreateEi.payload['tender']['items'][0][
                                    'additionalClassifications'][0]['id']
                            }],
                            "deliveryAddress": {
                                "streetAddress": GlobalClassCreateEi.payload['tender']['items'][0][
                                    'deliveryAddress']['streetAddress'],
                                "postalCode": GlobalClassCreateEi.payload['tender']['items'][0][
                                    'deliveryAddress']['postalCode'],
                                "addressDetails": {
                                    "country": {
                                        "id": GlobalClassCreateEi.payload['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['country']['id']
                                    },
                                    "region": {
                                        "id": GlobalClassCreateEi.payload['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['region']['id']
                                    },
                                    "locality": {
                                        "id": GlobalClassCreateEi.payload['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['id'],
                                        "description": GlobalClassCreateEi.payload['tender'][
                                            'items'][0]['deliveryAddress']['addressDetails'][
                                            'locality']['description'],
                                        "scheme": GlobalClassCreateEi.payload['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['scheme']
                                    }
                                }
                            },
                            "quantity": GlobalClassCreateEi.payload['tender']['items'][0]['quantity'],
                            "unit": {
                                "id": GlobalClassCreateEi.payload['tender']['items'][0]['unit']['id']
                            }
                        }]
                    },
                    "buyer": {
                        "name": GlobalClassCreateEi.payload['buyer']['name'],
                        "identifier": {
                            "id": GlobalClassCreateEi.payload['buyer']['identifier']['id'],
                            "scheme": GlobalClassCreateEi.payload['buyer']['identifier']['scheme'],
                            "legalName": GlobalClassCreateEi.payload['buyer']['identifier'][
                                'legalName'],
                            "uri": GlobalClassCreateEi.payload['buyer']['identifier']['uri']
                        },
                        "address": {
                            "streetAddress": GlobalClassCreateEi.payload['buyer']['address'][
                                'streetAddress'],
                            "postalCode": GlobalClassCreateEi.payload['buyer']['address']['postalCode'],
                            "addressDetails": {
                                "country": {
                                    "id": GlobalClassCreateEi.payload['buyer']['address'][
                                        'addressDetails']['country']['id']
                                },
                                "region": {
                                    "id": GlobalClassCreateEi.payload['buyer']['address'][
                                        'addressDetails']['region']['id']
                                },
                                "locality": {
                                    "scheme": GlobalClassCreateEi.payload['buyer']['address'][
                                        'addressDetails']['locality']['scheme'],
                                    "id": GlobalClassCreateEi.payload['buyer']['address'][
                                        'addressDetails']['locality']['id'],
                                    "description": GlobalClassCreateEi.payload['buyer']['address'][
                                        'addressDetails']['locality']['description']
                                }
                            }
                        },
                        "additionalIdentifiers": [{
                            "id": GlobalClassCreateEi.payload['buyer'][
                                'additionalIdentifiers'][0]['id'],
                            "scheme": GlobalClassCreateEi.payload['buyer'][
                                'additionalIdentifiers'][0]['scheme'],
                            "legalName": GlobalClassCreateEi.payload['buyer'][
                                'additionalIdentifiers'][0]['legalName'],
                            "uri": GlobalClassCreateEi.payload['buyer'][
                                'additionalIdentifiers'][0]['uri']
                        }],
                        "contactPoint": {
                            "name": GlobalClassCreateEi.payload['buyer']['contactPoint']['name'],
                            "email": GlobalClassCreateEi.payload['buyer']['contactPoint']['email'],
                            "telephone": GlobalClassCreateEi.payload['buyer'][
                                'contactPoint']['telephone'],
                            "faxNumber": GlobalClassCreateEi.payload['buyer'][
                                'contactPoint']['faxNumber'],
                            "url": GlobalClassCreateEi.payload['buyer']['contactPoint']['url']
                        },
                        "details": {
                            "typeOfBuyer": GlobalClassCreateEi.payload['buyer']['details'][
                                'typeOfBuyer'],
                            "mainGeneralActivity": GlobalClassCreateEi.payload['buyer'][
                                'details']['mainGeneralActivity'],
                            "mainSectoralActivity": GlobalClassCreateEi.payload['buyer'][
                                'details']['mainSectoralActivity']
                        }
                    }
                },
                "version": "0.0.1"
            })
        return data.json()

    def process_fs_data(self, ei_id, country, language):
        time_at_now = Date().time_at_now()
        command = HttpManager().e_mdm_service()[1]
        data = requests.post(
            url=f"{self.host}:{self.port}/{command}",
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
                                "currency": GlobalClassCreateFs.payload['planning']['budget'][
                                    'amount']['currency']
                            }
                        }
                    },
                    "tender": {
                        "procuringEntity": {
                            "name": GlobalClassCreateFs.payload['tender']['procuringEntity']['name'],
                            "identifier": {
                                "id": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['identifier']['id'],
                                "scheme": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['identifier']['scheme'],
                                "legalName": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['identifier']['legalName'],
                                "uri": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['identifier']['uri']
                            },
                            "additionalIdentifiers": [{
                                "id": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['additionalIdentifiers'][0]['id'],
                                "scheme": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['additionalIdentifiers'][0]['scheme'],
                                "legalName": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['additionalIdentifiers'][0]['legalName'],
                                "uri": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['additionalIdentifiers'][0]['uri']
                            }],
                            "address": {
                                "streetAddress": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['address']['streetAddress'],
                                "postalCode": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['address']['postalCode'],
                                "addressDetails": {
                                    "country": {
                                        "id": GlobalClassCreateFs.payload['tender'][
                                            'procuringEntity']['address']['addressDetails']['country']['id']
                                    },
                                    "region": {
                                        "id": GlobalClassCreateFs.payload['tender'][
                                            'procuringEntity']['address']['addressDetails']['region']['id']
                                    },
                                    "locality": {
                                        "scheme": GlobalClassCreateFs.payload['tender'][
                                            'procuringEntity']['address']['addressDetails']['locality']['scheme'],
                                        "id": GlobalClassCreateFs.payload['tender'][
                                            'procuringEntity']['address']['addressDetails']['locality']['id'],
                                        "description": GlobalClassCreateFs.payload['tender'][
                                            'procuringEntity']['address']['addressDetails']['locality']['description']
                                    }
                                }
                            },
                            "contactPoint": {
                                "name": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['contactPoint']['name'],
                                "email": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['contactPoint']['email'],
                                "telephone": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['contactPoint']['telephone'],
                                "faxNumber": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['contactPoint']['faxNumber'],
                                "url": GlobalClassCreateFs.payload['tender'][
                                    'procuringEntity']['contactPoint']['url']
                            }
                        }
                    },
                    "buyer": {
                        "name": GlobalClassCreateFs.payload['buyer']['name'],
                        "identifier": {
                            "id": GlobalClassCreateFs.payload['buyer']['identifier']['id'],
                            "scheme": GlobalClassCreateFs.payload['buyer']['identifier']['scheme'],
                            "legalName": GlobalClassCreateFs.payload['buyer']['identifier']['legalName'],
                            "uri": GlobalClassCreateFs.payload['buyer']['identifier']['uri']
                        },
                        "address": {
                            "streetAddress": GlobalClassCreateFs.payload['buyer'][
                                'address']['streetAddress'],
                            "postalCode": GlobalClassCreateFs.payload['buyer'][
                                'address']['postalCode'],
                            "addressDetails": {
                                "country": {
                                    "id": GlobalClassCreateFs.payload['buyer'][
                                        'address']['addressDetails']['country']['id']
                                },
                                "region": {
                                    "id": GlobalClassCreateFs.payload['buyer'][
                                        'address']['addressDetails']['region']['id']
                                },
                                "locality": {
                                    "scheme": GlobalClassCreateFs.payload['buyer'][
                                        'address']['addressDetails']['locality']['scheme'],
                                    "id": GlobalClassCreateFs.payload['buyer'][
                                        'address']['addressDetails']['locality']['id'],
                                    "description": GlobalClassCreateFs.payload['buyer'][
                                        'address']['addressDetails']['locality']['description']
                                }
                            }
                        },
                        "additionalIdentifiers": [{
                            "id": GlobalClassCreateFs.payload['buyer']['additionalIdentifiers'][0]['id'],
                            "scheme": GlobalClassCreateFs.payload['buyer'][
                                'additionalIdentifiers'][0]['scheme'],
                            "legalName": GlobalClassCreateFs.payload['buyer'][
                                'additionalIdentifiers'][0]['legalName'],
                            "uri": GlobalClassCreateFs.payload['buyer']['additionalIdentifiers'][0]['uri']
                        }],
                        "contactPoint": {
                            "name": GlobalClassCreateFs.payload['buyer']['contactPoint']['name'],
                            "email": GlobalClassCreateFs.payload['buyer']['contactPoint']['email'],
                            "telephone": GlobalClassCreateFs.payload['buyer'][
                                'contactPoint']['telephone'],
                            "faxNumber": GlobalClassCreateFs.payload['buyer'][
                                'contactPoint']['faxNumber'],
                            "url": GlobalClassCreateFs.payload['buyer'][
                                'contactPoint']['url']
                        }
                    }
                },
                "version": "0.0.1"
            })
        return data.json()

    @staticmethod
    def get_standard_criteria(country, language):
        url = None
        if GlobalClassMetadata.environment == "dev":
            url = "http://dev.public.eprocurement.systems/mdm/standardCriteria"
        elif GlobalClassMetadata.environment == "sandbox":
            url = "http://public.eprocurement.systems/mdm/standardCriteria"
        data = requests.get(url=url,
                            params={
                                'lang': language,
                                'country': country
                            })

        exclusion_ground_criteria_list = list()
        for criteria in copy.deepcopy(data.json()['data']):
            for i in criteria['classification']:
                if i == "id":
                    if criteria['classification']['id'][0:20] == "CRITERION.EXCLUSION.":
                        exclusion_ground_criteria_list.append(criteria['classification'])

        selection_criteria_list = list()
        for criteria in copy.deepcopy(data.json()['data']):
            for i in criteria['classification']:
                if i == "id":
                    if criteria['classification']['id'][0:20] == "CRITERION.SELECTION.":
                        selection_criteria_list.append(criteria['classification'])

        other_criteria_list = list()
        for criteria in copy.deepcopy(data.json()['data']):
            for i in criteria['classification']:
                if i == "id":
                    if criteria['classification']['id'][0:16] == "CRITERION.OTHER.":
                        other_criteria_list.append(criteria['classification'])
        return data.json(), exclusion_ground_criteria_list, selection_criteria_list, other_criteria_list

    def get_country(self, country, language):
        data = requests.get(url=f"{self.host}:{self.port}/addresses/countries/{country}",
                            params={
                                'lang': language
                            }).json()

        return data

    def get_region(self, country, region, language):
        data = requests.get(url=f"{self.host}:"
                                f"{self.port}/addresses/countries/{country}/regions/{region}",
                            params={
                                'lang': language
                            }).json()
        return data

    def get_locality(self, country, region, locality, language):
        data = requests.get(url=f"{self.host}:"
                                f"{self.port}/addresses/countries/{country}/regions/{region}/"
                                f"localities/{locality}",
                            params={
                                'lang': language
                            }).json()
        return data
