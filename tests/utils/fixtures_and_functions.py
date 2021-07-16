from uuid import UUID
import csv
import xlrd

import allure


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
    # Open current xlsx file.
    excel_data_file = xlrd.open_workbook('CPV_dictionary.xls')
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
    with open('CPVS_dictionary.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            cur_arr = row[0].split(';')
            if cur_arr[0] == cpvs and cur_arr[3] == f'"{language}"':
                return cur_arr[0].replace('"', ''), cur_arr[1].replace('"', ''), cur_arr[2].replace('"', ''), cur_arr[
                    3].replace('"', '')


def get_value_from_classification_unit_dictionary_csv(unit_id, language):
    with open('Units_dictionary.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            cur_arr = row[0].split(',')
            if cur_arr[0] == f'{unit_id}' and cur_arr[4].replace(';', '') == f'"{language}"':
                return cur_arr[0].replace("'", ""), cur_arr[2].replace('"', ''),
