from tests.conftest import GlobalClassCreateEi, GlobalClassCreateFs
from tests.utils.e_mdm_service import MdmService
from tests.utils.fixtures_and_functions import is_it_uuid, get_value_from_classification_cpv_dictionary_xls, \
    get_value_from_cpvs_dictionary_csv, get_value_from_classification_unit_dictionary_csv


class EiRelease:
    def __init__(self):
        self.metadata_budget_url = None
        try:
            if GlobalClassCreateEi.environment == "dev":
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
            elif GlobalClassCreateEi.environment == "sandbox":
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
        except ValueError:
            print("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

    def for_create_ei_full_data_model(self, ei_id, operation_date, release_id, language, tender_id, item_id, country):

        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            print("Check your tender_id in EI release: tender_id in EI release must be uuid version 4")
        try:
            is_it_uuid(
                uuid_to_test=item_id,
                version=4
            )
        except ValueError:
            print("Check your item_id in EI release: item_id in EI release must be uuid version 4")
        data_from_mdm_service = MdmService().process_ei_data(
            country=country,
            language=language
        )
        try:
            if data_from_mdm_service['data']['tender']['items'][0]['classification'][
                'id'] == get_value_from_classification_cpv_dictionary_xls(
                cpv=GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0]['classification']['id'],
                language=language
            ):
                print("item_classification_id is correct")
        except ValueError:
            print("Check your item_classification_id in EI release: "
                  "item_classification_id in EI release must be correct")
        try:
            if data_from_mdm_service['data']['tender']['items'][0]['additionalClassifications'][0][
                'id'] == get_value_from_cpvs_dictionary_csv(
                cpvs=GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0]['additionalClassifications'][0][
                    'id'],
                language=language
            ):
                print("item_additionalClassifications_id is correct")
        except ValueError:
            print("Check your item_additionalClassifications_id in EI release: "
                  "item_additionalClassifications_id in EI release must be correct")
        try:
            if data_from_mdm_service['data']['tender']['items'][0]['unit'][
                'id'] == get_value_from_classification_unit_dictionary_csv(
                unit_id=GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0]['unit']['id'],
                language=language
            ):
                print("item_unit_id is correct")
        except ValueError:
            print("Check your item_unit_id in EI release: "
                  "item_unit_idd in EI release must be correct")
        item_locality_object = None
        for i in data_from_mdm_service['data']['tender']['items'][0]['deliveryAddress']['addressDetails']['locality']:
            if i == "uri":
                item_locality_object = {
                    "scheme": data_from_mdm_service['data']['tender']['items'][0][
                        'deliveryAddress']['addressDetails']['locality']['scheme'],
                    "id": data_from_mdm_service['data']['tender']['items'][0][
                        'deliveryAddress']['addressDetails']['locality']['id'],
                    "description": data_from_mdm_service['data']['tender']['items'][0][
                        'deliveryAddress']['addressDetails']['locality']['description'],
                    "uri": data_from_mdm_service['data']['tender']['items'][0][
                        'deliveryAddress']['addressDetails']['locality']['uri']
                }
            else:
                item_locality_object = {
                    "scheme": data_from_mdm_service['data']['tender']['items'][0][
                        'deliveryAddress']['addressDetails']['locality']['scheme'],
                    "id": data_from_mdm_service['data']['tender']['items'][0][
                        'deliveryAddress']['addressDetails']['locality']['id'],
                    "description": data_from_mdm_service['data']['tender']['items'][0][
                        'deliveryAddress']['addressDetails']['locality']['description']

                }
        buyer_locality_object = None
        for i in data_from_mdm_service['data']['buyer']['address']['addressDetails']['locality']:
            if i == "uri":
                buyer_locality_object = {
                    "scheme": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['scheme'],
                    "id": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['id'],
                    "description": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['description'],
                    "uri": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['uri']
                }
            else:
                buyer_locality_object = {
                    "scheme": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['scheme'],
                    "id": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['id'],
                    "description": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['description'],
                    "uri": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['uri']
                }
        # Релиз базируется на ответе от сервиса eMDM: processEiData ->
        # ЛОГИКА ТАКАЯ: так как некоторые данные обогащаются на сервисе, то если в будущем какие-то другие
        # данные будут обогащаться здесь же, то будет проще. Сейчас данные, что заходят на сервис mdm
        # равны данным с запроса площадки.

        json = {
            "uri": f"{self.metadata_budget_url}/{ei_id}/{ei_id}",
            "version": "1.1",
            "extensions": [
                "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"],
            "publisher": {
                "name": "M-Tender",
                "uri": "https://www.mtender.gov.md"
            },
            "license": "http://opendefinition.org/licenses/",
            "publicationPolicy": "http://opendefinition.org/licenses/",
            "publishedDate": operation_date,
            "releases": [{
                "ocid": ei_id,
                # timestamp в release_id формируется системой произвольно -> невозможно ни на что завязаться
                "id": f"{ei_id}-{release_id[29:42]}",
                "date": operation_date,
                "tag": ["compiled"],
                "language": language,
                "initiationType": "tender",
                "tender": {
                    "id": tender_id,
                    "title": GlobalClassCreateEi.payload_for_create_ei['tender']['title'],
                    "description": GlobalClassCreateEi.payload_for_create_ei['tender']['description'],
                    "status": "planning",
                    "statusDetails": "empty",
                    "items": [{
                        "id": item_id,
                        "description": "item 1",
                        "classification": {
                            "scheme": data_from_mdm_service['data']['tender']['items'][0][
                                'classification']['scheme'],
                            "id": data_from_mdm_service['data']['tender']['items'][0][
                                'classification']['id'],
                            "description": data_from_mdm_service['data']['tender']['items'][0][
                                'classification']['description']
                        },
                        "additionalClassifications": [{
                            "scheme": data_from_mdm_service['data']['tender']['items'][0][
                                'additionalClassifications'][0]['scheme'],
                            "id": data_from_mdm_service['data']['tender']['items'][0][
                                'additionalClassifications'][0]['id'],
                            "description": data_from_mdm_service['data']['tender']['items'][0][
                                'additionalClassifications'][0]['description']
                        }],
                        "quantity": data_from_mdm_service['data']['tender']['items'][0]['quantity'],
                        "unit": {
                            "name": data_from_mdm_service['data']['tender']['items'][0]['unit']['name'],
                            "id": data_from_mdm_service['data']['tender']['items'][0]['unit']['id']
                        },
                        "deliveryAddress": {
                            "streetAddress": data_from_mdm_service['data']['tender']['items'][0][
                                'deliveryAddress']['streetAddress'],
                            "postalCode": data_from_mdm_service['data']['tender']['items'][0][
                                'deliveryAddress']['postalCode'],
                            "addressDetails": {
                                "country": {
                                    "scheme": data_from_mdm_service['data']['tender']['items'][0][
                                        'deliveryAddress']['addressDetails']['country']['scheme'],
                                    "id": data_from_mdm_service['data']['tender']['items'][0][
                                        'deliveryAddress']['addressDetails']['country']['id'],
                                    "description": data_from_mdm_service['data']['tender']['items'][0][
                                        'deliveryAddress']['addressDetails']['country']['description'],
                                    "uri": data_from_mdm_service['data']['tender']['items'][0][
                                        'deliveryAddress']['addressDetails']['country']['uri']
                                },
                                "region": {
                                    "scheme": data_from_mdm_service['data']['tender']['items'][0][
                                        'deliveryAddress']['addressDetails']['region']['scheme'],
                                    "id": data_from_mdm_service['data']['tender']['items'][0][
                                        'deliveryAddress']['addressDetails']['region']['id'],
                                    "description": data_from_mdm_service['data']['tender']['items'][0][
                                        'deliveryAddress']['addressDetails']['region']['description'],
                                    "uri": data_from_mdm_service['data']['tender']['items'][0][
                                        'deliveryAddress']['addressDetails']['region']['uri']
                                },
                                "locality": item_locality_object
                            }
                        }
                    }],
                    "mainProcurementCategory": data_from_mdm_service['data']['tender'][
                        'mainProcurementCategory'],
                    "classification": {
                        "scheme": data_from_mdm_service['data']['tender']['classification']['scheme'],
                        "id": data_from_mdm_service['data']['tender']['classification']['id'],
                        "description": data_from_mdm_service['data']['tender']['classification']['description']
                    }
                },
                "buyer": {
                    "id": f"{data_from_mdm_service['data']['buyer']['identifier']['scheme']}-"
                          f"{data_from_mdm_service['data']['buyer']['identifier']['id']}",
                    "name": data_from_mdm_service['data']['buyer']['name']
                },
                "parties": [{
                    "id": f"{data_from_mdm_service['data']['buyer']['identifier']['scheme']}-"
                          f"{data_from_mdm_service['data']['buyer']['identifier']['id']}",
                    "name": data_from_mdm_service['data']['buyer']['name'],
                    "identifier": {
                        "scheme": data_from_mdm_service['data']['buyer']['identifier']['scheme'],
                        "id": data_from_mdm_service['data']['buyer']['identifier']['id'],
                        "legalName": data_from_mdm_service['data']['buyer']['identifier']['legalName'],
                        "uri": data_from_mdm_service['data']['buyer']['identifier']['uri']
                    },
                    "address": {
                        "streetAddress": data_from_mdm_service['data']['buyer']['address']['streetAddress'],
                        "postalCode": data_from_mdm_service['data']['buyer']['address']['postalCode'],
                        "addressDetails": {
                            "country": {
                                "scheme": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['country']['scheme'],
                                "id": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['country']['id'],
                                "description": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['country']['description'],
                                "uri": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['country']['uri']
                            },
                            "region": {
                                "scheme": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['region']['scheme'],
                                "id": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['region']['id'],
                                "description": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['region']['description'],
                                "uri": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['region']['uri']
                            },
                            "locality": buyer_locality_object
                        }
                    },
                    "additionalIdentifiers": [{
                        "scheme": data_from_mdm_service['data']['buyer']['additionalIdentifiers'][0][
                            'scheme'],
                        "id": data_from_mdm_service['data']['buyer']['additionalIdentifiers'][0]['id'],
                        "legalName": data_from_mdm_service['data']['buyer']['additionalIdentifiers'][0][
                            'legalName'],
                        "uri": data_from_mdm_service['data']['buyer']['additionalIdentifiers'][0]['uri']
                    }],
                    "contactPoint": {
                        "name": data_from_mdm_service['data']['buyer']['contactPoint']['name'],
                        "email": data_from_mdm_service['data']['buyer']['contactPoint']['email'],
                        "telephone": data_from_mdm_service['data']['buyer']['contactPoint']['telephone'],
                        "faxNumber": data_from_mdm_service['data']['buyer']['contactPoint']['faxNumber'],
                        "url": data_from_mdm_service['data']['buyer']['contactPoint']['url']
                    },
                    "details": {
                        "typeOfBuyer": data_from_mdm_service['data']['buyer']['details']['typeOfBuyer'],
                        "mainGeneralActivity": data_from_mdm_service['data']['buyer']['details'][
                            'mainGeneralActivity'],
                        "mainSectoralActivity": data_from_mdm_service['data']['buyer']['details'][
                            'mainSectoralActivity']
                    },
                    "roles": ["buyer"]
                }],
                "planning": {
                    "budget": {
                        "id": data_from_mdm_service['data']['tender']['classification']['id'],
                        "period": {
                            "startDate": GlobalClassCreateEi.payload_for_create_ei['planning']['budget']['period'][
                                'startDate'],
                            "endDate": GlobalClassCreateEi.payload_for_create_ei['planning']['budget']['period'][
                                'endDate']
                        }
                    },
                    "rationale": GlobalClassCreateEi.payload_for_create_ei['planning']['rationale']
                }
            }]
        }
        return json


class FsRelease:
    def __init__(self):
        self.metadata_budget_url = None
        try:
            if GlobalClassCreateEi.environment == "dev":
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
            elif GlobalClassCreateEi.environment == "sandbox":
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
        except ValueError:
            print("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

    def for_create_fs_full_own_money_data_model(self, ei_id, fs_id, operation_date, release_id, language, tender_id,
                                                country, related_process_id):
        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            print("Check your tender_id in FS release: tender_id in FS release must be uuid version 4")
        try:
            is_it_uuid(
                uuid_to_test=related_process_id,
                version=1
            )
        except ValueError:
            print("Check your related_process_id in EI release: "
                  "related_process_id in FS release must be uuid version 1")
        data_from_mdm_service = MdmService().process_fs_data(
            ei_id=ei_id,
            country=country,
            language=language
        )

        buyer_locality_object = None
        for i in data_from_mdm_service['data']['buyer']['address']['addressDetails']['locality']:
            if i == "uri":
                buyer_locality_object = {
                    "scheme": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['scheme'],
                    "id": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['id'],
                    "description": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['description'],
                    "uri": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['uri']
                }
            else:
                buyer_locality_object = {
                    "scheme": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['scheme'],
                    "id": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['id'],
                    "description": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['description'],
                    "uri": data_from_mdm_service['data']['buyer']['address'][
                        'addressDetails']['locality']['uri']
                }

        procuring_entity_locality_object = None
        for i in data_from_mdm_service['data']['tender']['procuringEntity']['address']['addressDetails']['locality']:
            if i == "uri":
                procuring_entity_locality_object = {
                    "scheme": data_from_mdm_service['data']['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['scheme'],
                    "id": data_from_mdm_service['data']['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['id'],
                    "description": data_from_mdm_service['data']['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['description'],
                    "uri": data_from_mdm_service['data']['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['uri']
                }
            else:
                procuring_entity_locality_object = {
                    "scheme": data_from_mdm_service['data']['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['scheme'],
                    "id": data_from_mdm_service['data']['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['id'],
                    "description": data_from_mdm_service['data']['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['description'],
                    "uri": data_from_mdm_service['data']['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['uri']
                }
        verified = None
        for i in GlobalClassCreateFs.payload_for_create_fs.keys():
            if i == "buyer":
                verified = True
            else:
                verified = False
                # Релиз базируется на ответе от сервиса eMDM: processEiData ->
        # ЛОГИКА ТАКАЯ: так как некоторые данные обогащаются на сервисе, то если в будущем какие-то другие
        # данные будут обогащаться здесь же, то будет проще. Сейчас данные, что заходят на сервис mdm
        # равны данным с запроса площадки.

        json = {
            "uri": f"{self.metadata_budget_url}/{ei_id}/{fs_id}",
            "version": "1.1",
            "extensions": [
                "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"],
            "publisher": {
                "name": "M-Tender",
                "uri": "https://www.mtender.gov.md"
            },
            "license": "http://opendefinition.org/licenses/",
            "publicationPolicy": "http://opendefinition.org/licenses/",
            "publishedDate": operation_date,
            "releases": [{
                "ocid": fs_id,
                # timestamp в release_id формируется системой произвольно -> невозможно ни на что завязаться
                "id": f"{fs_id}-{release_id[46:59]}",
                "date": operation_date,
                "tag": ["planning"],
                "initiationType": "tender",
                "tender": {
                    "id": tender_id,
                    "status": "active",
                    "statusDetails": "empty"
                },
                "parties": [{
                    "id": f"{data_from_mdm_service['data']['buyer']['identifier']['scheme']}-"
                          f"{data_from_mdm_service['data']['buyer']['identifier']['id']}",
                    "name": data_from_mdm_service['data']['buyer']['name'],
                    "identifier": {
                        "scheme": data_from_mdm_service['data']['buyer']['identifier']['scheme'],
                        "id": data_from_mdm_service['data']['buyer']['identifier']['id'],
                        "legalName": data_from_mdm_service['data']['buyer']['identifier']['legalName'],
                        "uri": data_from_mdm_service['data']['buyer']['identifier']['uri']
                    },
                    "address": {
                        "streetAddress": data_from_mdm_service['data']['buyer']['address']['streetAddress'],
                        "postalCode": data_from_mdm_service['data']['buyer']['address']['postalCode'],
                        "addressDetails": {
                            "country": {
                                "scheme": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['country']['scheme'],
                                "id": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['country']['id'],
                                "description": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['country']['description'],
                                "uri": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['country']['uri']
                            },
                            "region": {
                                "scheme": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['region']['scheme'],
                                "id": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['region']['id'],
                                "description": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['region']['description'],
                                "uri": data_from_mdm_service['data']['buyer']['address'][
                                    'addressDetails']['region']['uri']
                            },
                            "locality": buyer_locality_object
                        }
                    },
                    "additionalIdentifiers": [{
                        "scheme": data_from_mdm_service['data']['buyer']['additionalIdentifiers'][0]['scheme'],
                        "id": data_from_mdm_service['data']['buyer']['additionalIdentifiers'][0]['id'],
                        "legalName": data_from_mdm_service['data']['buyer']['additionalIdentifiers'][0]['legalName'],
                        "uri": data_from_mdm_service['data']['buyer']['additionalIdentifiers'][0]['uri']
                    }],
                    "contactPoint": {
                        "name": data_from_mdm_service['data']['buyer']['contactPoint']['name'],
                        "email": data_from_mdm_service['data']['buyer']['contactPoint']['email'],
                        "telephone": data_from_mdm_service['data']['buyer']['contactPoint']['telephone'],
                        "faxNumber": data_from_mdm_service['data']['buyer']['contactPoint']['faxNumber'],
                        "url": data_from_mdm_service['data']['buyer']['contactPoint']['url']
                    },
                    "roles": ["funder"]
                }, {
                    "id": f"{data_from_mdm_service['data']['tender']['procuringEntity']['identifier']['scheme']}-"
                          f"{data_from_mdm_service['data']['tender']['procuringEntity']['identifier']['id']}",
                    "name": data_from_mdm_service['data']['tender']['procuringEntity']['name'],
                    "identifier": {
                        "scheme": data_from_mdm_service['data']['tender']['procuringEntity']['identifier']['scheme'],
                        "id": data_from_mdm_service['data']['tender']['procuringEntity']['identifier']['id'],
                        "legalName": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'identifier']['legalName'],
                        "uri": data_from_mdm_service['data']['tender']['procuringEntity']['identifier']['uri']
                    },
                    "address": {
                        "streetAddress": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'address']['streetAddress'],
                        "postalCode": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'address']['postalCode'],
                        "addressDetails": {
                            "country": {
                                "scheme": data_from_mdm_service['data']['tender']['procuringEntity'][
                                    'address']['addressDetails']['country']['scheme'],
                                "id": data_from_mdm_service['data']['tender']['procuringEntity'][
                                    'address']['addressDetails']['country']['id'],
                                "description": data_from_mdm_service['data']['tender']['procuringEntity'][
                                    'address']['addressDetails']['country']['description'],
                                "uri": data_from_mdm_service['data']['tender']['procuringEntity'][
                                    'address']['addressDetails']['country']['uri']
                            },
                            "region": {
                                "scheme": data_from_mdm_service['data']['tender']['procuringEntity'][
                                    'address']['addressDetails']['region']['scheme'],
                                "id": data_from_mdm_service['data']['tender']['procuringEntity'][
                                    'address']['addressDetails']['region']['id'],
                                "description": data_from_mdm_service['data']['tender']['procuringEntity'][
                                    'address']['addressDetails']['region']['description'],
                                "uri": data_from_mdm_service['data']['tender']['procuringEntity'][
                                    'address']['addressDetails']['region']['uri']
                            },
                            "locality": procuring_entity_locality_object
                        }
                    },
                    "additionalIdentifiers": [{
                        "scheme": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'additionalIdentifiers'][0]['scheme'],
                        "id": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'additionalIdentifiers'][0]['id'],
                        "legalName": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'additionalIdentifiers'][0]['legalName'],
                        "uri": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'additionalIdentifiers'][0]['uri']
                    }],
                    "contactPoint": {
                        "name": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'contactPoint']['name'],
                        "email": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'contactPoint']['email'],
                        "telephone": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'contactPoint']['telephone'],
                        "faxNumber": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'contactPoint']['faxNumber'],
                        "url": data_from_mdm_service['data']['tender']['procuringEntity'][
                            'contactPoint']['url']
                    },
                    "roles": ["payer"]
                }],
                "planning": {
                    "budget": {
                        "id": GlobalClassCreateFs.payload_for_create_fs['planning']['budget']['id'],
                        "description": GlobalClassCreateFs.payload_for_create_fs['planning']['budget']['description'],
                        "period": {
                            "startDate": GlobalClassCreateFs.payload_for_create_fs['planning']['budget']['period'][
                                'startDate'],
                            "endDate": GlobalClassCreateFs.payload_for_create_fs['planning']['budget']['period'][
                                'endDate']
                        },
                        "amount": {
                            "amount": GlobalClassCreateFs.payload_for_create_fs['planning']['budget'][
                                'amount']['amount'],
                            "currency": GlobalClassCreateFs.payload_for_create_fs['planning']['budget'][
                                'amount']['currency']
                        },
                        "europeanUnionFunding": {
                            "projectIdentifier": GlobalClassCreateFs.payload_for_create_fs['planning']['budget'][
                                'europeanUnionFunding']['projectIdentifier'],
                            "projectName": GlobalClassCreateFs.payload_for_create_fs['planning']['budget'][
                                'europeanUnionFunding']['projectName'],
                            "uri": GlobalClassCreateFs.payload_for_create_fs['planning']['budget'][
                                'europeanUnionFunding']['uri']
                        },
                        "isEuropeanUnionFunded": GlobalClassCreateFs.payload_for_create_fs['planning']['budget'][
                            'isEuropeanUnionFunded'],
                        "verified": verified,
                        "sourceEntity": {
                            "id": f"{data_from_mdm_service['data']['buyer']['identifier']['scheme']}-"
                                  f"{data_from_mdm_service['data']['buyer']['identifier']['id']}",
                            "name": data_from_mdm_service['data']['buyer']['name']
                        },
                        "project": GlobalClassCreateFs.payload_for_create_fs['planning']['budget']['project'],
                        "projectID": GlobalClassCreateFs.payload_for_create_fs['planning']['budget']['projectID'],
                        "uri": GlobalClassCreateFs.payload_for_create_fs['planning']['budget']['uri']
                    },
                    "rationale": GlobalClassCreateFs.payload_for_create_fs['planning']['rationale']
                },
                "relatedProcesses": [{
                    "id": related_process_id,
                    "relationship": ["parent"],
                    "scheme": "ocid",
                    "identifier": ei_id,
                    "uri": f"{self.metadata_budget_url}/{ei_id}/{ei_id}"
                }]
            }]
        }
        return json
