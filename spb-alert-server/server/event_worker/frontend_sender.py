import requests


class FrontendClusterSender:

    schema = "http"
    host = "localhost"
    port = 8891

    def __init__(self):
        self.base_url = "{}://{}:{}".format(FrontendClusterSender.schema, FrontendClusterSender.host, FrontendClusterSender.port)

    def send(self, clusters):
        method = "/showClusters"
        requests.post(method, {"data": clusters})