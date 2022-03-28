import pytest
from cassandra import ProtocolVersion
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster


@pytest.fixture(scope="class")
def log_in_to_database(get_hosts, parse_cassandra_username, parse_cassandra_password):
    auth_provider = PlainTextAuthProvider(
        username=parse_cassandra_username,
        password=parse_cassandra_password
    )

    cluster = Cluster(
        contact_points=[get_hosts[0]],
        auth_provider=auth_provider,
        protocol_version=ProtocolVersion.V4)
    return cluster


@pytest.fixture(scope="class")
def connect_to_ocds(log_in_to_database):
    ocds_keyspace = log_in_to_database.connect('ocds')
    yield ocds_keyspace
    ocds_keyspace.shutdown()
    print(f"The connection to {ocds_keyspace} has been disconnected.")


@pytest.fixture(scope="class")
def connect_to_orchestrator(log_in_to_database):
    orchestrator_keyspace = log_in_to_database.connect('orchestrator')
    yield orchestrator_keyspace
    orchestrator_keyspace.shutdown()
    print(f"The connection to {orchestrator_keyspace} has been disconnected.")
#
#
# @pytest.fixture(scope="class")
# def clear_tables_of_all_services(connect_to_ocds):
#     connect_to_ocds.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{cp_id}';").one()
