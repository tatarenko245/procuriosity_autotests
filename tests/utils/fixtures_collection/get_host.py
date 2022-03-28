import pytest


@pytest.fixture(scope="class")
def get_hosts(parse_environment):
    database_host = None
    bpe_host = None
    service_host = None

    if parse_environment == "dev":
        database_host = "10.0.20.104"
        bpe_host = "http://10.0.20.126:8900/api/v1"
        service_host = "http://10.0.20.126"
    elif parse_environment == "sandbox":
        database_host = "10.0.10.104"
        bpe_host = "http://10.0.10.116:8900/api/v1"
        service_host = "http://10.0.10.116"

    return database_host, bpe_host, service_host
