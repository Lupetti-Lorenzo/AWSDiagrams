from diagrams import Diagram, Cluster
from diagrams.aws.compute import Lambda
from diagrams.aws.database import RDS
from diagrams.aws.network import APIGateway, NATGateway
from diagrams.aws.security import SecretsManager

graph_attr = {
    # "fontsize": "45", -- title font size
    "bgcolor": "white",
}

node_attr = {
    # "fixedsize": "true",
    # "height": "1.1",
    # "width": "1.1",
}

# The order of rendered diagrams is the reverse of the declaration order.
with Diagram("DB access diagram", show=True, outformat="png", direction="LR", graph_attr=graph_attr, node_attr=node_attr):
    with Cluster("VPC"):
        with Cluster("Private Subnet"):
            db = RDS("database")

        with Cluster("Public Subnet"):
            nat = NATGateway("nat")

        with Cluster("Private Egress"):
            handler = Lambda("api handler")

    api = APIGateway("api gateway")
    sm = SecretsManager("secrets manager")

    api - handler - db
    handler - nat - sm
