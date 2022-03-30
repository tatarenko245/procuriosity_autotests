import copy

from tests.utils.ReleaseModels.LimitedProcedure.Award.award_release_library import ReleaseLibrary
from tests.utils.functions_collection import get_value_from_country_csv, get_value_from_region_csv, get_value_from_locality_csv


class AwardReleases:
    def __init__(self, environment, language, award_payload, awardFeedPointMessage):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.payload = award_payload
        self.awardFeedPointMessage = awardFeedPointMessage

        if environment == "dev":
            self.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
        elif environment == "sandbox":
            self.metadata_document_url = "http://storage.eprocurement.systems/get"

    def create_parties_array(self, actual_parties_array):

        expected_array_of_parties_mapper = list()

        for supplier in range(len(self.payload['award']['suppliers'])):
            try:
                """
                Prepare party object framework.
                """
                party_object = dict()
                party_object.update(self.constructor.np_release_parties_object())
            except Exception:
                raise Exception("Impossible to build expected party object framework.")

            try:
                """
                Enrich party object framework by required value.
                """
                party_object['id'] = f"{self.payload['award']['suppliers'][supplier]['identifier']['scheme']}-" \
                                     f"{self.payload['award']['suppliers'][supplier]['identifier']['id']}"

                party_object['name'] = self.payload['award']['suppliers'][supplier]['name']
                party_object['identifier'] = self.payload['award']['suppliers'][supplier]['identifier']

                party_object['address']['streetAddress'] = \
                    self.payload['award']['suppliers'][supplier]['address']['streetAddress']

                try:
                    """
                    Enrich party object framework by value: 'address.addressDetails.country', 
                     'address.addressDetails.region', 'address.addressDetails.locality' from csv tables.
                    """
                    tenderer_country_data = get_value_from_country_csv(
                        country=self.payload['award']['suppliers'][supplier]['address']['addressDetails'][
                            'country']['id'],

                        language=self.language
                    )

                    tenderer_country_object = {
                        "scheme": tenderer_country_data[2],

                        "id": self.payload['award']['suppliers'][supplier]['address']['addressDetails'][
                            'country']['id'],

                        "description": tenderer_country_data[1],
                        "uri": tenderer_country_data[3]
                    }

                    tenderer_region_data = get_value_from_region_csv(
                        country=self.payload['award']['suppliers'][supplier]['address']['addressDetails'][
                            'country']['id'],

                        region=self.payload['award']['suppliers'][supplier]['address']['addressDetails'][
                            'region']['id'],

                        language=self.language
                    )

                    tenderer_region_object = {
                        "scheme": tenderer_region_data[2],
                        "id": self.payload['award']['suppliers'][supplier]['address']['addressDetails']['region']['id'],
                        "description": tenderer_region_data[1],
                        "uri": tenderer_region_data[3]
                    }

                    if self.payload['award']['suppliers'][supplier]['address']['addressDetails'][
                            'locality']['scheme'] == "CUATM":

                        tenderer_locality_data = get_value_from_locality_csv(
                            country=self.payload['award']['suppliers'][supplier]['address']['addressDetails'][
                                'country']['id'],

                            region=self.payload['award']['suppliers'][supplier]['address']['addressDetails'][
                                'region']['id'],

                            locality=self.payload['award']['suppliers'][supplier]['address']['addressDetails'][
                                'locality']['id'],

                            language=self.language

                        )
                        tenderer_locality_object = {
                            "scheme": tenderer_locality_data[2],

                            "id": self.payload['award']['suppliers'][supplier]['address']['addressDetails']['locality'][
                                'id'],

                            "description": tenderer_locality_data[1],
                            "uri": tenderer_locality_data[3]
                        }
                    else:
                        tenderer_locality_object = {
                            "scheme": self.payload['award']['suppliers'][supplier]['address']['addressDetails'][
                                'locality']['scheme'],

                            "id": self.payload['award']['suppliers'][supplier]['address']['addressDetails'][
                                'locality']['id'],

                            "description": self.payload['award']['suppliers'][supplier]['address']['addressDetails'][
                                'locality']['description']
                        }
                except Exception:
                    raise Exception("Impossible to enrich party object framework by value: "
                                    "'address.addressDetails.country', 'address.addressDetails.region', "
                                    "'address.addressDetails.locality' from csv table.")

                party_object['address']['addressDetails']['country'] = tenderer_country_object
                party_object['address']['addressDetails']['region'] = tenderer_region_object
                party_object['address']['addressDetails']['locality'] = tenderer_locality_object
                party_object['contactPoint'] = self.payload['award']['suppliers'][supplier]['contactPoint']

            except Exception:
                raise Exception("Impossible to enrich party object framework by required value.")

            try:
                """
                Enrich party object framework by optional value.
                """

                if "additionalIdentifiers" in self.payload['award']['suppliers'][supplier]:
                    party_object['additionalIdentifiers'] = list()

                    for additionalIdentifier in range(
                            len(self.payload['award']['suppliers'][supplier]['additionalIdentifiers'])):

                        party_object['additionalIdentifiers'].append(
                            self.constructor.np_release_parties_additionalIdentifiers_object())

                        party_object['additionalIdentifiers'][additionalIdentifier]['id'] = \
                            self.payload['award']['suppliers'][supplier]['additionalIdentifiers'][
                                additionalIdentifier]['id']

                        party_object['additionalIdentifiers'][additionalIdentifier]['legalName'] = \
                            self.payload['award']['suppliers'][supplier]['additionalIdentifiers'][
                                additionalIdentifier]['legalName']

                        party_object['additionalIdentifiers'][additionalIdentifier]['scheme'] = \
                            self.payload['award']['suppliers'][supplier]['additionalIdentifiers'][
                                additionalIdentifier]['scheme']

                        if "uri" in self.payload['award']['suppliers'][supplier]['additionalIdentifiers'][
                                additionalIdentifier]:

                            party_object['additionalIdentifiers'][additionalIdentifier]['uri'] = \
                                self.payload['award']['suppliers'][supplier]['additionalIdentifiers'][
                                    additionalIdentifier]['uri']
                        else:
                            del party_object['additionalIdentifiers'][additionalIdentifier]['uri']
                else:
                    del party_object['additionalIdentifiers']

                if "postalCode" in self.payload['award']['suppliers'][supplier]['address']:

                    party_object['address']['postalCode'] = \
                        self.payload['award']['suppliers'][supplier]['address']['postalCode']
                else:
                    del party_object['address']['postalCode']

                if "persones" in self.payload['award']['suppliers'][supplier]:
                    party_object['persones'] = list()
                    for persone in range(len(self.payload['award']['suppliers'][supplier]['persones'])):
                        party_object['persones'].append(self.constructor.np_release_parties_persones_object())

                        persone_scheme = \
                            self.payload['award']['suppliers'][supplier]['persones'][persone]['identifier']['scheme']

                        persone_id = \
                            self.payload['award']['suppliers'][supplier]['persones'][persone]['identifier']['id']

                        party_object['persones'][persone]['id'] = f"{persone_scheme}-{persone_id}"

                        party_object['persones'][persone]['title'] = \
                            self.payload['award']['suppliers'][supplier]['persones'][persone]['title']

                        party_object['persones'][persone]['name'] = \
                            self.payload['award']['suppliers'][supplier]['persones'][persone]['name']

                        party_object['persones'][persone]['identifier']['scheme'] = \
                            self.payload['award']['suppliers'][supplier]['persones'][persone]['identifier']['scheme']

                        party_object['persones'][persone]['identifier']['id'] = \
                            self.payload['award']['suppliers'][supplier]['persones'][persone]['identifier']['id']

                        if "uri" in self.payload['award']['suppliers'][supplier]['persones'][persone]['identifier']:

                            party_object['persones'][persone]['identifier']['uri'] = \
                                self.payload['award']['suppliers'][supplier]['persones'][persone]['identifier']['uri']

                        else:
                            del party_object['persones'][persone]['identifier']['uri']

                        party_object['persones'][persone]['businessFunctions'] = list()
                        for businessFunction in range(len(self.payload['award']['suppliers'][supplier][
                                                              'persones'][persone]['businessFunctions'])):

                            party_object['persones'][persone]['businessFunctions'].append(
                                self.constructor.np_release_parties_persones_businessFunctions_object()
                            )

                            party_object['persones'][persone]['businessFunctions'][businessFunction]['id'] = \
                                self.payload['award']['suppliers'][supplier]['persones'][persone][
                                    'businessFunctions'][businessFunction]['id']

                            party_object['persones'][persone]['businessFunctions'][businessFunction]['type'] = \
                                self.payload['award']['suppliers'][supplier]['persones'][persone][
                                    'businessFunctions'][businessFunction]['type']

                            party_object['persones'][persone]['businessFunctions'][businessFunction]['jobTitle'] = \
                                self.payload['award']['suppliers'][supplier]['persones'][persone][
                                    'businessFunctions'][businessFunction]['jobTitle']

                            party_object['persones'][persone]['businessFunctions'][businessFunction]['period'][
                                'startDate'] = \
                                self.payload['award']['suppliers'][supplier]['persones'][persone][
                                    'businessFunctions'][businessFunction]['period']['startDate']

                            if "documents" in self.payload['award']['suppliers'][supplier][
                                    'persones'][persone]['businessFunctions'][businessFunction]:

                                party_object['persones'][persone]['businessFunctions'][businessFunction][
                                    'documents'] = list()

                                for document in range(len(self.payload['award']['suppliers'][supplier][
                                                              'persones'][persone]['businessFunctions'][
                                                              businessFunction]['documents'])):

                                    party_object['persones'][persone][
                                        'businessFunctions'][businessFunction]['documents'].append(
                                        self.constructor.
                                            np_release_parties_persones_businessFunctions_documents_object())

                                    party_object['persones'][persone]['businessFunctions'][businessFunction][
                                        'documents'][document]['documentType'] = \
                                        self.payload['award']['suppliers'][supplier]['persones'][persone][
                                            'businessFunctions'][businessFunction]['documents'][document][
                                            'documentType']

                                    party_object['persones'][persone]['businessFunctions'][businessFunction][
                                        'documents'][document]['id'] = \
                                        self.payload['award']['suppliers'][supplier]['persones'][persone][
                                            'businessFunctions'][businessFunction]['documents'][document]['id']

                                    party_object['persones'][persone]['businessFunctions'][businessFunction][
                                        'documents'][document]['title'] = \
                                        self.payload['award']['suppliers'][supplier]['persones'][persone][
                                            'businessFunctions'][businessFunction]['documents'][document]['title']

                                    document_id = \
                                        self.payload['award']['suppliers'][supplier]['persones'][persone][
                                            'businessFunctions'][businessFunction]['documents'][document]['id']

                                    party_object['persones'][persone]['businessFunctions'][businessFunction][
                                        'documents'][document]['url'] = f"{self.metadata_document_url}/{document_id}"

                                    party_object['persones'][persone]['businessFunctions'][businessFunction][
                                        'documents'][document]['datePublished'] = \
                                        self.awardFeedPointMessage['data']['operationDate']

                                    if "description" in self.payload['award']['suppliers'][supplier][
                                        'persones'][persone]['businessFunctions'][businessFunction][
                                            'documents'][document]:

                                        party_object['persones'][persone]['businessFunctions'][businessFunction][
                                            'documents'][document]['description'] = \
                                            self.payload['award']['suppliers'][supplier]['persones'][persone][
                                                'businessFunctions'][businessFunction]['documents'][document][
                                                'description']

                                    else:
                                        del party_object['persones'][persone]['businessFunctions'][businessFunction][
                                            'documents'][document]['description']
                            else:
                                del party_object['persones'][persone]['businessFunctions'][businessFunction][
                                    'documents']
                else:
                    del party_object['persones']

                if "typeOfSupplier" in self.payload['award']['suppliers'][supplier]['details']:

                    party_object['details']['typeOfSupplier'] = self.payload['award']['suppliers'][supplier]['details'][
                        'typeOfSupplier']
                else:
                    del party_object['details']['typeOfSupplier']

                if "mainEconomicActivities" in self.payload['award']['suppliers'][supplier]['details']:

                    party_object['details']['mainEconomicActivities'] = list()

                    for mainEconomicActivity in range(len(
                            self.payload['award']['suppliers'][supplier]['details']['mainEconomicActivities'])):
                        party_object['details']['mainEconomicActivities'].append(
                            self.constructor.np_release_parties_details_mainEconomicActivity_object())

                        party_object['details']['mainEconomicActivities'][mainEconomicActivity] = \
                            self.payload['award']['suppliers'][supplier]['details']['mainEconomicActivities'][
                                mainEconomicActivity]
                else:
                    del party_object['details']['mainEconomicActivities']

                if "bankAccounts" in self.payload['award']['suppliers'][supplier]['details']:

                    party_object['details']['bankAccounts'] = list()

                    for bank in range(len(self.payload['award']['suppliers'][supplier]['details']['bankAccounts'])):

                        party_object['details']['bankAccounts'].append(
                            self.constructor.np_release_parties_details_bankAccounts_object())

                        party_object['details']['bankAccounts'][bank]['description'] = \
                            self.payload['award']['suppliers'][supplier]['details']['bankAccounts'][bank]['description']

                        party_object['details']['bankAccounts'][bank]['bankName'] = \
                            self.payload['award']['suppliers'][supplier]['details']['bankAccounts'][bank]['bankName']

                        party_object['details']['bankAccounts'][bank]['address']['streetAddress'] = \
                            self.payload['award']['suppliers'][supplier]['details']['bankAccounts'][bank]['address'][
                                'streetAddress']

                        if "postalCode" in \
                                self.payload['award']['suppliers'][supplier]['details']['bankAccounts'][bank][
                                    'address']:

                            party_object['details']['bankAccounts'][bank]['address']['postalCode'] = \
                                self.payload['award']['suppliers'][supplier]['details']['bankAccounts'][bank][
                                    'address']['postalCode']
                        else:
                            del party_object['details']['bankAccounts'][bank]['address']['postalCode']

                        try:
                            """
                            Enrich party object framework by value: 
                            'award.suppliers.details.bankAccounts.address.addressDetails.country', 
                            'award.suppliers.details.bankAccounts.address.addressDetails.region',
                            'award.suppliers.details.bankAccounts.address.addressDetails.locality'
                            from csv tables.
                            """
                            bank_country_data = get_value_from_country_csv(
                                country=self.payload['award']['suppliers'][supplier]['details'][
                                    'bankAccounts'][bank]['address']['addressDetails']['country']['id'],

                                language=self.language
                            )

                            bank_country_object = {
                                "scheme": bank_country_data[2],

                                "id": self.payload['award']['suppliers'][supplier]['details'][
                                    'bankAccounts'][bank]['address']['addressDetails']['country']['id'],

                                "description": bank_country_data[1],
                                "uri": bank_country_data[3]
                            }

                            bank_region_data = get_value_from_region_csv(
                                country=self.payload['award']['suppliers'][supplier]['details'][
                                    'bankAccounts'][bank]['address']['addressDetails']['country']['id'],

                                region=self.payload['award']['suppliers'][supplier]['details'][
                                    'bankAccounts'][bank]['address']['addressDetails']['region']['id'],

                                language=self.language
                            )

                            bank_region_object = {
                                "scheme": bank_region_data[2],

                                "id": self.payload['award']['suppliers'][supplier]['details'][
                                    'bankAccounts'][bank]['address']['addressDetails']['region']['id'],

                                "description": bank_region_data[1],
                                "uri": bank_region_data[3]
                            }

                            if \
                                    self.payload['award']['suppliers'][supplier]['details'][
                                        'bankAccounts'][bank]['address']['addressDetails']['locality']['scheme'] == \
                                    "CUATM":

                                bank_locality_data = get_value_from_locality_csv(
                                    country=self.payload['award']['suppliers'][supplier]['details'][
                                        'bankAccounts'][bank]['address']['addressDetails']['country']['id'],

                                    region=self.payload['award']['suppliers'][supplier]['details'][
                                        'bankAccounts'][bank]['address']['addressDetails']['region']['id'],

                                    locality=self.payload['award']['suppliers'][supplier]['details'][
                                        'bankAccounts'][bank]['address']['addressDetails']['locality']['id'],

                                    language=self.language
                                )

                                bank_locality_object = {
                                    "scheme": bank_locality_data[2],

                                    "id": self.payload['award']['suppliers'][supplier]['details'][
                                        'bankAccounts'][bank]['address']['addressDetails']['locality']['id'],

                                    "description": bank_locality_data[1],
                                    "uri": bank_locality_data[3]
                                }
                            else:
                                bank_locality_object = {
                                    "scheme": self.payload['award']['suppliers'][supplier]['details'][
                                        'bankAccounts'][bank]['address']['addressDetails']['locality']['scheme'],

                                    "id": self.payload['award']['suppliers'][supplier]['details'][
                                        'bankAccounts'][bank]['address']['addressDetails']['locality']['id'],

                                    "description": self.payload['award']['suppliers'][supplier]['details'][
                                        'bankAccounts'][bank]['address']['addressDetails']['locality']['description']
                                }

                            party_object['details']['bankAccounts'][bank]['address']['addressDetails'][
                                'country'] = bank_country_object

                            party_object['details']['bankAccounts'][bank]['address']['addressDetails'][
                                'region'] = bank_region_object

                            party_object['details']['bankAccounts'][bank]['address']['addressDetails'][
                                'locality'] = bank_locality_object
                        except Exception:
                            raise Exception("Impossible to enrich party object framework by value: "
                                            "'award.suppliers.details.bankAccounts.address.addressDetails.country', "
                                            "'award.suppliers.details.bankAccounts.address.addressDetails.region',"
                                            "'award.suppliers.details.bankAccounts.address.addressDetails.locality'"
                                            "from csv tables.")

                        party_object['details']['bankAccounts'][bank]['identifier'] = \
                            self.payload['award']['suppliers'][supplier]['details']['bankAccounts'][bank]['identifier']

                        party_object['details']['bankAccounts'][bank]['accountIdentification'] = \
                            self.payload['award']['suppliers'][supplier]['details']['bankAccounts'][bank][
                                'accountIdentification']

                        if "additionalAccountIdentifiers" in \
                                self.payload['award']['suppliers'][supplier]['details']['bankAccounts'][bank]:

                            party_object['details']['bankAccounts'][bank]['additionalAccountIdentifiers'] = \
                                self.payload['award']['suppliers'][supplier]['details']['bankAccounts'][bank][
                                    'additionalAccountIdentifiers']
                        else:
                            del party_object['details']['bankAccounts'][bank]['additionalAccountIdentifiers']

                else:
                    del party_object['details']['bankAccounts']

                party_object['details']['scale'] = \
                    self.payload['award']['suppliers'][supplier]['details']['scale']

                if "permits" in self.payload['award']['suppliers'][supplier]['details']:
                    party_object['details']['permits'] = list()
                    for permit in range(len(self.payload['award']['suppliers'][supplier]['details']['permits'])):

                        party_object['details']['permits'].append(
                            self.constructor.np_release_parties_details_permits_object())

                        party_object['details']['permits'][permit]['scheme'] = \
                            self.payload['award']['suppliers'][supplier]['details']['permits'][permit]['scheme']

                        party_object['details']['permits'][permit]['id'] = \
                            self.payload['award']['suppliers'][supplier]['details']['permits'][permit]['id']

                        if "url" in self.payload['award']['suppliers'][supplier]['details']['permits'][permit]:

                            party_object['details']['permits'][permit]['url'] = \
                                self.payload['award']['suppliers'][supplier]['details']['permits'][permit]['url']
                        else:
                            del party_object['details']['permits'][permit]['url']

                        party_object['details']['permits'][permit]['permitDetails']['issuedBy'] = \
                            self.payload['award']['suppliers'][supplier]['details']['permits'][permit][
                                'permitDetails']['issuedBy']

                        party_object['details']['permits'][permit]['permitDetails']['issuedThought'] = \
                            self.payload['award']['suppliers'][supplier]['details']['permits'][permit][
                                'permitDetails']['issuedThought']

                        party_object['details']['permits'][permit]['permitDetails']['validityPeriod']['startDate'] = \
                            self.payload['award']['suppliers'][supplier]['details']['permits'][permit][
                                'permitDetails']['validityPeriod']['startDate']

                        if "endDate" in self.payload['award']['suppliers'][supplier]['details']['permits'][permit][
                                'permitDetails']['validityPeriod']:

                            party_object['details']['permits'][permit]['permitDetails']['validityPeriod']['endDate'] = \
                                self.payload['award']['suppliers'][supplier]['details']['permits'][permit][
                                    'permitDetails']['validityPeriod']['endDate']
                        else:
                            del party_object['details']['permits'][permit]['permitDetails']['validityPeriod']['endDate']
                else:
                    del party_object['details']['permits']

                if "legalForm" in self.payload['award']['suppliers'][supplier]['details']:

                    party_object['details']['legalForm']['scheme'] = \
                        self.payload['award']['suppliers'][supplier]['details']['legalForm']['scheme']

                    party_object['details']['legalForm']['id'] = \
                        self.payload['award']['suppliers'][supplier]['details']['legalForm']['id']

                    party_object['details']['legalForm']['description'] = \
                        self.payload['award']['suppliers'][supplier]['details']['legalForm']['description']

                    if "uri" in self.payload['award']['suppliers'][supplier]['details']['legalForm']:
                        party_object['details']['legalForm']['uri'] = \
                            self.payload['award']['suppliers'][supplier]['details']['legalForm']['uri']
                    else:
                        del party_object['details']['legalForm']['uri']
                else:
                    del party_object['details']['legalForm']

            except Exception:
                raise Exception("Impossible to enrich party object framework by optional value.")

            party_object['roles'] = ["supplier"]
            mapper = {
                "id": party_object['id'],
                "value": party_object
            }
            expected_array_of_parties_mapper.append(mapper)

        final_expected_parties_array = list()
        for actual in range(len(actual_parties_array)):
            for expected in range(len(expected_array_of_parties_mapper)):
                if expected_array_of_parties_mapper[expected]['id'] == actual_parties_array[actual]['id']:
                    final_expected_parties_array.append(expected_array_of_parties_mapper[expected]['value'])
        return final_expected_parties_array

    def create_awards_array(self, lot_id, actual_awards_array):
        expected_array_of_awards_mapper = list()

        for actual_award in range(len(actual_awards_array)):
            try:
                """
                Prepare award object framework.
                """
                award_object = dict()
                award_object.update(self.constructor.np_release_awards_object())
            except Exception:
                raise Exception("Impossible to build expected award object framework.")

            if actual_awards_array[actual_award]['relatedLots'] == [lot_id]:

                try:
                    """
                    Enrich award object framework by required value.
                    """
                    award_object['id'] = actual_awards_array[actual_award]['id']
                    award_object['status'] = "pending"
                    award_object['statusDetails'] = "empty"
                    award_object['date'] = self.awardFeedPointMessage['data']['operationDate']
                    award_object['value']['currency'] = self.payload['award']['value']['currency']

                    award_object['suppliers'] = list()
                    for supplier in range(len(self.payload['award']['suppliers'])):
                        award_object['suppliers'].append(self.constructor.np_release_awards_suppliers_object())

                        award_object['suppliers'][supplier]['id'] = \
                            f"{self.payload['award']['suppliers'][supplier]['identifier']['scheme']}-" \
                            f"{self.payload['award']['suppliers'][supplier]['identifier']['id']}"

                        award_object['suppliers'][supplier]['name'] = \
                            self.payload['award']['suppliers'][supplier]['name']

                    award_object['relatedLots'] = [lot_id]

                except Exception:
                    raise Exception("Impossible to enrich award object framework by required value.")

                try:
                    """
                    Enrich award object framework by optional value.
                    """
                    if "internalId" in self.payload['award']:
                        award_object['internalId'] = self.payload['award']['internalId']
                    else:
                        del award_object['internalId']

                    if "description" in self.payload['award']:
                        award_object['description'] = self.payload['award']['description']
                    else:
                        del award_object['description']

                    if "amount" in self.payload['award']['value']:
                        award_object['value']['amount'] = self.payload['award']['value']['amount']
                    else:
                        del award_object['value']['amount']

                    if "documents" in self.payload['award']:
                        award_object['documents'] = list()

                        for document in range(len(self.payload['award']['documents'])):

                            award_object['documents'].append(self.constructor.np_release_awards_documents_object())

                            award_object['documents'][document]['id'] = \
                                self.payload['award']['documents'][document]['id']

                            award_object['documents'][document]['documentType'] = \
                                self.payload['award']['documents'][document]['documentType']

                            award_object['documents'][document]['title'] = \
                                self.payload['award']['documents'][document]['title']

                            if "description" in self.payload['award']['documents'][document]:
                                award_object['documents'][document]['description'] = \
                                    self.payload['award']['documents'][document]['description']
                            else:
                                del award_object['documents'][document]['description']

                            award_object['documents'][document]['url'] = \
                                f"{self.metadata_document_url}/{self.payload['award']['documents'][document]['id']}"

                            award_object['documents'][document]['datePublished'] = \
                                self.awardFeedPointMessage['data']['operationDate']
                    else:
                        del award_object['documents']
                except Exception:
                    raise Exception("Impossible to enrich award object framework by optional value.")

                mapper = {
                    "id": award_object['id'],
                    "value": award_object
                }
                expected_array_of_awards_mapper.append(mapper)

        final_expected_awards_array = list()
        for actual in range(len(actual_awards_array)):
            for expected in range(len(expected_array_of_awards_mapper)):
                if expected_array_of_awards_mapper[expected]['id'] == actual_awards_array[actual]['id']:
                    final_expected_awards_array.append(expected_array_of_awards_mapper[expected]['value'])
        return final_expected_awards_array
