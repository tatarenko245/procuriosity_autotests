"""Prepare some fixtures."""

import pytest
from cassandra import ProtocolVersion
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster


@pytest.fixture(scope="class")
def log_in_database(get_hosts, parse_cassandra_username, parse_cassandra_password):
    """Log in the database."""

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
def connect_to_ocds(log_in_database):
    """Connect to 'ocds' keyspace."""

    ocds_keyspace = log_in_database.connect('ocds')
    yield ocds_keyspace
    ocds_keyspace.shutdown()
    print(f"The connection to {ocds_keyspace} has been disconnected.")


@pytest.fixture(scope="class")
def connect_to_orchestrator(log_in_database):
    """Connect to 'orchestrator' keyspace."""

    orchestrator_keyspace = log_in_database.connect('orchestrator')
    yield orchestrator_keyspace
    orchestrator_keyspace.shutdown()
    print(f"The connection to {orchestrator_keyspace} has been disconnected.")


@pytest.fixture(scope="class")
def connect_to_access(log_in_database):
    """Connect to 'access' keyspace."""

    access_keyspace = log_in_database.connect('access')
    yield access_keyspace
    access_keyspace.shutdown()
    print(f"The connection to {access_keyspace} has been disconnected.")


@pytest.fixture(scope="class")
def connect_to_clarification(log_in_database):
    """Connect to 'clarification' keyspace."""

    clarification_keyspace = log_in_database.connect('clarification')
    yield clarification_keyspace
    clarification_keyspace.shutdown()
    print(f"The connection to {clarification_keyspace} has been disconnected.")
