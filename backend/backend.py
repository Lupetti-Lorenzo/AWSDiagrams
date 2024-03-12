from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda, EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import APIGateway, NATGateway, Route53
from diagrams.aws.security import SecretsManager
from diagrams.aws.engagement import SimpleEmailServiceSes
from diagrams.aws.general import Users
from diagrams.aws.devtools import Codepipeline, Codebuild, Codecommit
from diagrams.aws.management import Cloudformation

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
with Diagram("Backend Deployment Diagram", filename="backend_infra", show=True, outformat="png", direction="LR", graph_attr=graph_attr, node_attr=node_attr):
    with Cluster("AWS Cloud"):
        with Cluster("VPC"):
            with Cluster("Public Subnet"):
                nat = NATGateway("NAT")
            with Cluster("Private Subnet"):
                db = RDS("Postgres Database")

            with Cluster("Private Egress"):
                handler = Lambda("API Handler")
                bastion = EC2("Bastion Host")

        api = APIGateway("API Gateway")
        sm = SecretsManager("Secrets Manager")
        ses = SimpleEmailServiceSes("SES")
        # Route53 for DNS
        route53 = Route53("sm.taisoftware.solutions")
        cloud_formation = Cloudformation("CloudFormation")

        # CodePipeline with CodeBuild
        with Cluster("Pipeline"):
            codepipeline = Codepipeline("CodePipeline")
            codebuild = Codebuild("CodeBuild")
            backend_repo = Codecommit("Backend Repo")
            infra_repo = Codecommit("Infrastructure Repo")
            backend_repo >> Edge(label="Source Events") >> codepipeline
            infra_repo >> Edge(label="Source") >> codepipeline
            codepipeline >> codebuild >> Edge(
                label="Deploy") >> cloud_formation >> Edge(color="black", label="Update") >> [api, handler]

    handler - Edge(color="black", label="Send email") >> ses

    api - Edge(color="black") - handler - \
        Edge(color="black", label="DB Access") - db
    handler - Edge(color="black", label="Get DB Credentials") - \
        nat - Edge(color="black") - sm

    # Users
    api_users = Users("Api Users")
    api_users - Edge(color="black", label="Call Api") - api
    api_users - Edge(label="DNS", color="black") - route53

    # DevOps
    infra_users = Users("DevOps Team")
    infra_users >> Edge(color="black", label="Push to Repo") >> infra_repo

    # Database admin
    db_manager = Users("Database Administrator")
    db_manager >> Edge(color="black", label="SSH Tunnel") >> bastion >> Edge(
        color="black", label="Bridge") >> db

    # BackendUsers
    backend_users = Users("Backend Team")
    backend_users >> Edge(color="black", label="Push to Repo") >> backend_repo
