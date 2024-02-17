from diagrams import Diagram, Cluster
from diagrams.aws.compute import Lambda
from diagrams.aws.database import RDS
from diagrams.aws.network import APIGateway, NATGateway
from diagrams.aws.security import SecretsManager

# The order of rendered diagrams is the reverse of the declaration order.
with Diagram("dbaccess", show=True, outformat="png", direction="LR"):
    with Cluster("VPC"):
        with Cluster("Private Subnet"):
            db = RDS("database")

        with Cluster("Public Subnet"):
            nat = NATGateway("nat")

        with Cluster("Private Egress"):
            handler = Lambda("api handler")

    api = APIGateway("api gateway")
    sm = SecretsManager("secrets manager")

    api >> handler >> db
    handler >> nat >> sm
