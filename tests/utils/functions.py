import copy
import datetime
import fnmatch
import json
import random
from pathlib import Path
from uuid import UUID
import csv

import pytz
import xlrd
import allure
from tests.conftest import GlobalClassMetadata
from tests.utils.PayloadModel.SubmitBid.bid_payload_library import PayloadLibrary
from tests.utils.data_of_enum import cpv_goods_low_level_03, cpv_goods_low_level_1, cpv_goods_low_level_2, \
    cpv_goods_low_level_3, cpv_goods_low_level_44, cpv_goods_low_level_48, cpv_works_low_level_45, \
    cpv_services_low_level_5, cpv_services_low_level_6, cpv_services_low_level_7, cpv_services_low_level_8, \
    cpv_services_low_level_92, cpv_services_low_level_98
from tests.utils.date_class import Date
from tests.utils.services.e_mdm_service import MdmService
import time


@allure.step('Compare actual and expected results')
def compare_actual_result_and_expected_result(expected_result, actual_result):
    allure.attach(str(expected_result), "Expected result")
    allure.attach(str(actual_result), "Actual result")
    if expected_result == actual_result:
        return True
    else:
        return False


def is_it_uuid(uuid_to_test, version):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def get_value_from_classification_cpv_dictionary_xls(cpv, language):
    path = get_project_root()
    # Open current xlsx file.
    excel_data_file = xlrd.open_workbook(f'{path}/CPV_dictionary.xls')
    # Take current page of the file.
    sheet = excel_data_file.sheet_by_index(0)

    # classification_description = []
    # How mach rows contains into file?
    rows_number = sheet.nrows
    column_number = sheet.ncols
    requested_row = list()
    requested_column = list()
    if rows_number > 0:
        for row in range(0, rows_number):
            if cpv in sheet.row(row)[0].value:
                requested_row.append(row)

    if column_number > 0:
        for column in range(0, column_number):
            if language.upper() in sheet.col(column)[0].value:
                requested_column.append(column)
    new_cpv = sheet.cell_value(rowx=int(requested_row[0]), colx=0)
    description = sheet.cell_value(rowx=int(requested_row[0]), colx=int(requested_column[0]))
    return new_cpv, description


def get_value_from_cpvs_dictionary_csv(cpvs, language):
    path = get_project_root()
    with open(f'{path}/CPVS_dictionary.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            cur_arr = row[0].split(';')
            if cur_arr[0] == cpvs and cur_arr[3] == f'"{language}"':
                return cur_arr[0].replace('"', ''), cur_arr[1].replace('"', ''), cur_arr[2].replace('"', ''), cur_arr[
                    3].replace('"', '')


def get_value_from_classification_unit_dictionary_csv(unit_id, language):
    path = get_project_root()
    with open(f'{path}/Units_dictionary.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            cur_arr = row[0].split(',')
            if cur_arr[0] == f'{unit_id}' and cur_arr[4].replace(';', '') == f'"{language}"':
                return cur_arr[0].replace("'", ""), cur_arr[2].replace('"', ''),


def generate_items_array(quantity_of_object, item_object, tender_classification_id, lots_array=None):
    copy.deepcopy(item_object)
    items_array = []
    for i in range(quantity_of_object):
        item_json = copy.deepcopy(item_object)
        item_json['id'] = str(i)
        items_array.append(item_json)

    new_array_items = []
    for quantity_of_object in range(quantity_of_object):
        if lots_array is not None:
            for o in items_array:
                for r in o:
                    if r == "relatedLot":
                        items_array[quantity_of_object]['relatedLot'] = lots_array[quantity_of_object]['id']
                    else:
                        pass
        else:
            pass
        item_classification_id = None
        if tender_classification_id[0:2] == "03":
            item_classification_id = f"{random.choice(cpv_goods_low_level_03)}"
        elif tender_classification_id[0] == "1":
            item_classification_id = f"{random.choice(cpv_goods_low_level_1)}"
        elif tender_classification_id[0] == "2":
            item_classification_id = f"{random.choice(cpv_goods_low_level_2)}"
        elif tender_classification_id[0] == "3":
            item_classification_id = f"{random.choice(cpv_goods_low_level_3)}"
        elif tender_classification_id[0:2] == "44":
            item_classification_id = f"{random.choice(cpv_goods_low_level_44)}"
        elif tender_classification_id[0:2] == "48":
            item_classification_id = f"{random.choice(cpv_goods_low_level_48)}"
        elif tender_classification_id[0:2] == "45":
            item_classification_id = f"{random.choice(cpv_works_low_level_45)}"
        elif tender_classification_id[0] == "5":
            item_classification_id = f"{random.choice(cpv_services_low_level_5)}"
        elif tender_classification_id[0] == "6":
            item_classification_id = f"{random.choice(cpv_services_low_level_6)}"
        elif tender_classification_id[0] == "7":
            item_classification_id = f"{random.choice(cpv_services_low_level_7)}"
        elif tender_classification_id[0] == "8":
            item_classification_id = f"{random.choice(cpv_services_low_level_8)}"
        elif tender_classification_id[0:2] == "92":
            item_classification_id = f"{random.choice(cpv_services_low_level_92)}"
        elif tender_classification_id[0:2] == "98":
            item_classification_id = f"{random.choice(cpv_services_low_level_98)}"
        else:
            Exception("Error: check your 'tender.clasification.id'")
        items_array[quantity_of_object]['classification']['id'] = item_classification_id
        val = items_array[quantity_of_object]
        new_array_items.append(copy.deepcopy(val))
    return new_array_items


def generate_lots_array(quantity_of_object, lot_object):
    copy.deepcopy(lot_object)
    lots_array = []
    for i in range(quantity_of_object):
        lot_json = copy.deepcopy(lot_object)
        lot_json['id'] = str(i)
        lot_json['value']['amount'] = round(float(lot_object['value']['amount'] / quantity_of_object), 2)
        lots_array.append(lot_json)

    new_array_lots = []
    for quantity_of_object in range(quantity_of_object):
        val = lots_array[quantity_of_object]
        new_array_lots.append(copy.deepcopy(val))
    return new_array_lots


def generate_criteria_array(quantity_of_criteria_object, criteria_object, quantity_of_groups_object,
                            quantity_of_requirements_object, quantity_of_evidences_object, type_of_standard_criteria):
    copy.deepcopy(criteria_object)
    criteria_array = []
    for i in range(quantity_of_criteria_object):
        criteria_json = copy.deepcopy(criteria_object)
        criteria_json['id'] = str(i).zfill(3)

        criteria_json['requirementGroups'] = generate_criteria_requirement_groups_array(
            quantity_of_object=quantity_of_groups_object,
            requirement_groups_object=criteria_json['requirementGroups'][0],
            quantity_of_requirements_object=quantity_of_requirements_object,
            quantity_of_evidences_object=quantity_of_evidences_object,
        )
        for j in range(quantity_of_groups_object):
            criteria_json['requirementGroups'][j]['id'] = f"{criteria_json['id']}-{j}"
            for y in range(quantity_of_requirements_object):
                criteria_json['requirementGroups'][j]['requirements'][y]['id'] = \
                    f"{criteria_json['requirementGroups'][j]['id']}-{y}"
        criteria_array.append(criteria_json)

    standard_criteria = MdmService(host=GlobalClassMetadata.host_for_services).get_standard_criteria(
        country=GlobalClassMetadata.country,
        language=GlobalClassMetadata.language)

    new_array_criteria = []
    for quantity_of_object in range(quantity_of_criteria_object):
        criteria_array[quantity_of_object]['classification'] = \
            standard_criteria[type_of_standard_criteria][quantity_of_object]
        val = criteria_array[quantity_of_object]
        new_array_criteria.append(copy.deepcopy(val))
    return new_array_criteria


def generate_criteria_requirement_groups_array(quantity_of_object, requirement_groups_object,
                                               quantity_of_requirements_object, quantity_of_evidences_object):
    copy.deepcopy(requirement_groups_object)
    requirement_groups_array = []
    for i in range(quantity_of_object):
        requirement_groups_json = copy.deepcopy(requirement_groups_object)
        requirement_groups_json['id'] = str(i)
        requirement_groups_json['requirements'] = generate_criteria_requirement_groups_requirements(
            quantity_of_object=quantity_of_requirements_object,
            requirement_object=requirement_groups_json['requirements'][0],
            quantity_of_evidences_object=quantity_of_evidences_object)
        requirement_groups_array.append(requirement_groups_json)

    new_array_requirement_groups = []
    for quantity_of_object in range(quantity_of_object):
        val = requirement_groups_array[quantity_of_object]
        new_array_requirement_groups.append(copy.deepcopy(val))
    return new_array_requirement_groups


def generate_criteria_requirement_groups_requirements(
        quantity_of_object, requirement_object, quantity_of_evidences_object):
    copy.deepcopy(requirement_object)
    requirements_array = []
    for i in range(quantity_of_object):
        requirement_json = copy.deepcopy(requirement_object)
        requirement_json['id'] = str(i)
        requirement_json['eligibleEvidences'] = \
            generate_criteria_requirement_groups_requirements_eligible_evidences_array(
                quantity_of_object=quantity_of_evidences_object,
                eligible_evidences_object=requirement_json['eligibleEvidences'][0])
        requirements_array.append(requirement_json)

    new_array_requirements = []
    for quantity_of_object in range(quantity_of_object):
        val = requirements_array[quantity_of_object]
        new_array_requirements.append(copy.deepcopy(val))
    return new_array_requirements


def generate_criteria_requirement_groups_requirements_eligible_evidences_array(
        quantity_of_object, eligible_evidences_object):
    copy.deepcopy(eligible_evidences_object)
    eligible_evidences_array = []
    for i in range(quantity_of_object):
        eligible_evidences_json = copy.deepcopy(eligible_evidences_object)
        eligible_evidences_json['id'] = str(i)
        eligible_evidences_array.append(eligible_evidences_json)

    new_array_requirement_groups = []
    for quantity_of_object in range(quantity_of_object):
        val = eligible_evidences_array[quantity_of_object]
        new_array_requirement_groups.append(copy.deepcopy(val))

    return new_array_requirement_groups


# def generate_items_array(quantity_of_object, item_object, tender_classification_id):
#     copy.deepcopy(item_object)
#     items_array = [item_object for _ in range(quantity_of_object)]
#     id_set = set()
#     while len(id_set) < quantity_of_object:
#         id_list = list()
#         for i in items_array:
#             for keys, values in i.items():
#                 if keys == "id":
#                     values = random.randint(1, quantity_of_object + 1)
#                     id_list.append(values)
#
#         id_set = set(id_list)
#     correct_id_list = list(id_set)
#     new_array_items = list()
#     for quantity_of_object in range(quantity_of_object):
#         id_ = str(correct_id_list[quantity_of_object])
#         items_array[quantity_of_object]['id'] = id_
#         item_classification_id = None
#         if tender_classification_id[0:2] == "03":
#             item_classification_id = f"{random.choice(cpv_goods_low_level_03)}"
#         elif tender_classification_id[0] == "1":
#             item_classification_id = f"{random.choice(cpv_goods_low_level_1)}"
#         elif tender_classification_id[0] == "2":
#             item_classification_id = f"{random.choice(cpv_goods_low_level_2)}"
#         elif tender_classification_id[0] == "3":
#             item_classification_id = f"{random.choice(cpv_goods_low_level_3)}"
#         elif tender_classification_id[0:2] == "44":
#             item_classification_id = f"{random.choice(cpv_goods_low_level_44)}"
#         elif tender_classification_id[0:2] == "48":
#             item_classification_id = f"{random.choice(cpv_goods_low_level_48)}"
#         elif tender_classification_id[0:2] == "45":
#             item_classification_id = f"{random.choice(cpv_works_low_level_45)}"
#         elif tender_classification_id[0] == "5":
#             item_classification_id = f"{random.choice(cpv_services_low_level_5)}"
#         elif tender_classification_id[0] == "6":
#             item_classification_id = f"{random.choice(cpv_services_low_level_6)}"
#         elif tender_classification_id[0] == "7":
#             item_classification_id = f"{random.choice(cpv_services_low_level_7)}"
#         elif tender_classification_id[0] == "8":
#             item_classification_id = f"{random.choice(cpv_services_low_level_8)}"
#         elif tender_classification_id[0:2] == "92":
#             item_classification_id = f"{random.choice(cpv_services_low_level_92)}"
#         elif tender_classification_id[0:2] == "98":
#             item_classification_id = f"{random.choice(cpv_services_low_level_98)}"
#         else:
#             Exception("Error: check your 'tender.clasification.id'")
#         items_array[quantity_of_object]['classification']['id'] = item_classification_id
#         val = items_array[quantity_of_object]
#         new_array_items.append(copy.deepcopy(val))
#     return new_array_items


def generate_tender_classification_id(items_array):
    list_of_keys = list()
    list_of_values = list()
    for o in items_array:
        for id_ in o['classification']:
            if id_ == "id":
                list_of_keys.append(id_)
                list_of_values.append(o['classification']['id'])
    quantity = len(list_of_keys)
    if quantity >= 2:
        classification_1 = list_of_values[0]
        classification_2 = list_of_values[1]
        s_1 = fnmatch.fnmatch(classification_1[0], classification_2[0])
        s_2 = fnmatch.fnmatch(classification_1[1], classification_2[1])
        s_3 = fnmatch.fnmatch(classification_1[2], classification_2[2])
        s_4 = fnmatch.fnmatch(classification_1[3], classification_2[3])
        s_5 = fnmatch.fnmatch(classification_1[4], classification_2[4])
        s_6 = fnmatch.fnmatch(classification_1[5], classification_2[5])
        s_7 = fnmatch.fnmatch(classification_1[6], classification_2[6])
        s_8 = fnmatch.fnmatch(classification_1[7], classification_2[7])
        s_9 = fnmatch.fnmatch(classification_1[8], classification_2[8])
        s_10 = fnmatch.fnmatch(classification_1[9], classification_2[9])
        new = list()
        if s_1 is True:
            new.append(classification_1[0])
        else:
            new.append("0")
        if s_2 is True:
            new.append(classification_1[1])
        else:
            new.append("0")
        if s_3 is True:
            new.append(classification_1[2])
        else:
            new.append("0")
        if s_4 is True:
            new.append(classification_1[3])
        else:
            new.append("0")
        if s_5 is True:
            new.append(classification_1[4])
        else:
            new.append("0")
        if s_6 is True:
            new.append(classification_1[5])
        else:
            new.append("0")
        if s_7 is True:
            new.append(classification_1[6])
        else:
            new.append("0")
        if s_8 is True:
            new.append(classification_1[7])
        else:
            new.append("0")
        if s_9 is True:
            new.append(classification_1[8])
        else:
            new.append("0")
        if s_10 is True:
            new.append(classification_1[9])
        else:
            new.append("0")
        new_classification_id = copy.deepcopy(
            str(new[0] + new[1] + new[2] + new[3] + new[4] + new[5] + new[6] + new[7]))
        tender_classification_id = f"{new_classification_id[0:3]}00000"
        iteration = quantity - 2
        index = 1
        while iteration > 0:
            index += 1
            classification_1 = new_classification_id
            classification_2 = list_of_values[index]
            s_1 = fnmatch.fnmatch(classification_1[0], classification_2[0])
            s_2 = fnmatch.fnmatch(classification_1[1], classification_2[1])
            s_3 = fnmatch.fnmatch(classification_1[2], classification_2[2])
            s_4 = fnmatch.fnmatch(classification_1[3], classification_2[3])
            s_5 = fnmatch.fnmatch(classification_1[4], classification_2[4])
            s_6 = fnmatch.fnmatch(classification_1[5], classification_2[5])
            s_7 = fnmatch.fnmatch(classification_1[6], classification_2[6])
            s_8 = fnmatch.fnmatch(classification_1[7], classification_2[7])
            new = list()
            if s_1 is True:
                new.append(classification_1[0])
            else:
                new.append("0")
            if s_2 is True:
                new.append(classification_1[1])
            else:
                new.append("0")
            if s_3 is True:
                new.append(classification_1[2])
            else:
                new.append("0")
            if s_4 is True:
                new.append(classification_1[3])
            else:
                new.append("0")
            if s_5 is True:
                new.append(classification_1[4])
            else:
                new.append("0")
            if s_6 is True:
                new.append(classification_1[5])
            else:
                new.append("0")
            if s_7 is True:
                new.append(classification_1[6])
            else:
                new.append("0")
            if s_8 is True:
                new.append(classification_1[7])
            else:
                new.append("0")
            new_classification_id = copy.deepcopy(
                str(new[0] + new[1] + new[2] + new[3] + new[4] + new[5] + new[6] + new[7]))
            iteration -= 1
            tender_classification_id = f"{new_classification_id[0:4]}0000"
    else:
        tender_classification_id = f"{items_array[0]['classification']['id'][0:4]}0000"
    return tender_classification_id


# This function returns root dir, for example 'procuriosity_autotests' dir
def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def get_value_from_country_csv(country, language):
    path = get_project_root()
    with open(f'{path}/country.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == country and row[4] == language:
                return row


def get_value_from_region_csv(region, country, language):
    path = get_project_root()
    with open(f'{path}/region.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == region and row[4] == country and row[5] == language:
                return row


def get_value_from_locality_csv(locality, region, country, language):
    path = get_project_root()
    with open(f'{path}/locality.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == locality and row[4] == region and row[5] == country and row[6] == language:
                return row


def get_contract_period_for_ms_release(lots_array):
    start_date = list()
    end_date = list()
    for lot_object in lots_array:
        if "contractPeriod" in lot_object:
            if "startDate" in lot_object['contractPeriod']:
                date = datetime.datetime.strptime(lot_object['contractPeriod']['startDate'], "%Y-%m-%dT%H:%M:%SZ")
                start_date.append(date)
            else:
                raise KeyError("Check lot_object['contractPeriod']['startDate']")

            if "endDate" in lot_object['contractPeriod']:
                date = datetime.datetime.strptime(lot_object['contractPeriod']['endDate'], "%Y-%m-%dT%H:%M:%SZ")
                end_date.append(date)
            else:
                raise KeyError("Check lot_object['contractPeriod']['endDate']")
        else:
            raise KeyError("Check lot_object['contractPeriod']")
    minimum_date = min(start_date)
    start_date_for_ms_release = minimum_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    maximum_date = max(end_date)
    end_date_for_ms_release = maximum_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    return start_date_for_ms_release, end_date_for_ms_release


def get_sum_of_lot(lots_array):
    """
    This function returns result of sum all lots into payload.
    """
    sum_of_lot = list()
    for lot_object in lots_array:
        if "value" in lot_object:
            if "amount" in lot_object['value']:
                sum_of_lot.append(lot_object['value']['amount'])
            else:
                raise KeyError("Check lot_object['value']['amount']")
        else:
            raise KeyError("Check lot_object['value']")
    s = float(format(sum(sum_of_lot), '.2f'))
    return s


def set_permanent_id(release_array, payload_array):
    """
    This function returns payload_array with permanent id from release_array.
    It means, we can set permanent id for lots, items, documents, any array.
    """
    try:
        """
        Check how many objects contains into release_*_array.
        Get permanent *.id
        """
        permanent_id_list = list()
        for some_object in release_array:
            if "id" in some_object:
                permanent_id_list.append(some_object['id'])
        quantity_of_release_id = len(permanent_id_list)
    except KeyError:
        raise KeyError("'id' was not fined into 'release_*_array'")

    try:
        """
        Check how many objects contains into payload_lots_array.
        """
        permanent_id_list = list()
        for some_object in payload_array:
            if "id" in some_object:
                permanent_id_list.append(some_object['id'])
        quantity_of_payload_id = len(permanent_id_list)
    except KeyError:
        raise KeyError("'id' was not fined into 'payload_lots_array'")

    try:
        """
        Set permanent lot.id into payload_lots_array
        """
        if quantity_of_payload_id == quantity_of_release_id or \
                quantity_of_payload_id > quantity_of_release_id:
            cycle = quantity_of_release_id - 1
            position = 0
            while cycle >= 0:
                copy.deepcopy(payload_array)
                payload_array[position]['id'] = release_array[position]['id']
                position += 1
                cycle -= 1

        elif quantity_of_payload_id < quantity_of_release_id:
            cycle = quantity_of_payload_id - 1
            position = 0
            while cycle >= 0:
                copy.deepcopy(payload_array)
                payload_array[position]['id'] = release_array[position]['id']
                position += 1
                cycle -= 1

    except ValueError:
        raise ValueError("Impossible to set permanent id into 'payload_lots_array'")
    return payload_array


def get_value_from_standard_criteria_csv(country, language):
    """
    This function returns value from the file 'standard_criteria.csv'.
    The file 'standard_criteria.csv' contains standard_criteria value from 'mdm' Postgres database.
    """
    path = get_project_root()
    with open(f'{path}/standard_criteria.csv') as f:
        reader = csv.reader(f)
        standard_criteria_full_list = list()
        for row in reader:
            if row[1] == country and row[2] == language.upper():
                standard_criteria_full_list.append(json.loads(row[3]))

        exclusion_ground_criteria_list = list()
        for criteria in copy.deepcopy(standard_criteria_full_list):
            for i in criteria['classification']:
                if i == "id":
                    if criteria['classification']['id'][0:20] == "CRITERION.EXCLUSION.":
                        exclusion_ground_criteria_list.append(criteria['classification'])

        selection_criteria_list = list()
        for criteria in copy.deepcopy(standard_criteria_full_list):
            for i in criteria['classification']:
                if i == "id":
                    if criteria['classification']['id'][0:20] == "CRITERION.SELECTION.":
                        selection_criteria_list.append(criteria['classification'])

        other_criteria_list = list()
        for criteria in copy.deepcopy(standard_criteria_full_list):
            for i in criteria['classification']:
                if i == "id":
                    if criteria['classification']['id'][0:16] == "CRITERION.OTHER.":
                        other_criteria_list.append(criteria['classification'])
        return standard_criteria_full_list, exclusion_ground_criteria_list, selection_criteria_list, other_criteria_list


def make_unique_numbers(n):
    """
    This function returns set of the unique numbers.
    """
    set_of_numbers = set()
    while len(set_of_numbers) < n:
        set_of_numbers.add(random.randint(0, n))
    return set_of_numbers


def set_eligibility_evidences_unique_temporary_id(payload_criteria_array):
    """
    This function returns
    criteria[*].requirementGroups[*].requirements[*].eligibleEvidences[*].id as temporary id.
    """
    quantity_of_id_list = list()
    for i in payload_criteria_array:
        if "requirementGroups" in i:
            for i_1 in i['requirementGroups']:
                if "requirements" in i_1:
                    for i_2 in i_1['requirements']:
                        if "eligibleEvidences" in i_2:
                            for i_3 in i_2['eligibleEvidences']:
                                if "id" in i_3:
                                    quantity_of_id_list.append(i_3['id'])

    test = make_unique_numbers(len(quantity_of_id_list))
    iterator = len(test)
    if len(quantity_of_id_list) == len(test):
        for i in payload_criteria_array:
            if "requirementGroups" in i:
                for i_1 in i['requirementGroups']:
                    if "requirements" in i_1:
                        for i_2 in i_1['requirements']:
                            if "eligibleEvidences" in i_2:
                                for i_3 in i_2['eligibleEvidences']:
                                    if "id" in i_3:
                                        i_3['id'] = str(iterator)
                                        iterator -= 1

    return payload_criteria_array


def set_criteria_array_unique_temporary_id(payload_criteria_array):
    """
    This function returns criteria array with unique criteria[*].id, criteria[*].requirementGroups[*].id,
    criteria[*].requirementGroups[*].requirements[*].id as temporary id.
    """
    criteria_objects = list()
    for o in payload_criteria_array:
        if "id" in o:
            criteria_objects.append(o['id'])

    requirement_groups_objects = list()
    for o in payload_criteria_array:
        if "id" in o:
            for o_1 in o['requirementGroups']:
                if "id" in o_1:
                    requirement_groups_objects.append(o_1['id'])

    requirements_objects = list()
    for o in payload_criteria_array:
        if "id" in o:
            for o_1 in o['requirementGroups']:
                if "id" in o_1:
                    for o_2 in o_1['requirements']:
                        if "id" in o_2:
                            requirements_objects.append(o_1['id'])

    quantity_of_criteria_objects = len(criteria_objects)
    quantity_of_requirement_group_objects = len(requirement_groups_objects)
    quantity_of_requirement_objects = len(requirements_objects)

    test = make_unique_numbers(quantity_of_criteria_objects)
    iterator = len(test)
    criteria_list = []
    if quantity_of_criteria_objects == len(test):
        for o in payload_criteria_array:
            o['id'] = str(iterator).zfill(3)
            iterator -= 1
            criteria_list.append(o)

    test = make_unique_numbers(quantity_of_requirement_group_objects)
    iterator = len(test)
    requirement_groups_list = []
    if quantity_of_requirement_group_objects == len(test):
        for o in criteria_list:
            for o_1 in o['requirementGroups']:
                o_1['id'] = f"{o['id']}-{str(iterator).zfill(3)}"
                iterator -= 1
                requirement_groups_list.append(o_1)

    test = make_unique_numbers(quantity_of_requirement_objects)
    iterator = len(test)
    requirements_list = []
    if quantity_of_requirement_objects == len(test):
        for o in requirement_groups_list:
            for o_1 in o['requirements']:
                o_1['id'] = f"{o['id']}-{str(iterator).zfill(3)}"
                iterator -= 1
                requirements_list.append(o_1)

    return payload_criteria_array


def generate_conversions_array(quantity_of_conversion_object, conversion_object, requirements_array):
    copy.deepcopy(conversion_object)

    coefficient_id_list = list()
    for o in conversion_object['coefficients']:
        if "id" in o:
            coefficient_id_list.append(o['id'])
    quantity_of_coefficient_object = len(coefficient_id_list)

    conversions_array = []
    for i in range(quantity_of_conversion_object):
        conversion_json = copy.deepcopy(conversion_object)
        conversion_json['id'] = str(i)
        conversion_json['relatedItem'] = requirements_array[i]
        coefficients_array = []
        for j in range(quantity_of_coefficient_object):
            coefficient_json = copy.deepcopy(conversion_json['coefficients'][j])
            coefficient_json['id'] = str(j)
            coefficients_array.append(coefficient_json)
        conversion_json['coefficients'] = coefficients_array
        conversions_array.append(conversion_json)

    new_array_conversions = []
    for quantity_of_object in range(quantity_of_conversion_object):
        val = conversions_array[quantity_of_object]
        new_array_conversions.append(copy.deepcopy(val))
    return new_array_conversions


def set_conversions_unique_temporary_id(payload_conversions_array):
    """
    This function returns
    conversions[*]..id as temporary id.
    """
    quantity_of_id_list = list()
    for i in payload_conversions_array:
        if "id" in i:
            quantity_of_id_list.append(i['id'])

    test = make_unique_numbers(len(quantity_of_id_list))
    iterator = len(test)
    if len(quantity_of_id_list) == len(test):
        for i in payload_conversions_array:
            if "id" in i:
                i['id'] = str(iterator)
                iterator -= 1

    return payload_conversions_array


def get_temporary_requirements_id_and_permanent_requirements_id(temporary_criteria_array, permanent_criteria_array):
    temporary_id_list = list()
    for criteria_object in temporary_criteria_array:
        for requirement_group in criteria_object['requirementGroups']:
            for requirement in requirement_group['requirements']:
                for i in requirement:
                    if i == "id":
                        temporary_id_list.append(requirement[i])

    permanent_id_list = list()
    for criteria_object in permanent_criteria_array:
        for requirement_group in criteria_object['requirementGroups']:
            for requirement in requirement_group['requirements']:
                for i in requirement:
                    if i == "id":
                        permanent_id_list.append(requirement[i])

    quantity_of_temporary_id = len(temporary_id_list)
    quantity_of_permanent_id = len(permanent_id_list)
    try:
        """
        Compare quantity of temporary objects into temporary_array and permanent_array.
        """
        if quantity_of_temporary_id == quantity_of_permanent_id:
            pass
    except KeyError:
        raise KeyError("Quantity of temporary.id into quantity_of_temporary_id != "
                       "quantity of permanent.id into and permanent_id_list")

    quantity = quantity_of_temporary_id - 1

    dictionary_of_id = dict()
    while quantity >= 0:
        expected_of_id = {
            temporary_id_list[quantity]: permanent_id_list[quantity]
        }
        dictionary_of_id.update(expected_of_id)
        quantity -= 1

    return dictionary_of_id


def get_temporary_lots_id_and_permanent_lots_id(temporary_lots_array, permanent_lots_array):
    temporary_id_list = list()
    for lot_object in temporary_lots_array:
        for i in lot_object:
            if i == "id":
                temporary_id_list.append(lot_object[i])

    permanent_id_list = list()
    for lot_object in permanent_lots_array:
        for i in lot_object:
            if i == "id":
                permanent_id_list.append(lot_object[i])

    quantity_of_temporary_id = len(temporary_id_list)
    quantity_of_permanent_id = len(permanent_id_list)
    try:
        """
        Compare quantity of temporary objects into temporary_array and permanent_array.
        """
        if quantity_of_temporary_id == quantity_of_permanent_id:
            pass
    except KeyError:
        raise KeyError("Quantity of temporary.id into quantity_of_temporary_id != "
                       "quantity of permanent.id into and permanent_id_list")

    quantity = quantity_of_temporary_id - 1

    dictionary_of_id = dict()
    while quantity >= 0:
        expected_of_id = {
            temporary_id_list[quantity]: permanent_id_list[quantity]
        }
        dictionary_of_id.update(expected_of_id)
        quantity -= 1

    return dictionary_of_id


def time_bot(expected_time):
    expected_time = datetime.datetime.strptime(expected_time, "%Y-%m-%dT%H:%M:%SZ")
    time_at_now = datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.now(pytz.utc),
                                                                        "%Y-%m-%dT%H:%M:%SZ"), "%Y-%m-%dT%H:%M:%SZ")
    while time_at_now < expected_time:
        time_at_now = datetime.datetime.strptime(datetime.datetime.strftime(datetime.datetime.now(pytz.utc),
                                                                            "%Y-%m-%dT%H:%M:%SZ"), "%Y-%m-%dT%H:%M:%SZ")
        if time_at_now >= expected_time:
            time.sleep(3)
            break
    print("The time was expired")


def generate_requirement_response_array(ev_release_criteria_array, payload):
    copy.deepcopy(payload)
    date = Date()
    try:
        """
        Calculate quantity of object into payload['bid']['tenderers'] array.
        """
        tenderer_id_list = list()
        for to in payload['bid']['tenderers']:
            for o in to['identifier']:
                if o == "id":
                    tenderer_id_list.append(o)
        quantity_of_tenderer_object = len(tenderer_id_list)
    except ValueError:
        raise ValueError("Impossibility to calculate quantity of groups into group of "
                         "ev_release_criteria_array.")
    try:
        """
        Calculate quantity of object into ev_release_criteria_array.
        """
        id_list = list()
        for i in ev_release_criteria_array:
            for i_1 in i:
                if i_1 == "id":
                    id_list.append(i_1)
        quantity_of_criteria_object = len(id_list)
    except ValueError:
        raise ValueError("Impossibility to calculate quantity of criterion into ev_release_criteria_array.")

    try:
        """
        Calculate quantity of object into ev_release_criteria_array['requirementGroups'].
        """
        requirements_id_list = list()
        requirements_expected_value_was_chose = list()

        for x in range(quantity_of_criteria_object):
            groups_id_list = list()
            for x_1 in ev_release_criteria_array[x]['requirementGroups']:
                for x_2 in x_1:
                    if x_2 == "id":
                        groups_id_list.append(x_2)
            quantity_of_requirement_groups = len(groups_id_list)
            choose_the_requirement_group = random.randint(0, quantity_of_requirement_groups - 1)

            for y in ev_release_criteria_array[x]['requirementGroups'][choose_the_requirement_group][
                'requirements']:
                if "id" in y and "expectedValue" in y:
                    requirements_id_list.append(y['id'])
                    requirements_expected_value_was_chose.append(copy.deepcopy(
                        {"id": y['id'],
                         "value": y['expectedValue']}))
                elif "id" in y and "minValue" in y:
                    requirements_id_list.append(y['id'])
                    requirements_expected_value_was_chose.append(copy.deepcopy(
                        {"id": y['id'],
                         "value": y['minValue']}))
                elif "id" in y and "maxValue" in y:
                    requirements_id_list.append(y['id'])
                    requirements_expected_value_was_chose.append(copy.deepcopy(
                        {"id": y['id'],
                         "value": y['maxValue']}))
        quantity_of_requirements = len(requirements_id_list)
    except ValueError:
        raise ValueError("Impossibility to calculate quantity of criterion into "
                         "ev_release_criteria_array['requirementGroups'].")

    list_of_requirements_expected_value_was_chose = requirements_expected_value_was_chose * quantity_of_tenderer_object
    quantity_of_requirement_responses_objects = quantity_of_tenderer_object * quantity_of_requirements

    payload['bid']['requirementResponses'] = list()
    constructor = copy.deepcopy(PayloadLibrary())
    requirement_responses_object = constructor.requirement_response()
    requirement_responses_object['evidences'] = [{}]
    requirement_responses_object['evidences'][0] = constructor.evidence_object()

    for t in range(quantity_of_tenderer_object):
        for i in range(quantity_of_requirements):
            requirement_responses_object['id'] = str(i)
            requirement_responses_object['evidences'][0]['id'] = str(i)
            requirement_responses_object['relatedTenderer']['name'] = \
                payload['bid']['tenderers'][t]['name']
            requirement_responses_object['relatedTenderer']['identifier']['id'] = \
                payload['bid']['tenderers'][t]['identifier']['id']
            requirement_responses_object['relatedTenderer']['identifier']['scheme'] = \
                payload['bid']['tenderers'][t]['identifier']['scheme']

            requirement_responses_object['evidences'][0]['title'] = "evidences.title"
            requirement_responses_object['evidences'][0]['description'] = "evidences.description"
            requirement_responses_object['evidences'][0]['relatedDocument']['id'] = \
                payload['bid']['documents'][0]['id']

            requirement_responses_object['period']['startDate'] = date.contact_period()[0]
            requirement_responses_object['period']['endDate'] = date.contact_period()[1]
            payload['bid']['requirementResponses'].append(copy.deepcopy(requirement_responses_object))

    for i in range(quantity_of_requirement_responses_objects):
        payload['bid']['requirementResponses'][i]['requirement']['id'] = \
            list_of_requirements_expected_value_was_chose[i]['id']
        payload['bid']['requirementResponses'][i]['value'] = \
            list_of_requirements_expected_value_was_chose[i]['value']

        payload['bid']['requirementResponses'][i]['evidences'][0]['id'] = str(i)
        payload['bid']['requirementResponses'][i]['id'] = str(i)

    return payload['bid']['requirementResponses']


def generate_requirement_response_array(ev_release_criteria_array, payload):
    copy.deepcopy(payload)
    date = Date()
    try:
        """
        Calculate quantity of object into payload['bid']['tenderers'] array.
        """
        tenderer_id_list = list()
        for to in payload['bid']['tenderers']:
            for o in to['identifier']:
                if o == "id":
                    tenderer_id_list.append(o)
        quantity_of_tenderer_object = len(tenderer_id_list)
    except ValueError:
        raise ValueError("Impossibility to calculate quantity of groups into group of "
                         "ev_release_criteria_array.")
    try:
        """
        Calculate quantity of object into ev_release_criteria_array.
        """
        id_list = list()
        for i in ev_release_criteria_array:
            for i_1 in i:
                if i_1 == "id":
                    id_list.append(i_1)
        quantity_of_criteria_object = len(id_list)
    except ValueError:
        raise ValueError("Impossibility to calculate quantity of criterion into ev_release_criteria_array.")

    try:
        """
        Calculate quantity of object into ev_release_criteria_array['requirementGroups'].
        """
        requirements_id_list = list()
        requirements_expected_value_was_chose = list()

        for x in range(quantity_of_criteria_object):
            groups_id_list = list()
            if ev_release_criteria_array[x]['relatesTo'] == "lot" or ev_release_criteria_array[x][
                'relatesTo'] == "tender" or ev_release_criteria_array[x]['relatesTo'] == "item":
                for x_1 in ev_release_criteria_array[x]['requirementGroups']:
                    for x_2 in x_1:
                        if x_2 == "id":
                            groups_id_list.append(x_2)
                quantity_of_requirement_groups = len(groups_id_list)
                choose_the_requirement_group = random.randint(0, quantity_of_requirement_groups - 1)

                for y in ev_release_criteria_array[x]['requirementGroups'][choose_the_requirement_group][
                    'requirements']:
                    if "id" in y and "expectedValue" in y:
                        requirements_id_list.append(y['id'])
                        requirements_expected_value_was_chose.append(copy.deepcopy(
                            {"id": y['id'],
                             "value": y['expectedValue']}))
                    elif "id" in y and "minValue" in y:
                        requirements_id_list.append(y['id'])
                        requirements_expected_value_was_chose.append(copy.deepcopy(
                            {"id": y['id'],
                             "value": y['minValue']}))
                    elif "id" in y and "maxValue" in y:
                        requirements_id_list.append(y['id'])
                        requirements_expected_value_was_chose.append(copy.deepcopy(
                            {"id": y['id'],
                             "value": y['maxValue']}))
        quantity_of_requirements = len(requirements_id_list)
    except ValueError:
        raise ValueError("Impossibility to calculate quantity of criterion into "
                         "ev_release_criteria_array['requirementGroups'].")

    list_of_requirements_expected_value_was_chose = requirements_expected_value_was_chose * quantity_of_tenderer_object
    quantity_of_requirement_responses_objects = quantity_of_requirements * quantity_of_tenderer_object

    payload['bid']['requirementResponses'] = list()
    constructor = copy.deepcopy(PayloadLibrary())
    requirement_responses_object = constructor.requirement_response()
    requirement_responses_object['evidences'] = [{}]
    requirement_responses_object['evidences'][0] = constructor.evidence_object()

    for t in range(quantity_of_tenderer_object):
        for i in range(quantity_of_requirements):
            requirement_responses_object['id'] = str(i)
            requirement_responses_object['evidences'][0]['id'] = str(i)
            requirement_responses_object['relatedTenderer']['name'] = \
                payload['bid']['tenderers'][t]['name']
            requirement_responses_object['relatedTenderer']['identifier']['id'] = \
                payload['bid']['tenderers'][t]['identifier']['id']
            requirement_responses_object['relatedTenderer']['identifier']['scheme'] = \
                payload['bid']['tenderers'][t]['identifier']['scheme']
            requirement_responses_object['evidences'][0]['title'] = "evidences.title"
            requirement_responses_object['evidences'][0]['description'] = "evidences.description"
            requirement_responses_object['evidences'][0]['relatedDocument']['id'] = \
                payload['bid']['documents'][0]['id']
            requirement_responses_object['period']['startDate'] = date.contact_period()[0]
            requirement_responses_object['period']['endDate'] = date.contact_period()[1]
            payload['bid']['requirementResponses'].append(copy.deepcopy(requirement_responses_object))
    for i in range(quantity_of_requirement_responses_objects):
        payload['bid']['requirementResponses'][i]['requirement']['id'] = \
            list_of_requirements_expected_value_was_chose[i]['id']
        payload['bid']['requirementResponses'][i]['value'] = \
            list_of_requirements_expected_value_was_chose[i]['value']
        payload['bid']['requirementResponses'][i]['evidences'][0]['id'] = str(i)
        payload['bid']['requirementResponses'][i]['id'] = str(i)
    return payload['bid']['requirementResponses']


def get_id_token_of_award_in_pending_awaiting_state(actual_awards_array, feed_point_message):
    actual_award_id_list = list()
    award_id = None
    award_token = None
    try:
        """
        Calculate how many quantity of object into actual_awards_requirement_responses_array
        """
        for a in actual_awards_array:
            if a['status'] == "pending":
                if a['statusDetails'] == "awaiting":
                    actual_award_id_list.append(a['id'])
    except Exception:
        log_msg_one = f"\n{datetime.datetime.now()}\n" \
                      f"File = declare_non_conflict_interest_prepared_release.py -> \n" \
                      f"Class = DeclareExpectedRelease -> \n" \
                      f"Method = awards_requirement_responses_array -> \n" \
                      f"Message: Impossible to calculate how many quantity of object into " \
                      f"actual_awards_requirement_responses_array.\n"
        with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
            logfile.write(log_msg_one)
        raise Exception("Impossible to calculate how many quantity of object into "
                        f"actual_awards_requirement_responses_array.")

    for f in feed_point_message['data']['outcomes']['awards']:
        if f['id'] == actual_award_id_list[0]:
            award_id = actual_award_id_list[0]
            award_token = f['X-TOKEN']
    return award_id, award_token
