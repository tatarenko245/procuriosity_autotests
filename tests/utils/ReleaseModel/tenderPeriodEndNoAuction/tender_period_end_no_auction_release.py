import copy

from tests.conftest import GlobalClassMetadata
from tests.utils.ReleaseModel.tenderPeriodEndNoAuction.tender_period_end_no_auction_release_library import \
    ReleaseLibrary
from tests.utils.functions import is_it_uuid


class TenderPeriodExpectedChanges:
    def __init__(self, environment, language):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.metadata_budget_url = None
        self.metadata_tender_url = None
        self.metadata_document_url = None
        self.metadata_auction_url = None

        try:
            if environment == "dev":
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"
                self.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
                self.metadata_auction_url = "http://auction.eprocurement.systems/auctions/"

            elif environment == "sandbox":
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://public.eprocurement.systems/tenders"
                self.metadata_document_url = "http://storage.eprocurement.systems/get"
                self.metadata_auction_url = "https://eauction.eprocurement.systems/auctions/"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")
        GlobalClassMetadata.metadata_budget_url = self.metadata_budget_url
        GlobalClassMetadata.metadata_tender_url = self.metadata_tender_url

    @staticmethod
    def prepare_parties_array(payload_tenderers_array, release_parties_array):
        expected_parties_array = []
        quantity_of_tender_additional_identifiers_objects_into_payload = None
        quantity_of_tender_details_main_economic_activities_objects_into_payload = None
        quantity_of_tender_details_parmits_objects_into_payload = None
        quantity_of_tender_details_bank_accounts_objects_into_payload = None
        quantity_of_tender_details_bank_accounts_additional_account_objects_into_payload = None
        quantity_of_tender_persones_objects_into_payload = None
        quantity_of_tender_persones_business_functions_objects_into_payload = None
        quantity_of_tender_persones_business_functions_documents_objects_into_payload = None

        try:
            """
            Check how many quantity of object into payload_bid_tenderers_array.
            """
            list_of_payload_tenderer_id = list()
            for tenderer_object in payload_tenderers_array:
                for i in tenderer_object['identifier']:
                    if i == "id":
                        list_of_payload_tenderer_id.append(i)

                        try:
                            """
                            Check how many quantity of object into payload_bid_tenderers_array[´additional_identifiers_object'].
                            """
                            list_of_payload_tenderer_additional_identifiers_id = list()
                            for i in tenderer_object['additionalIdentifiers']:
                                for i_1 in i:
                                    if i_1 == "id":
                                        list_of_payload_tenderer_additional_identifiers_id.append(i)
                            quantity_of_tender_additional_identifiers_objects_into_payload = \
                                len(list_of_payload_tenderer_additional_identifiers_id)
                        except KeyError:
                            raise KeyError("Check payload_tenderers_array['additionalIdentifiers']['id']")

                        try:
                            """
                            Check how many quantity of object into payload_bid_tenderers_array[´details']['mainEconomicActivities'].
                            """
                            list_of_payload_tenderer_details_main_economic_activities_id = list()
                            for i in tenderer_object['details']['mainEconomicActivities']:
                                for i_1 in i:
                                    if i_1 == "id":
                                        list_of_payload_tenderer_details_main_economic_activities_id.append(i_1)
                            quantity_of_tender_details_main_economic_activities_objects_into_payload = \
                                len(list_of_payload_tenderer_details_main_economic_activities_id)
                        except KeyError:
                            raise KeyError("Check payload_tenderers_array[´details']['mainEconomicActivities']['id']")

                        try:
                            """
                            Check how many quantity of object into payload_bid_tenderers_array[´details']['permits'].
                            """
                            list_of_payload_tenderer_details_parmits_id = list()
                            for i in tenderer_object['details']['permits']:
                                for i_1 in i:
                                    if i_1 == "id":
                                        list_of_payload_tenderer_details_parmits_id.append(i_1)
                            quantity_of_tender_details_parmits_objects_into_payload = \
                                len(list_of_payload_tenderer_details_parmits_id)
                        except KeyError:
                            raise KeyError("Check payload_tenderers_array[´details']['permits']['id']")

                        try:
                            """
                            Check how many quantity of object into payload_bid_tenderers_array[´details']['bankAccounts'].
                            """
                            list_of_payload_tenderer_details_bank_accounts_name = list()
                            for i in tenderer_object['details']['bankAccounts']:
                                for i_1 in i:
                                    if i_1 == "bankName":
                                        list_of_payload_tenderer_details_bank_accounts_name.append(i_1)
                            quantity_of_tender_details_bank_accounts_objects_into_payload = \
                                len(list_of_payload_tenderer_details_bank_accounts_name)

                            try:
                                """
                                Check how many quantity of object into payload_bid_tenderers_array[´details']['bankAccounts'][
                                'additionalAccountIdentifiers'].
                                """
                                list_of_payload_tenderer_details_bank_accounts_additional_account_id = list()
                                for i_1 in i:
                                    if i_1 == "additionalAccountIdentifiers":
                                        for i_2 in i['additionalAccountIdentifiers']:
                                            for i_3 in i_2:
                                                if i_3 == "id":
                                                    list_of_payload_tenderer_details_bank_accounts_additional_account_id.append(
                                                        i_3)
                                quantity_of_tender_details_bank_accounts_additional_account_objects_into_payload = \
                                    len(list_of_payload_tenderer_details_bank_accounts_additional_account_id)
                            except KeyError:
                                raise KeyError(
                                    "Check payload_tenderers_array[´details']['bankAccounts']['additionalAccountIdentifiers']['id']")
                        except KeyError:
                            raise KeyError("Check payload_tenderers_array[´details']['bankAccounts']['bankName']")

                        try:
                            """
                            Check how many quantity of object into payload_bid_tenderers_array[´persones'].
                            """
                            list_of_payload_tenderer_persones_id = list()
                            for i in tenderer_object['persones']:
                                for i_1 in i['identifier']:
                                    if i_1 == "id":
                                        list_of_payload_tenderer_persones_id.append(i_1)
                            quantity_of_tender_persones_objects_into_payload = \
                                len(list_of_payload_tenderer_persones_id)

                            try:
                                """
                                Check how many quantity of object into payload_bid_tenderers_array[´persones']['businessFunctions'].
                                """
                                list_of_payload_tenderer_persones_business_functions_id = list()
                                for i_1 in i['businessFunctions']:
                                    for i_2 in i_1:
                                        if i_2 == "id":
                                            list_of_payload_tenderer_persones_business_functions_id.append(i_2)
                                quantity_of_tender_persones_business_functions_objects_into_payload = \
                                    len(list_of_payload_tenderer_persones_business_functions_id)

                                try:
                                    """
                                    Check how many quantity of object into payload_bid_tenderers_array[´persones']['businessFunctions'][
                                    'documents'].
                                    """
                                    list_of_payload_tenderer_persones_business_documents_functions_id = list()
                                    for i_1 in i['businessFunctions']:
                                        for i_2 in i_1:
                                            if i_2 == "documents":
                                                for i_3 in i_1['documents']:
                                                    for i_4 in i_3:
                                                        if i_4 == "id":
                                                            list_of_payload_tenderer_persones_business_documents_functions_id.append(
                                                                i_4)
                                    quantity_of_tender_persones_business_functions_documents_objects_into_payload = \
                                        len(list_of_payload_tenderer_persones_business_documents_functions_id) // \
                                        quantity_of_tender_persones_business_functions_objects_into_payload
                                except KeyError:
                                    raise KeyError(
                                        "Check payload_tenderers_array['persones']['businessFunctions']['documents']['id']")
                            except KeyError:
                                raise KeyError("Check payload_tenderers_array['persones']['businessFunctions']['id']")
                        except KeyError:
                            raise KeyError("Check payload_tenderers_array['persones']['id']")

            quantity_of_tender_object_into_payload = len(list_of_payload_tenderer_id)
        except KeyError:
            raise KeyError("Check payload_tenderers_array['identifier']['id']")

        # try:
        #     """
        #     Check how many quantity of object into payload_bid_tenderers_array[´additional_identifiers_object'].
        #     """
        #     list_of_payload_tenderer_additional_identifiers_id = list()
        #     for tenderer_object in payload_tenderers_array:
        #         for i in tenderer_object['additionalIdentifiers']:
        #             for i_1 in i:
        #                 if i_1 == "id":
        #                     list_of_payload_tenderer_additional_identifiers_id.append(i)
        #     quantity_of_tender_additional_identifiers_objects_into_payload = \
        #         len(list_of_payload_tenderer_additional_identifiers_id)
        # except KeyError:
        #     raise KeyError("Check payload_tenderers_array['additionalIdentifiers']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into payload_bid_tenderers_array[´details']['mainEconomicActivities'].
        #     """
        #     list_of_payload_tenderer_details_main_economic_activities_id = list()
        #     for tenderer_object in payload_tenderers_array:
        #         for i in tenderer_object['details']['mainEconomicActivities']:
        #             for i_1 in i:
        #                 if i_1 == "id":
        #                     list_of_payload_tenderer_details_main_economic_activities_id.append(i_1)
        #     quantity_of_tender_details_main_economic_activities_objects_into_payload = \
        #         len(list_of_payload_tenderer_details_main_economic_activities_id)
        # except KeyError:
        #     raise KeyError("Check payload_tenderers_array[´details']['mainEconomicActivities']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into payload_bid_tenderers_array[´details']['permits'].
        #     """
        #     list_of_payload_tenderer_details_parmits_id = list()
        #     for tenderer_object in payload_tenderers_array:
        #         for i in tenderer_object['details']['permits']:
        #             for i_1 in i:
        #                 if i_1 == "id":
        #                     list_of_payload_tenderer_details_parmits_id.append(i_1)
        #     quantity_of_tender_details_parmits_objects_into_payload = \
        #         len(list_of_payload_tenderer_details_parmits_id)
        # except KeyError:
        #     raise KeyError("Check payload_tenderers_array[´details']['permits']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into payload_bid_tenderers_array[´details']['bankAccounts'].
        #     """
        #     list_of_payload_tenderer_details_bank_accounts_name = list()
        #     for tenderer_object in payload_tenderers_array:
        #         for i in tenderer_object['details']['bankAccounts']:
        #             for i_1 in i:
        #                 if i_1 == "bankName":
        #                     list_of_payload_tenderer_details_bank_accounts_name.append(i_1)
        #     quantity_of_tender_details_bank_accounts_objects_into_payload = \
        #         len(list_of_payload_tenderer_details_bank_accounts_name)
        # except KeyError:
        #     raise KeyError("Check payload_tenderers_array[´details']['bankAccounts']['bankName']")
        #
        # try:
        #     """
        #     Check how many quantity of object into payload_bid_tenderers_array[´details']['bankAccounts'][
        #     'additionalAccountIdentifiers'].
        #     """
        #     list_of_payload_tenderer_details_bank_accounts_additional_account_id = list()
        #     for tenderer_object in payload_tenderers_array:
        #         for i in tenderer_object['details']['bankAccounts']:
        #             for i_1 in i:
        #                 if i_1 == "additionalAccountIdentifiers":
        #                     for i_2 in i['additionalAccountIdentifiers']:
        #                         for i_3 in i_2:
        #                             if i_3 == "id":
        #                                 list_of_payload_tenderer_details_bank_accounts_additional_account_id.append(i_3)
        #     quantity_of_tender_details_bank_accounts_additional_account_objects_into_payload = \
        #         len(list_of_payload_tenderer_details_bank_accounts_additional_account_id)
        # except KeyError:
        #     raise KeyError(
        #         "Check payload_tenderers_array[´details']['bankAccounts']['additionalAccountIdentifiers']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into payload_bid_tenderers_array[´persones'].
        #     """
        #     list_of_payload_tenderer_persones_id = list()
        #     for tenderer_object in payload_tenderers_array:
        #         for i in tenderer_object['persones']:
        #             for i_1 in i['identifier']:
        #                 if i_1 == "id":
        #                     list_of_payload_tenderer_persones_id.append(i_1)
        #     quantity_of_tender_persones_objects_into_payload = \
        #         len(list_of_payload_tenderer_persones_id)
        # except KeyError:
        #     raise KeyError("Check payload_tenderers_array['persones']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into payload_bid_tenderers_array[´persones']['businessFunctions'].
        #     """
        #     list_of_payload_tenderer_persones_business_functions_id = list()
        #     for tenderer_object in payload_tenderers_array:
        #         for i in tenderer_object['persones']:
        #             for i_1 in i['businessFunctions']:
        #                 for i_2 in i_1:
        #                     if i_2 == "id":
        #                         list_of_payload_tenderer_persones_business_functions_id.append(i_2)
        #     quantity_of_tender_persones_business_functions_objects_into_payload = \
        #         len(list_of_payload_tenderer_persones_business_functions_id)
        # except KeyError:
        #     raise KeyError("Check payload_tenderers_array['persones']['businessFunctions']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into payload_bid_tenderers_array[´persones']['businessFunctions'][
        #     'documents'].
        #     """
        #     list_of_payload_tenderer_persones_business_documents_functions_id = list()
        #     for tenderer_object in payload_tenderers_array:
        #         for i in tenderer_object['persones']:
        #             for i_1 in i['businessFunctions']:
        #                 for i_2 in i_1:
        #                     if i_2 == "documents":
        #                         for i_3 in i_1['documents']:
        #                             for i_4 in i_3:
        #                                 if i_4 == "id":
        #                                     list_of_payload_tenderer_persones_business_documents_functions_id.append(
        #                                         i_4)
        #     quantity_of_tender_persones_business_functions_documents_objects_into_payload = \
        #         len(list_of_payload_tenderer_persones_business_documents_functions_id)
        # except KeyError:
        #     raise KeyError("Check payload_tenderers_array['persones']['businessFunctions']['documents']['id']")
        quantity_of_party_additional_identifiers_objects_into_release = None
        quantity_of_party_details_main_economic_activities_objects_into_release = None
        quantity_of_party_details_permits_objects_into_release = None
        quantity_of_party_details_bank_accounts_objects_into_release = None
        quantity_of_party_details_bank_accounts_additional_account_objects_into_release = None
        quantity_of_party_persones_into_release = None
        quantity_of_party_persones_business_functions_into_release = None
        quantity_of_party_persones_business_functions_documents_into_release = None
        try:
            """
            Check how many quantity of object into release_parties_array.
            """
            list_of_release_party_id = list()
            for party_object in release_parties_array:
                for i in party_object:
                    if i == "id":
                        list_of_release_party_id.append(i)

                        try:
                            """
                            Check how many quantity of object into release_parties_array['additionalIdentifiers'].
                            """
                            list_of_release_party_additional_identifiers_id = list()
                            for i in party_object['additionalIdentifiers']:
                                for i_1 in i:
                                    if i_1 == "id":
                                        list_of_release_party_additional_identifiers_id.append(i_1)
                            quantity_of_party_additional_identifiers_objects_into_release = \
                                len(list_of_release_party_additional_identifiers_id)
                        except KeyError:
                            raise KeyError("Check ['releases']['tender']['parties'][*]['additionalIdentifiers']['id']")

                        try:
                            """
                            Check how many quantity of object into release_parties_array[´details']['mainEconomicActivities'].
                            """
                            list_of_release_party_details_main_economic_activities_id = list()
                            for i in party_object['details']['mainEconomicActivities']:
                                for i_1 in i:
                                    if i_1 == "id":
                                        list_of_release_party_details_main_economic_activities_id.append(i_1)
                            quantity_of_party_details_main_economic_activities_objects_into_release = \
                                len(list_of_release_party_details_main_economic_activities_id)
                        except KeyError:
                            raise KeyError(
                                "Check ['releases']['tender']['parties'][*][´details']['mainEconomicActivities']['id']")

                        try:
                            """
                            Check how many quantity of object into release_parties_array[´details']['permits'].
                            """
                            list_of_release_party_details_permits_id = list()
                            for i in party_object['details']['permits']:
                                for i_1 in i:
                                    if i_1 == "id":
                                        list_of_release_party_details_permits_id.append(i_1)
                            quantity_of_party_details_permits_objects_into_release = \
                                len(list_of_release_party_details_permits_id)
                        except KeyError:
                            raise KeyError("Check ['releases']['tender']['parties'][*][´details']['permits']['id']")

                        try:
                            """
                            Check how many quantity of object into release_parties_array[´details']['bankAccounts'].
                            """
                            list_of_release_party_details_bank_accounts_name = list()
                            for i in party_object['details']['bankAccounts']:
                                for i_1 in i:
                                    if i_1 == "bankName":
                                        list_of_release_party_details_bank_accounts_name.append(i_1)
                            quantity_of_party_details_bank_accounts_objects_into_release = \
                                len(list_of_release_party_details_bank_accounts_name)
                        except KeyError:
                            raise KeyError(
                                "Check ['releases']['tender']['parties'][*][´details']['bankAccounts']['bankName']")

                        try:
                            """
                            Check how many quantity of object into release_parties_array[´details']['bankAccounts'][
                            'additionalAccountIdentifiers'].
                            """
                            list_of_release_party_details_bank_accounts_additional_account_id = list()
                            for i in party_object['details']['bankAccounts']:
                                for i_1 in i:
                                    if i_1 == "additionalAccountIdentifiers":
                                        for i_2 in i['additionalAccountIdentifiers']:
                                            for i_3 in i_2:
                                                if i_3 == "id":
                                                    list_of_release_party_details_bank_accounts_additional_account_id.append(
                                                        i_3)
                            quantity_of_party_details_bank_accounts_additional_account_objects_into_release = \
                                len(list_of_release_party_details_bank_accounts_additional_account_id)
                        except KeyError:
                            raise KeyError(
                                "Check ['releases']['tender']['parties'][*][´details']['bankAccounts']["
                                "'additionalAccountIdentifiers']['id']")

                        try:
                            """
                            Check how many quantity of object into release_parties_array['persones'].
                            """
                            list_of_release_party_persones_id = list()
                            for i in party_object['persones']:
                                for i_1 in i['identifier']:
                                    if i_1 == "id":
                                        list_of_release_party_persones_id.append(i_1)
                            quantity_of_party_persones_into_release = \
                                len(list_of_release_party_persones_id)
                        except KeyError:
                            raise KeyError("Check ['releases']['tender']['parties'][*]['persones']['id']")

                        try:
                            """
                            Check how many quantity of object into release_parties_array['persones']['businessFunctions'].
                            Check ['persones']['businessFunctions'][*]['id'] -> is it uuid.
                            """
                            list_of_release_party_persones_business_functions_id = list()
                            for i in party_object['persones']:
                                for i_1 in i['businessFunctions']:
                                    for i_2 in i_1:
                                        if i_2 == "id":
                                            list_of_release_party_persones_business_functions_id.append(i_2)
                                            try:
                                                is_it_uuid(
                                                    uuid_to_test=i_1['id'],
                                                    version=4
                                                )
                                            except ValueError:
                                                raise ValueError("Check your businessFunctions array in release: "
                                                                 "['persones']['businessFunctions'][*]['id'] in release "
                                                                 "must be uuid version 4")
                            quantity_of_party_persones_business_functions_into_release = \
                                len(list_of_release_party_persones_business_functions_id)
                        except KeyError:
                            raise KeyError("Check ['releases']['tender']['parties'][*]['persones']['id']")

                        try:
                            """
                            Check how many quantity of object into release_parties_array['persones']['businessFunctions']['documents'].
                            """
                            list_of_release_party_persones_business_functions_documents_id = list()
                            for i in party_object['persones']:
                                for i_1 in i['businessFunctions']:
                                    for i_2 in i_1:
                                        if i_2 == "documents":
                                            for i_3 in i_1['documents']:
                                                for i_4 in i_3:
                                                    if i_4 == "id":
                                                        list_of_release_party_persones_business_functions_documents_id.append(
                                                            i_4)
                            quantity_of_party_persones_business_functions_documents_into_release = \
                                len(list_of_release_party_persones_business_functions_documents_id)
                        except KeyError:
                            raise KeyError("Check ['releases']['tender']['parties'][*]['persones']['id']")
            quantity_of_party_object_into_release = len(list_of_release_party_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['parties'][*]['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into release_parties_array['additionalIdentifiers'].
        #     """
        #     list_of_release_party_additional_identifiers_id = list()
        #     for party_object in release_parties_array:
        #         for i in party_object['additionalIdentifiers']:
        #             for i_1 in i:
        #                 if i_1 == "id":
        #                     list_of_release_party_additional_identifiers_id.append(i_1)
        #     quantity_of_party_additional_identifiers_objects_into_release = \
        #         len(list_of_release_party_additional_identifiers_id)
        # except KeyError:
        #     raise KeyError("Check ['releases']['tender']['parties'][*]['additionalIdentifiers']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into release_parties_array[´details']['mainEconomicActivities'].
        #     """
        #     list_of_release_party_details_main_economic_activities_id = list()
        #     for party_object in release_parties_array:
        #         for i in party_object['details']['mainEconomicActivities']:
        #             for i_1 in i:
        #                 if i_1 == "id":
        #                     list_of_release_party_details_main_economic_activities_id.append(i_1)
        #     quantity_of_party_details_main_economic_activities_objects_into_release = \
        #         len(list_of_release_party_details_main_economic_activities_id)
        # except KeyError:
        #     raise KeyError("Check ['releases']['tender']['parties'][*][´details']['mainEconomicActivities']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into release_parties_array[´details']['permits'].
        #     """
        #     list_of_release_party_details_permits_id = list()
        #     for party_object in release_parties_array:
        #         for i in party_object['details']['permits']:
        #             for i_1 in i:
        #                 if i_1 == "id":
        #                     list_of_release_party_details_permits_id.append(i_1)
        #     quantity_of_party_details_permits_objects_into_release = \
        #         len(list_of_release_party_details_permits_id)
        # except KeyError:
        #     raise KeyError("Check ['releases']['tender']['parties'][*][´details']['permits']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into release_parties_array[´details']['bankAccounts'].
        #     """
        #     list_of_release_party_details_bank_accounts_name = list()
        #     for party_object in release_parties_array:
        #         for i in party_object['details']['bankAccounts']:
        #             for i_1 in i:
        #                 if i_1 == "bankName":
        #                     list_of_release_party_details_bank_accounts_name.append(i_1)
        #     quantity_of_party_details_bank_accounts_objects_into_release = \
        #         len(list_of_release_party_details_bank_accounts_name)
        # except KeyError:
        #     raise KeyError("Check ['releases']['tender']['parties'][*][´details']['bankAccounts']['bankName']")
        #
        # try:
        #     """
        #     Check how many quantity of object into release_parties_array[´details']['bankAccounts'][
        #     'additionalAccountIdentifiers'].
        #     """
        #     list_of_release_party_details_bank_accounts_additional_account_id = list()
        #     for party_object in release_parties_array:
        #         for i in party_object['details']['bankAccounts']:
        #             for i_1 in i:
        #                 if i_1 == "additionalAccountIdentifiers":
        #                     for i_2 in i['additionalAccountIdentifiers']:
        #                         for i_3 in i_2:
        #                             if i_3 == "id":
        #                                 list_of_release_party_details_bank_accounts_additional_account_id.append(i_3)
        #     quantity_of_party_details_bank_accounts_additional_account_objects_into_release = \
        #         len(list_of_release_party_details_bank_accounts_additional_account_id)
        # except KeyError:
        #     raise KeyError(
        #         "Check ['releases']['tender']['parties'][*][´details']['bankAccounts']["
        #         "'additionalAccountIdentifiers']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into release_parties_array['persones'].
        #     """
        #     list_of_release_party_persones_id = list()
        #     for party_object in release_parties_array:
        #         for i in party_object['persones']:
        #             for i_1 in i['identifier']:
        #                 if i_1 == "id":
        #                     list_of_release_party_persones_id.append(i_1)
        #     quantity_of_party_persones_into_release = \
        #         len(list_of_release_party_persones_id)
        # except KeyError:
        #     raise KeyError("Check ['releases']['tender']['parties'][*]['persones']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into release_parties_array['persones']['businessFunctions'].
        #     Check ['persones']['businessFunctions'][*]['id'] -> is it uuid.
        #     """
        #     list_of_release_party_persones_business_functions_id = list()
        #     for party_object in release_parties_array:
        #         for i in party_object['persones']:
        #             for i_1 in i['businessFunctions']:
        #                 for i_2 in i_1:
        #                     if i_2 == "id":
        #                         list_of_release_party_persones_business_functions_id.append(i_2)
        #                         try:
        #                             is_it_uuid(
        #                                 uuid_to_test=i_1['id'],
        #                                 version=4
        #                             )
        #                         except ValueError:
        #                             raise ValueError("Check your businessFunctions array in release: "
        #                                              "['persones']['businessFunctions'][*]['id'] in release "
        #                                              "must be uuid version 4")
        #     quantity_of_party_persones_business_functions_into_release = \
        #         len(list_of_release_party_persones_business_functions_id)
        # except KeyError:
        #     raise KeyError("Check ['releases']['tender']['parties'][*]['persones']['id']")
        #
        # try:
        #     """
        #     Check how many quantity of object into release_parties_array['persones']['businessFunctions']['documents'].
        #     """
        #     list_of_release_party_persones_business_functions_documents_id = list()
        #     for party_object in release_parties_array:
        #         for i in party_object['persones']:
        #             for i_1 in i['businessFunctions']:
        #                 for i_2 in i_1:
        #                     if i_2 == "documents":
        #                         for i_3 in i_1['documents']:
        #                             for i_4 in i_3:
        #                                 if i_4 == "id":
        #                                     list_of_release_party_persones_business_functions_documents_id.append(i_4)
        #     quantity_of_party_persones_business_functions_documents_into_release = \
        #         len(list_of_release_party_persones_business_functions_documents_id)
        # except KeyError:
        #     raise KeyError("Check ['releases']['tender']['parties'][*]['persones']['id']")
        #
        # try:
        #     """
        #     Compare quantity of lot objects into payload_lots_array and release_lots_array.
        #     """
        #     if quantity_of_tender_object_into_payload == quantity_of_party_object_into_release:
        #         pass
        # except KeyError:
        #     raise KeyError("Quantity of tenderers objects into payload_tenderers_array != "
        #                    "quantity of parties objects into release_parties_array")
        #
        # try:
        #     """
        #     Compare quantity of lot objects into payload_lots_array['additionalIdentifiers'] and
        #     release_lots_array['additionalIdentifiers'].
        #     """
        #     if quantity_of_tender_additional_identifiers_objects_into_payload == \
        #             quantity_of_party_additional_identifiers_objects_into_release:
        #         pass
        # except KeyError:
        #     raise KeyError("Quantity of tenderers objects into payload_tenderers_array['additionalIdentifiers'] != "
        #                    "quantity of parties objects into release_parties_array['additionalIdentifiers']")
        #
        # try:
        #     """
        #     Compare quantity of lot objects into payload_lots_array[´details']['mainEconomicActivities'] and
        #     release_lots_array[´details']['mainEconomicActivities'].
        #     """
        #     if quantity_of_tender_details_main_economic_activities_objects_into_payload == \
        #             quantity_of_party_details_main_economic_activities_objects_into_release:
        #         pass
        # except KeyError:
        #     raise KeyError("Quantity of tenderers objects into payload_tenderers_array[´details']"
        #                    "['mainEconomicActivities']!= quantity of parties objects into "
        #                    "release_parties_array[´details']['mainEconomicActivities']")
        #
        # try:
        #     """
        #     Compare quantity of lot objects into payload_lots_array[´details']['permits'] and
        #     release_lots_array[´details']['permits'].
        #     """
        #     if quantity_of_tender_details_parmits_objects_into_payload == \
        #             quantity_of_party_details_permits_objects_into_release:
        #         pass
        # except KeyError:
        #     raise KeyError("Quantity of tenderers objects into payload_tenderers_array[´details']"
        #                    "['permits']!= quantity of parties objects into "
        #                    "release_parties_array[´details']['permits']")
        #
        # try:
        #     """
        #     Compare quantity of lot objects into payload_lots_array[´details']['bankAccounts'] and
        #     release_lots_array[´details']['bankAccounts'].
        #     """
        #     if quantity_of_tender_details_bank_accounts_objects_into_payload == \
        #             quantity_of_party_details_bank_accounts_objects_into_release:
        #         pass
        # except KeyError:
        #     raise KeyError("Quantity of tenderers objects into payload_tenderers_array[´details']"
        #                    "['bankAccounts']!= quantity of parties objects into "
        #                    "release_parties_array[´details']['banAccounts']")
        #
        # try:
        #     """
        #     Compare quantity of lot objects into payload_lots_array[´details']['bankAccounts'][
        #     'additionalAccountIdentifiers'] and
        #     release_lots_array[´details']['bankAccounts'][
        #     'additionalAccountIdentifiers'].
        #     """
        #     if quantity_of_tender_details_bank_accounts_additional_account_objects_into_payload == \
        #             quantity_of_party_details_bank_accounts_additional_account_objects_into_release:
        #         pass
        # except KeyError:
        #     raise KeyError("Quantity of tenderers objects into payload_tenderers_array[´details']"
        #                    "['bankAccounts']['additionalAccountIdentifiers']!= quantity of parties objects into "
        #                    "release_parties_array[´details']['banAccounts']['additionalAccountIdentifiers']")
        #
        # try:
        #     """
        #     Compare quantity of lot objects into payload_lots_array['persones'] and
        #     release_lots_array['persones'].
        #     """
        #     if quantity_of_tender_persones_objects_into_payload == \
        #             quantity_of_party_persones_into_release:
        #         pass
        # except KeyError:
        #     raise KeyError("Quantity of tenderers objects into payload_tenderers_array['persones'] != "
        #                    "quantity of parties objects into release_parties_array['persones']")
        #
        # try:
        #     """
        #     Compare quantity of lot objects into payload_lots_array['persones']['businessFunctions'] and
        #     release_lots_array['persones']['businessFunctions'].
        #     """
        #     if quantity_of_tender_persones_business_functions_objects_into_payload == \
        #             quantity_of_party_persones_business_functions_into_release:
        #         pass
        # except KeyError:
        #     raise KeyError("Quantity of tenderers objects into payload_tenderers_array['persones']["
        #                    "'businessFunctions'] != "
        #                    "quantity of parties objects into release_parties_array['persones']["
        #                    "'businessFunctions']")
        #
        # try:
        #     """
        #     Compare quantity of lot objects into payload_lots_array['persones']['businessFunctions']['documents] and
        #     release_lots_array['persones']['businessFunctions']['documents].
        #     """
        #     if quantity_of_tender_persones_business_functions_documents_objects_into_payload == \
        #             quantity_of_party_persones_business_functions_documents_into_release:
        #         pass
        # except KeyError:
        #     raise KeyError("Quantity of tenderers objects into payload_tenderers_array['persones']["
        #                    "'businessFunctions']['documents] != "
        #                    "quantity of parties objects into release_parties_array['persones']["
        #                    "'businessFunctions']['documents]")
        #
        # try:
        #     """
        #     Prepare parties array framework.
        #     """
        #     quantity_one = quantity_of_party_object_into_release
        #     while quantity_one > 0:
        #         party_object = {}
        #         party_object.update(self.constructor.ev_release_parties_object())
        #
        #         expected_lots_array.append(lot_object)
        #         quantity_one -= 1
        # except ValueError:
        #     raise ValueError("Impossible to build expected lots array framework.")

        return quantity_of_tender_additional_identifiers_objects_into_payload, \
               quantity_of_tender_details_main_economic_activities_objects_into_payload, \
               quantity_of_tender_details_parmits_objects_into_payload, \
               quantity_of_tender_details_bank_accounts_objects_into_payload, \
               quantity_of_tender_details_bank_accounts_additional_account_objects_into_payload, \
               quantity_of_tender_persones_objects_into_payload, \
               quantity_of_tender_persones_business_functions_objects_into_payload, \
               quantity_of_tender_persones_business_functions_documents_objects_into_payload
