import random

import pytest

from tests.utils.data_of_enum import cpv_category_tuple, cpv_goods_high_level_tuple, cpv_works_high_level_tuple, \
    cpv_services_high_level_tuple


@pytest.fixture(scope="class")
def prepare_tenderClassificationId():
    tenderClassificationId = None
    category = random.choice(cpv_category_tuple)
    if category == "goods":
        tenderClassificationId = random.choice(cpv_goods_high_level_tuple)
    elif category == "works":
        tenderClassificationId = random.choice(cpv_works_high_level_tuple)
    elif category == "services":
        tenderClassificationId = random.choice(cpv_services_high_level_tuple)
    return tenderClassificationId