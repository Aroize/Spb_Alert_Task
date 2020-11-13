from tornado.web import RequestHandler
from server.api.utils import ApiPushEvent
import json


class ApiPushEventHandler(RequestHandler):

    @staticmethod
    def get_mapping():
        return "/api.pushEvent"

    def post(self, *args, **kwargs):
        request_body = json.loads(self.request.body)
        event = ApiPushEvent(request_body)
        print(event)

    def data_received(self, chunk):
        pass
