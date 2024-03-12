from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import APIGateway, CloudFront, Route53
from diagrams.aws.storage import S3
from diagrams.aws.devtools import Codepipeline, Codebuild, Codecommit
from diagrams.aws.general import Users

graph_attr = {
    # "fontsize": "45", -- title font size
    "bgcolor": "white",
}

node_attr = {
    # "fixedsize": "true",
    # "height": "1.1",
    # "width": "1.1",
}

with Diagram("Frontend Infrastructure", filename="frontend_infra", show=True, outformat="png", direction="LR", graph_attr=graph_attr, node_attr=node_attr):
    with Cluster("AWS Cloud"):
        # S3 bucket for storing HTML, CSS, and JS
        s3_bucket = S3("S3 Bucket")

        # CloudFront distribution linked to the S3 bucket
        cloudfront = CloudFront("CloudFront Distribution")
        s3_bucket << Edge(label="Website Content") << cloudfront

        # CodePipeline with CodeBuild
        with Cluster("Pipeline"):
            codepipeline = Codepipeline("CodePipeline")
            codebuild = Codebuild("CodeBuild")
            frontend_repo = Codecommit("CodeCommit Repo")
            frontend_repo >> Edge(label="Source") >> codepipeline >> codebuild >> Edge(
                label="Update Build") >> s3_bucket

        # API Gateway
        api_gateway = APIGateway("API Gateway")

        # Route53 for DNS
        route53 = Route53("sm.taisoftware.solutions")

    # Developers
    developer = Users("Developers")
    developer >> Edge(label="Push") >> frontend_repo

    # Users
    website_user = Users("Website Visitors")

    website_user - Edge(label="Resolve domain name") - route53
    website_user - cloudfront
    website_user - Edge(label="Call API") - api_gateway
