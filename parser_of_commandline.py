import argparse


def parse_argument_of_terminal():
    parser = argparse.ArgumentParser()
    # parser.add_argument("--country", required=True, type=str)
    # parser.add_argument("--language", required=True, type=str)
    parser.add_argument("--instance", required=True, type=str)
    # parser.add_argument("--cassandra_username", required=True, type=str)
    # parser.add_argument("--cassandra_password", required=True, type=str)
    args = parser.parse_args()
    return args



