from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2, Lambda, EKS, ECS
from diagrams.aws.database import RDS
from diagrams.aws.network import VPC, APIGateway, ELB, NATGateway
from diagrams.aws.security import SecretsManager
from diagrams.aws.storage import S3
from diagrams.aws.integration import SQS
from diagrams.aws.analytics import Redshift

# https://www.graphviz.org/doc/info/attrs.html
graph_attr = {
    # "fontsize": "45", -- title font size
    "bgcolor": "white",
}


# The order of rendered diagrams is the reverse of the declaration order.
with Diagram("Example", show=True, outformat="png", direction="LR", graph_attr=graph_attr):
    # Data flow >>, <<. -
    EC2("bastion") >> RDS("database")
    RDS("database") << EC2("bastion")
    APIGateway("apigw") - Lambda("handler")
    # Goup data flow - can't connect two lists directly because shift/arithmetic operations between lists are not allowed in Python.
    ELB("lb") >> [EC2("worker1"),
                  EC2("worker2"),
                  EC2("worker3"),
                  EC2("worker4"),
                  EC2("worker5")] >> RDS("events")

    # Grouping - clusters and vpcs
    source = EKS("k8s source")

    with Cluster("Event Flows"):
        with Cluster("Event Workers"):
            workers = [ECS("worker1"),
                       ECS("worker2"),
                       ECS("worker3")]

        queue = SQS("event queue")

        with Cluster("Processing"):
            handlers = [Lambda("proc1"),
                        Lambda("proc2"),
                        Lambda("proc3")]

    store = S3("events store")
    dw = Redshift("analytics")

    source >> workers >> queue >> handlers
    handlers >> store
    handlers >> dw
