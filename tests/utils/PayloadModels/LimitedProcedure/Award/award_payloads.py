import copy
import random

from tests.utils.PayloadModels.LimitedProcedure.Award.award_payload_library import PayloadLibrary
from tests.utils.data_of_enum import scale_tuple, person_title_tuple, business_function_type_tuple, type_of_supplier_tuple, \
    documentType_for_create_award_of_limited_procedure_tuple
from tests.utils.date_class import Date
from tests.utils.iStorage import Document


class AwardPayloads:
    def __init__(self, host_for_services, currency):
        self.constructor = copy.deepcopy(PayloadLibrary())

        self.document_class = Document(host=host_for_services, file_name="API.pdf")

        date_class = Date()
        self.business_function_period = date_class.old_period()
        self.duration_period = date_class.duration_period()
        self.currency = currency

    def create_award_full_data_model(
            self, quantity_of_suppliers_objects=1,
            quantity_of_suppliers_additionalIdentifiers_objects=1,
            quantity_of_suppliers_persones_objects=1,
            quantity_of_suppliers_persones_businessFunctions_objects=1,
            quantity_of_suppliers_persones_businessFunctions_documents_objects=1,
            quantity_of_suppliers_details_mainEconomicActivities_objects=1,
            quantity_of_suppliers_details_permits=1,
            quantity_of_suppliers_details_bankAccounts_objects=1,
            quantity_of_suppliers_details_bankAccounts_additionalAccountIdentifiers_objects=1,
            quantity_of_documents_objects=1):

        payload = self.constructor.create_award_object()

        payload['award']['internalId'] = "create award: internalId 1"
        payload['award']['description'] = "create award: description 1"
        payload['award']['value']['amount'] = 888.89
        payload['award']['value']['currency'] = self.currency

        payload['award']['suppliers'] = list()
        for supplier in range(quantity_of_suppliers_objects):

            payload['award']['suppliers'].append(self.constructor.create_award_suppliers_object())

            payload['award']['suppliers'][supplier]['name'] = f"create award: award.suppliers{supplier}.name"

            payload['award']['suppliers'][supplier]['identifier']['id'] = \
                f"create award: award.suppliers{supplier}.identifier.id"

            payload['award']['suppliers'][supplier]['identifier']['legalName'] = \
                f"create award: award.suppliers{supplier}.identifier.legalName"

            payload['award']['suppliers'][supplier]['identifier']['scheme'] = "MD-IDNO"

            payload['award']['suppliers'][supplier]['identifier']['uri'] = \
                f"create award: award.suppliers{supplier}.identifier.uri"

            payload['award']['suppliers'][supplier]['additionalIdentifiers'] = list()
            for additionalIdentifier in range(quantity_of_suppliers_additionalIdentifiers_objects):

                payload['award']['suppliers'][supplier]['additionalIdentifiers'].append(
                    self.constructor.create_award_suppliers_additionalIdentifiers_object())

                payload['award']['suppliers'][supplier]['additionalIdentifiers'][additionalIdentifier]['id'] = \
                    f"create award: award.suppliers{supplier}.additionalIdentifiers{additionalIdentifier}.id"

                payload['award']['suppliers'][supplier]['additionalIdentifiers'][additionalIdentifier]['legalName'] = \
                    f"create award: award.suppliers{supplier}.additionalIdentifiers{additionalIdentifier}.legalName"

                payload['award']['suppliers'][supplier]['additionalIdentifiers'][additionalIdentifier]['scheme'] = \
                    f"create award: award.suppliers{supplier}.additionalIdentifiers{additionalIdentifier}.scheme"

                payload['award']['suppliers'][supplier]['additionalIdentifiers'][additionalIdentifier]['uri'] = \
                    f"create award: award.suppliers{supplier}.additionalIdentifiers{additionalIdentifier}.uri"

            payload['award']['suppliers'][supplier]['address']['streetAddress'] = \
                f"create award: award.suppliers{supplier}.address.streetAddress"

            payload['award']['suppliers'][supplier]['address']['postalCode'] = \
                f"create award: award.suppliers{supplier}.address.postalCode"

            payload['award']['suppliers'][supplier]['address']['addressDetails']['country']['id'] = "MD"
            payload['award']['suppliers'][supplier]['address']['addressDetails']['country']['scheme'] = "iso-alpha2"

            payload['award']['suppliers'][supplier]['address']['addressDetails']['country'][
                'description'] = f"create award: award.suppliers{supplier}.address.addressDetails.country.description"

            payload['award']['suppliers'][supplier]['address']['addressDetails']['region']['id'] = "1700000"
            payload['award']['suppliers'][supplier]['address']['addressDetails']['region']['scheme'] = "CUATM"

            payload['award']['suppliers'][supplier]['address']['addressDetails']['region'][
                'description'] = f"create award: award.suppliers{supplier}.address.addressDetails.region.description"

            payload['award']['suppliers'][supplier]['address']['addressDetails']['locality']['id'] = "1701000"
            payload['award']['suppliers'][supplier]['address']['addressDetails']['locality']['scheme'] = "CUATM"

            payload['award']['suppliers'][supplier]['address']['addressDetails']['locality'][
                'description'] = f"create award: award.suppliers{supplier}.address.addressDetails.locality.description"

            payload['award']['suppliers'][supplier]['contactPoint']['name'] = \
                f"create award: award.suppliers{supplier}.contactPoint.name"

            payload['award']['suppliers'][supplier]['contactPoint']['email'] = \
                f"create award: award.suppliers{supplier}.contactPoint.email"

            payload['award']['suppliers'][supplier]['contactPoint']['telephone'] = \
                f"create award: award.suppliers{supplier}.contactPoint.telephone"

            payload['award']['suppliers'][supplier]['contactPoint']['faxNumber'] = \
                f"create award: award.suppliers{supplier}.contactPoint.faxNumber"

            payload['award']['suppliers'][supplier]['contactPoint']['url'] = \
                f"create award: award.suppliers{supplier}.contactPoint.url"

            payload['award']['suppliers'][supplier]['persones'] = list()
            for person in range(quantity_of_suppliers_persones_objects):

                payload['award']['suppliers'][supplier]['persones'].append(
                    self.constructor.create_award_suppliers_persones_object())

                payload['award']['suppliers'][supplier]['persones'][person]['title'] = f"{random.choice(person_title_tuple)}"

                payload['award']['suppliers'][supplier]['persones'][person]['name'] = \
                    f"create award: award.suppliers{supplier}.persones{person}.name"

                payload['award']['suppliers'][supplier]['persones'][person]['identifier']['scheme'] = "MD-IDNO"

                payload['award']['suppliers'][supplier]['persones'][person]['identifier'][
                    'id'] = f"create award: award.suppliers{supplier}.persones{person}.identifier.id"

                payload['award']['suppliers'][supplier]['persones'][person]['identifier'][
                    'uri'] = f"create award: award.suppliers{supplier}.persones{person}.identifier.uri"

                payload['award']['suppliers'][supplier]['persones'][person]['businessFunctions'] = list()
                for businessFunction in range(quantity_of_suppliers_persones_businessFunctions_objects):

                    payload['award']['suppliers'][supplier]['persones'][person]['businessFunctions'].append(
                        self.constructor.create_award_suppliers_persones_businessFunctions_object())

                    payload['award']['suppliers'][supplier]['persones'][person][
                        'businessFunctions'][businessFunction]['id'] = \
                        f"create award: award.suppliers{supplier}.persones{person}." \
                        f"businessFunctions{businessFunction}.id"

                    payload['award']['suppliers'][supplier]['persones'][person][
                        'businessFunctions'][businessFunction]['type'] = f"{random.choice(business_function_type_tuple)}"

                    payload['award']['suppliers'][supplier]['persones'][person][
                        'businessFunctions'][businessFunction]['jobTitle'] = \
                        f"create award: award.suppliers{supplier}.persones{person}." \
                        f"businessFunctions{businessFunction}.jobTitle"

                    payload['award']['suppliers'][supplier]['persones'][person][
                        'businessFunctions'][businessFunction]['period']['startDate'] = self.business_function_period[0]

                    payload['award']['suppliers'][supplier]['persones'][person]['businessFunctions'][
                        businessFunction]['documents'] = list()

                    for businessFunction_document in range(
                            quantity_of_suppliers_persones_businessFunctions_documents_objects):
                        document_was_uploaded = self.document_class.uploading_document()

                        payload['award']['suppliers'][supplier]['persones'][person]['businessFunctions'][
                            businessFunction]['documents'].append(
                            self.constructor.create_award_suppliers_persones_businessFunctions_documents_object())

                        payload['award']['suppliers'][supplier]['persones'][person]['businessFunctions'][
                            businessFunction]['documents'][businessFunction_document]['documentType'] = \
                            "regulatoryDocument"

                        payload['award']['suppliers'][supplier]['persones'][person]['businessFunctions'][
                            businessFunction]['documents'][businessFunction_document]['id'] = \
                            document_was_uploaded[0]['data']['id']

                        payload['award']['suppliers'][supplier]['persones'][person]['businessFunctions'][
                            businessFunction]['documents'][businessFunction_document]['title'] = \
                            f"create award: award.suppliers{supplier}.persones{person}." \
                            f"businessFunctions{businessFunction}.documents{businessFunction_document}.title"

                        payload['award']['suppliers'][supplier]['persones'][person]['businessFunctions'][
                            businessFunction]['documents'][businessFunction_document]['description'] = \
                            f"create award: award.suppliers{supplier}.persones{person}." \
                            f"businessFunctions{businessFunction}.documents{businessFunction_document}.description"

            payload['award']['suppliers'][supplier]['details']['typeOfSupplier'] = f"{random.choice(type_of_supplier_tuple)}"

            payload['award']['suppliers'][supplier]['details']['mainEconomicActivities'] = list()
            for mainEconomicActivity in range(quantity_of_suppliers_details_mainEconomicActivities_objects):

                payload['award']['suppliers'][supplier]['details']['mainEconomicActivities'].append(
                    self.constructor.create_award_suppliers_details_mainEconomicActivities_object())

                payload['award']['suppliers'][supplier]['details'][
                    'mainEconomicActivities'][mainEconomicActivity]['id'] = \
                    f"create award: award.supplers{supplier}.details.mainEconomicActivities{mainEconomicActivity}.id"

                payload['award']['suppliers'][supplier]['details'][
                    'mainEconomicActivities'][mainEconomicActivity]['scheme'] = \
                    f"create award: award.supplers{supplier}.details.mainEconomicActivities{mainEconomicActivity}." \
                    f"scheme"

                payload['award']['suppliers'][supplier]['details'][
                    'mainEconomicActivities'][mainEconomicActivity]['description'] = \
                    f"create award: award.supplers{supplier}.details.mainEconomicActivities{mainEconomicActivity}." \
                    f"description"

                payload['award']['suppliers'][supplier]['details'][
                    'mainEconomicActivities'][mainEconomicActivity]['uri'] = \
                    f"create award: award.suppliers{supplier}.details.mainEconomicActivities{mainEconomicActivity}.uri"

            payload['award']['suppliers'][supplier]['details']['scale'] = f"{random.choice(scale_tuple)}"

            payload['award']['suppliers'][supplier]['details']['permits'] = list()
            for permit in range(quantity_of_suppliers_details_permits):

                payload['award']['suppliers'][supplier]['details']['permits'].append(
                    self.constructor.create_award_suppliers_details_permits_object())

                payload['award']['suppliers'][supplier]['details']['permits'][permit]['scheme'] = \
                    f"create award: award.suppliers{supplier}.details.permits{permit}.scheme"

                payload['award']['suppliers'][supplier]['details']['permits'][permit]['id'] = \
                    f"create award: award.suppliers{supplier}.details.permits{permit}.id"

                payload['award']['suppliers'][supplier]['details']['permits'][permit]['url'] = \
                    f"create award: award.suppliers{supplier}.details.permits{permit}.url"

                payload['award']['suppliers'][supplier]['details']['permits'][permit]['permitDetails'][
                    'issuedBy']['id'] = \
                    f"create award: award.suppliers{supplier}.details.permits{permit}.permitDetail.issuedBy.id"

                payload['award']['suppliers'][supplier]['details']['permits'][permit]['permitDetails'][
                    'issuedBy']['name'] = \
                    f"create award: award.suppliers{supplier}.details.permits{permit}.permitDetail.issuedBy.name"

                payload['award']['suppliers'][supplier]['details']['permits'][permit]['permitDetails'][
                    'issuedThought']['id'] = \
                    f"create award: award.suppliers{supplier}.details.permits{permit}.permitDetail.issuedThought.id"

                payload['award']['suppliers'][supplier]['details']['permits'][permit]['permitDetails'][
                    'issuedThought']['name'] = \
                    f"create award: award.suppliers{supplier}.details.permits{permit}.permitDetail.issuedThought.name"

                payload['award']['suppliers'][supplier]['details']['permits'][permit]['permitDetails'][
                    'validityPeriod']['startDate'] = self.duration_period[0]

                payload['award']['suppliers'][supplier]['details']['permits'][permit]['permitDetails'][
                    'validityPeriod']['endDate'] = self.duration_period[1]

            payload['award']['suppliers'][supplier]['details']['bankAccounts'] = list()
            for bankAccount in range(quantity_of_suppliers_details_bankAccounts_objects):

                payload['award']['suppliers'][supplier]['details']['bankAccounts'].append(
                    self.constructor.create_award_suppliers_details_bankAccounts_object())

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount]['description'] = \
                    f"create award: award.suppliers{supplier}.details.bankAccounts{bankAccount}.description"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount]['bankName'] = \
                    f"create award: award.suppliers{supplier}.details.bankAccounts{bankAccount}.bankName"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'address']['streetAddress'] = \
                    f"create award: award.suppliers{supplier}.details.bankAccounts{bankAccount}.address.streetAddress"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'address']['postalCode'] = \
                    f"create award: award.suppliers{supplier}.details.bankAccounts{bankAccount}.address.postalCode"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'address']['addressDetails']['country']['id'] = "MD"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'address']['addressDetails']['country']['scheme'] = "iso-alpha2"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'address']['addressDetails']['country']['description'] = \
                    f"create award: award.suppliers{supplier}.details.bankAccounts{bankAccount}.address." \
                    f"addressDetails.country.description"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'address']['addressDetails']['region']['id'] = "3400000"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'address']['addressDetails']['region']['scheme'] = "CUATM"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'address']['addressDetails']['region']['description'] = \
                    f"create award: award.suppliers{supplier}.details.bankAccounts{bankAccount}.address." \
                    f"addressDetails.region.description"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'address']['addressDetails']['locality']['id'] = "3401000"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'address']['addressDetails']['locality']['scheme'] = "other"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'address']['addressDetails']['locality']['description'] = \
                    f"create award: award.suppliers{supplier}.details.bankAccounts{bankAccount}.address." \
                    f"addressDetails.locality.description"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'identifier']['scheme'] = "UA-MFO"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'identifier']['id'] = \
                    f"create award: award.suppliers{supplier}.details.bankAccounts{bankAccount}.identifier.id"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'accountIdentification']['scheme'] = "IBAN"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'accountIdentification']['id'] = \
                    f"create award: award.suppliers{supplier}.details.bankAccounts{bankAccount}." \
                    f"accountIdentification.id"

                payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                    'additionalAccountIdentifiers'] = list()

                for additionalAccountIdentifier in range(
                        quantity_of_suppliers_details_bankAccounts_additionalAccountIdentifiers_objects):

                    payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                        'additionalAccountIdentifiers'].append(
                        self.constructor.create_award_suppliers_details_bankAccounts_additionalAccountIdentifiers_object())

                    payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                        'additionalAccountIdentifiers'][additionalAccountIdentifier]['scheme'] = "fiscal"

                    payload['award']['suppliers'][supplier]['details']['bankAccounts'][bankAccount][
                        'additionalAccountIdentifiers'][additionalAccountIdentifier]['id'] = \
                        f"create award: award.suppliers{supplier}.details.bankAccounts{bankAccount}." \
                        f"additionalAccountIdentifiers{additionalAccountIdentifier}.id"

            payload['award']['suppliers'][supplier]['details']['legalForm']['scheme'] = "MD-CFOJ"

            payload['award']['suppliers'][supplier]['details']['legalForm']['id'] = \
                f"create award: award.suppliers{supplier}.details.legalForm.id"

            payload['award']['suppliers'][supplier]['details']['legalForm']['description'] = \
                f"create award: award.suppliers{supplier}.details.legalForm.description"

            payload['award']['suppliers'][supplier]['details']['legalForm']['uri'] = \
                f"create award: award.suppliers{supplier}.details.legalForm.uri"

        payload['award']['documents'] = list()
        for document in range(quantity_of_documents_objects):
            document_was_uploaded = self.document_class.uploading_document()
            payload['award']['documents'].append(self.constructor.create_award_documents_object())
            payload['award']['documents'][document]['id'] = document_was_uploaded[0]['data']['id']
            payload['award']['documents'][document]['title'] = f"create award: award.documents{document}.title"

            payload['award']['documents'][document]['description'] = \
                f"create award: award.documents{document}.description"

            payload['award']['documents'][document]['documentType'] = \
                f"{random.choice(documentType_for_create_award_of_limited_procedure_tuple)}"
        return payload

    def create_award_obligatory_data_model(self, quantity_of_suppliers_objects=1, need_to_value_amount=False):
        payload = self.constructor.create_award_object()

        del payload['award']['internalId']
        del payload['award']['description']
        del payload['award']['documents']

        if need_to_value_amount is False:
            del payload['award']['value']['amount']
        else:
            payload['award']['value']['amount'] = 888.89

        payload['award']['value']['currency'] = self.currency

        payload['award']['suppliers'] = list()
        for supplier in range(quantity_of_suppliers_objects):
            payload['award']['suppliers'].append(self.constructor.create_award_suppliers_object())

            del payload['award']['suppliers'][supplier]['identifier']['uri']
            del payload['award']['suppliers'][supplier]['additionalIdentifiers']
            del payload['award']['suppliers'][supplier]['address']['postalCode']
            del payload['award']['suppliers'][supplier]['contactPoint']['faxNumber']
            del payload['award']['suppliers'][supplier]['contactPoint']['url']
            del payload['award']['suppliers'][supplier]['persones']
            del payload['award']['suppliers'][supplier]['details']['typeOfSupplier']
            del payload['award']['suppliers'][supplier]['details']['mainEconomicActivities']
            del payload['award']['suppliers'][supplier]['details']['permits']
            del payload['award']['suppliers'][supplier]['details']['bankAccounts']
            del payload['award']['suppliers'][supplier]['details']['legalForm']

            payload['award']['suppliers'][supplier]['name'] = f"create award: Name {supplier}"
            payload['award']['suppliers'][supplier]['identifier']['id'] = f"create award: id {supplier}"
            payload['award']['suppliers'][supplier]['identifier']['legalName'] = f"create award: lehalName {supplier}"
            payload['award']['suppliers'][supplier]['identifier']['scheme'] = "MD-IDNO"
            payload['award']['suppliers'][supplier]['address']['streetAddress'] = f"create award: street {supplier}"
            payload['award']['suppliers'][supplier]['address']['addressDetails']['country']['id'] = "MD"
            payload['award']['suppliers'][supplier]['address']['addressDetails']['country']['scheme'] = "iso-alpha2"

            payload['award']['suppliers'][supplier]['address']['addressDetails']['country']['description'] = \
                f"create award: kraina {supplier}"

            payload['award']['suppliers'][supplier]['address']['addressDetails']['region']['id'] = "1700000"
            payload['award']['suppliers'][supplier]['address']['addressDetails']['region']['scheme'] = "CUATM"

            payload['award']['suppliers'][supplier]['address']['addressDetails']['region']['description'] = \
                f"create award: region {supplier}"

            payload['award']['suppliers'][supplier]['address']['addressDetails']['locality']['id'] = "1701000"
            payload['award']['suppliers'][supplier]['address']['addressDetails']['locality']['scheme'] = "CUATM"

            payload['award']['suppliers'][supplier]['address']['addressDetails']['locality']['description'] = \
                f"create award: local {supplier}"

            payload['award']['suppliers'][supplier]['contactPoint']['name'] = f"create award: contact name {supplier}"
            payload['award']['suppliers'][supplier]['contactPoint']['email'] = f"create award: contact email {supplier}"

            payload['award']['suppliers'][supplier]['contactPoint']['telephone'] = \
                f"create award: contact telephone {supplier}"

            payload['award']['suppliers'][supplier]['details']['scale'] = f"{random.choice(scale_tuple)}"
        return payload

    def evaluate_award_full_data_model(self, award_statusDetails, lot_id, quantity_of_documents_objects=1):
        payload = self.constructor.evaluate_award_object()

        payload['award']['statusDetails'] = award_statusDetails
        payload['award']['description'] = "evaluate award: award.description"

        payload['award']['documents'] = list()
        for document in range(quantity_of_documents_objects):

            document_was_uploaded = self.document_class.uploading_document()

            payload['award']['documents'].append(self.constructor.evaluate_award_documents_object())

            payload['award']['documents'][document]['documentType'] = \
                f"{random.choice(documentType_for_create_award_of_limited_procedure_tuple)}"

            payload['award']['documents'][document]['id'] = document_was_uploaded[0]['data']['id']
            payload['award']['documents'][document]['title'] = f"evaluate award: award.documents{document}.title"

            payload['award']['documents'][document]['description'] = \
                f"evaluate award: award.documents{document}.description"

            payload['award']['documents'][document]['relatedLots'] = [lot_id]
            return payload

    def evaluate_award_obligatory_data_model(self, award_statusDetails):
        payload = self.constructor.evaluate_award_object()

        del payload['award']['description']
        del payload['award']['documents']

        payload['award']['statusDetails'] = award_statusDetails
        return payload


