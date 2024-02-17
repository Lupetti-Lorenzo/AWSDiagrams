# https://diagrams.mingrammer.com/docs/guides/diagram
from diagrams import Diagram, Cluster, Edge

from diagrams.onprem.queue import Kafka
from diagrams.onprem.network import Nginx
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.aggregator import Fluentd
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.compute import Server
from diagrams.onprem.analytics import Spark
from diagrams.aws.compute import EC2, Lambda, EKS, ECS
from diagrams.aws.database import RDS
from diagrams.aws.network import APIGateway, ELB
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

    # Edges with labels, colors, and styles
    ingress = Nginx("ingress")

    metrics = Prometheus("metric")
    metrics << Edge(color="firebrick", style="dashed") << Grafana("monitoring")

    with Cluster("Service Cluster"):
        grpcsvc = [
            Server("grpc1"),
            Server("grpc2"),
            Server("grpc3")]

    with Cluster("Sessions HA"):
        primary = Redis("session")
        primary \
            - Edge(color="brown", style="dashed") \
            - Redis("replica") \
            << Edge(label="collect") \
            << metrics
        grpcsvc >> Edge(color="brown") >> primary

    with Cluster("Database HA"):
        primary = PostgreSQL("users")
        primary \
            - Edge(color="brown", style="dotted") \
            - PostgreSQL("replica") \
            << Edge(label="collect") \
            << metrics
        grpcsvc >> Edge(color="black") >> primary

    aggregator = Fluentd("logging")
    aggregator \
        >> Edge(label="parse") \
        >> Kafka("stream") \
        >> Edge(color="black", style="bold") \
        >> Spark("analytics")

    ingress \
        >> Edge(color="darkgreen") \
        << grpcsvc \
        >> Edge(color="darkorange") \
        >> aggregator
