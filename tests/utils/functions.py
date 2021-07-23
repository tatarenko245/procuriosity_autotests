import copy
import fnmatch

import random
from pathlib import Path

from uuid import UUID
import csv
import xlrd

import allure

from tests.utils.data_of_enum import cpv_goods_low_level_03, cpv_goods_low_level_1, cpv_goods_low_level_2, \
    cpv_goods_low_level_3, cpv_goods_low_level_44, cpv_goods_low_level_48, cpv_works_low_level_45, \
    cpv_services_low_level_5, cpv_services_low_level_6, cpv_services_low_level_7, cpv_services_low_level_8, \
    cpv_services_low_level_92, cpv_services_low_level_98


@allure.step('Compare actual and expected results')
def compare_actual_result_and_expected_result(expected_result, actual_result):
    allure.attach(expected_result, "Expected result")
    allure.attach(actual_result, "Actual result")
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


def generate_items_array(quantity_of_object, item_object, tender_classification_id):
    copy.deepcopy(item_object)
    items_array = [item_object for _ in range(quantity_of_object)]
    id_set = set()
    while len(id_set) < quantity_of_object:
        id_list = list()
        for i in items_array:
            for keys, values in i.items():
                if keys == "id":
                    values = random.randint(1, quantity_of_object + 1)
                    id_list.append(values)

        id_set = set(id_list)
    correct_id_list = list(id_set)
    new_array_items = list()
    for quantity_of_object in range(quantity_of_object):
        id_ = str(correct_id_list[quantity_of_object])
        items_array[quantity_of_object]['id'] = id_
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


def generate_tender_classification_id(items_array):
    list_of_keys = list()
    list_of_values = list()
    for o in items_array:
        for id_ in o['classification']:
            if id_ == "id":
                list_of_keys.append(id_)
                list_of_values.append(o['classification']['id'])
    quantity = len(list_of_keys)
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
        tender_classification_id = f"{new_classification_id[0:3]}00000"
    return tender_classification_id


# This function returns 'procuriosity_autotests' dir
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
