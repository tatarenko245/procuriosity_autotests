"""Prepare criteria array."""
import copy

from tests.utils.date_class import Date
from tests.utils.functions_collection.functions import set_eligibility_evidences_unique_temporary_id, \
    set_criteria_array_unique_temporary_id
from tests.utils.iStorage import Document
from tests.utils.services.e_mdm_service import MdmService


class CriteriaArray:
    """This class prepares instance of criteria."""

    def __init__(self, host_to_service, country, language, environment, quantity_of_criteria_objects,
                 quantity_of_requirementGroups_objects, quantity_of_requirements_objects,
                 quantity_of_eligibleEvidences_objects, type_of_standardCriteria):

        self.host_to_service = host_to_service
        self.country = country
        self.language = language
        self.environment = environment
        self.quantity_of_criteria_objects = quantity_of_criteria_objects
        self.quantity_of_requirementGroups_objects = quantity_of_requirementGroups_objects
        self.quantity_of_requirements_objects = quantity_of_requirements_objects
        self.quantity_of_eligibleEvidences_objects = quantity_of_eligibleEvidences_objects
        self.type_of_standardCriteria = type_of_standardCriteria

        self.standard_criteria = MdmService(host_to_service, environment).get_standard_criteria(country, language)

        self.criteria_array = [{
            "id": "0",
            "title": "",
            "description": "",
            "relatesTo": "",
            "requirementGroups": [{
                "id": "0-0",
                "description": "",
                "requirements": [{
                    "id": "0-0-0",
                    "title": "",

                    "description": "",
                    "dataType": "",
                    "period": {
                        "startDate": "",
                        "endDate": ""
                    },
                    "expectedValue": True,
                    "minValue": 0.99,
                    "maxValue": 99.99,
                    "eligibleEvidences": [{
                        "id": "0-0-0-0",
                        "title": "",
                        "description": "",
                        "type": "document",
                        "relatedDocument": {
                            "id": ""
                        }
                    }]
                }]
            }],
            "classification": {
                "id": "",
                "scheme": ""
            }
        }]

    def delete_optional_fields(
            self, *args, criteria_position=0, requirementGroups_position=0, requirements_position=0,
            eligibleEvidences_position=0):
        """Delete optional fields."""

        for a in args:
            if a == "criteria.description":
                del self.criteria_array[criteria_position]['description']
            elif a == "criteria.requirementGroups.description":
                del self.criteria_array[criteria_position]['requirementGroups'][requirementGroups_position][
                    'description']
            elif a == "criteria.requirementGroups.requirements.description":
                del self.criteria_array[criteria_position]['requirementGroups'][requirementGroups_position][
                    'requirements'][requirements_position]['description']
            elif a == "criteria.requirementGroups.requirements.period":
                del self.criteria_array[criteria_position]['requirementGroups'][requirementGroups_position][
                    'requirements'][requirements_position]['period']
            elif a == "criteria.requirementGroups.requirements.expectedValue":
                del self.criteria_array[criteria_position]['requirementGroups'][requirementGroups_position][
                    'requirements'][requirements_position]['expectedValue']
            elif a == "criteria.requirementGroups.requirements.minValue":
                del self.criteria_array[criteria_position]['requirementGroups'][requirementGroups_position][
                    'requirements'][requirements_position]['minValue']
            elif a == "criteria.requirementGroups.requirements.maxValue":
                del self.criteria_array[criteria_position]['requirementGroups'][requirementGroups_position][
                    'requirements'][requirements_position]['maxValue']
            elif a == "criteria.requirementGroups.requirements.eligibleEvidences":
                del self.criteria_array[criteria_position]['requirementGroups'][requirementGroups_position][
                    'requirements'][requirements_position]['eligibleEvidences']
            elif a == "criteria.requirementGroups.requirements.eligibleEvidences.description":
                del self.criteria_array[criteria_position]['requirementGroups'][requirementGroups_position][
                    'requirements'][requirements_position]['eligibleEvidences'][eligibleEvidences_position][
                    'description']
            elif a == "criteria.requirementGroups.requirements.eligibleEvidences.relatedDocument":
                del self.criteria_array[criteria_position]['requirementGroups'][requirementGroups_position][
                    'requirements'][requirements_position]['eligibleEvidences'][eligibleEvidences_position][
                    'relatedDocument']

    def prepare_criteria_array(self, criteria_relatesTo):
        """Prepare criteria array."""

        new_criteria_array = list()

        for q_0 in range(self.quantity_of_criteria_objects):
            new_criteria_object = copy.deepcopy(self.criteria_array[0])

            new_criteria_object['id'] = str(q_0).zfill(3)

            new_criteria_object['title'] = f"criteria[{q_0}.title"

            if "description" in new_criteria_object:
                new_criteria_object['description'] = f"criteria[{q_0}.description"

            new_criteria_object['relatesTo'] = criteria_relatesTo

            new_criteria_object['classification'] = self.standard_criteria[self.type_of_standardCriteria][q_0]

            new_requirementGroups_array = list()
            for q_1 in range(self.quantity_of_requirementGroups_objects):
                new_requirementGroups_object = (
                    copy.deepcopy(self.criteria_array[0]['requirementGroups'][0]))

                new_requirementGroups_object['id'] = f"{q_1}"

                if "description" in new_requirementGroups_object:
                    new_requirementGroups_object['description'] = \
                        f"criteria[{q_0}].requirementGroups[{q_1}].description"

                new_requirements_array = list()
                for q_2 in range(self.quantity_of_requirements_objects):
                    new_requirements_object = (copy.deepcopy(
                        self.criteria_array[0]['requirementGroups'][0]['requirements'][0]))

                    new_requirements_object['id'] = f"{q_2}"

                    new_requirements_object['title'] = \
                        f"criteria[{q_0}].requirementGroups[{q_1}].requirements[{q_2}].title"

                    if "description" in new_requirements_object:
                        new_requirements_object['description'] = \
                            f"criteria[{q_0}].requirementGroups[{q_1}].requirements[{q_2}].description"

                    if "period" in new_requirements_object:
                        date = Date()
                        period_for_requirement_object = date.old_period()
                        new_requirements_object['period']['startDate'] = period_for_requirement_object[0]
                        new_requirements_object['period']['endDate'] = period_for_requirement_object[1]

                    if "expectedValue" in new_requirements_object:
                        new_requirements_object['dataType'] = "boolean"
                    elif "minValue" in new_requirements_object and "maxValue" in new_requirements_object:
                        new_requirements_object['dataType'] = "number"
                        new_requirements_object['minValue'] += q_2
                        new_requirements_object['maxValue'] += q_2
                    elif "minValue" in new_requirements_object:
                        new_requirements_object['minValue'] += q_2
                        new_requirements_object['dataType'] = "number"
                    elif "maxValue" in new_requirements_object:
                        new_requirements_object['maxValue'] += q_2
                        new_requirements_object['dataType'] = "number"
                    else:
                        raise KeyError(f"Mismatch key 'expectedValue', 'minValue', 'maxValue'.")

                    if "eligibleEvidences" in new_requirements_object:
                        new_eligibleEvidences_array = list()
                        for q_3 in range(self.quantity_of_eligibleEvidences_objects):
                            new_eligibleEvidences_object = (copy.deepcopy(
                                self.criteria_array[0]['requirementGroups'][0]['requirements'][0][
                                    'eligibleEvidences'][0]))

                            new_eligibleEvidences_object['id'] = f"{q_3}"

                            new_eligibleEvidences_object['title'] = \
                                f"criteria[{q_0}].requirementGroups[{q_1}]." \
                                f"requirements[{q_2}].eligibleEvidences[{q_3}].title"

                            if "description" in new_eligibleEvidences_object:
                                new_eligibleEvidences_object['description'] = \
                                    f"criteria[{q_0}].requirementGroups[{q_1}]." \
                                    f"requirements[{q_2}].eligibleEvidences[{q_3}].description"

                            new_eligibleEvidences_object['type'] = "document"

                            if "relatedDocument" in new_eligibleEvidences_object:
                                document = Document(self.host_to_service)
                                document_was_uploaded = document.uploading_document()
                                new_eligibleEvidences_object['relatedDocument']['id'] = \
                                    document_was_uploaded[0]["data"]["id"]

                            new_eligibleEvidences_array.append(new_eligibleEvidences_object)

                        new_requirements_object['eligibleEvidences'] = new_eligibleEvidences_array
                    new_requirements_array.append(new_requirements_object)

                new_requirementGroups_object['requirements'] = new_requirements_array
                new_requirementGroups_array.append(new_requirementGroups_object)

            new_criteria_object['requirementGroups'] = new_requirementGroups_array
            new_criteria_array.append(new_criteria_object)

        self.criteria_array = new_criteria_array

    def set_unique_temporary_id_for_eligibleEvidences(self):
        """At first prepare all criteria array. Then set unique id."""
        new_criteria_array_with_unique_id = set_eligibility_evidences_unique_temporary_id(self.criteria_array)
        self.criteria_array = new_criteria_array_with_unique_id

    def set_unique_temporary_id_for_criteria(self):
        """At first prepare all criteria array. Then set unique id."""
        new_criteria_array_with_unique_id = set_criteria_array_unique_temporary_id(self.criteria_array)
        self.criteria_array = new_criteria_array_with_unique_id

    def build_criteria_array(self):
        """Build criteria array"""
        return self.criteria_array
