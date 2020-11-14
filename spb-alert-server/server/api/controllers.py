import json
import requests
from tornado.web import RequestHandler
from server.api.utils import ApiPushEvent


class ApiPushEventHandler(RequestHandler):

    schema = "http"
    host = "localhost"
    port = 8889

    @staticmethod
    def get_mapping():
        return "/api.pushEvent"

    def post(self, *args, **kwargs):
        request_body = json.loads(self.request.body)
        event = ApiPushEvent(request_body)
        self.send_to_event_service(event)

    def data_received(self, chunk):
        pass

    def send_to_event_service(self, event):
        url = "{}://{}:{}/internal.appendEvent".format(
            ApiPushEventHandler.schema,
            ApiPushEventHandler.host,
            ApiPushEventHandler.port
        )
        json_event = {
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "lat": event.lat,
            "lon": event.lon
        }
        requests.post(url, json_event)
