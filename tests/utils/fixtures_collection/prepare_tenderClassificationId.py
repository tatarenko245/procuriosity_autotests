import random

import pytest

from tests.utils.data_of_enum import cpv_category_tuple, cpv_goods_high_level_tuple, cpv_works_high_level_tuple, \
    cpv_services_high_level_tuple


@pytest.fixture(scope="class")
def prepare_tender_classification_id():
    tender_classification_id = None
    category = random.choice(cpv_category_tuple)
    if category == "goods":
        tender_classification_id = random.choice(cpv_goods_high_level_tuple)
    elif category == "works":
        tender_classification_id = random.choice(cpv_works_high_level_tuple)
    elif category == "services":
        tender_classification_id = random.choice(cpv_services_high_level_tuple)
    return tender_classification_id
