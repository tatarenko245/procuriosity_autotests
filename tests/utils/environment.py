class Environment:
    @staticmethod
    def choose_environment(instance):
        cassandra_cluster = None
        host_of_request = None
        host_of_services = None
        if instance == "dev":
            cassandra_cluster = "10.0.20.104"
            host_of_request = "http://10.0.20.126:8900/api/v1"
            host_of_services = "http://10.0.20.126"
        elif instance == "sandbox":
            cassandra_cluster = "10.0.10.104"
            host_of_request = "http://10.0.10.116:8900/api/v1"
            host_of_services = "http://10.0.10.116"
        return cassandra_cluster, host_of_request, host_of_services
