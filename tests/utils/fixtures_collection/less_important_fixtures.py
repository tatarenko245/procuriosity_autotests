import pytest


@pytest.fixture(scope="function")
def queue_mapper():
    queue_mapper = {
        0: "first",
        1: "second",
        2: "third",
        3: "fourth",
        4: "fifth",
        5: "sixth",
        6: "seventh",
        7: "eighth",
        8: "ninth",
        9: "tenth"
    }
    return queue_mapper


@pytest.fixture(scope="session")
def metadata_budget_url(parse_environment):
    metadata_budget_url = None
    if parse_environment == "dev":
        metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
    elif parse_environment == "sandbox":
        metadata_budget_url = "http://public.eprocurement.systems/budgets"
    return metadata_budget_url
