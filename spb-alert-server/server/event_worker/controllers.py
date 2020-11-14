import json
from tornado.web import RequestHandler
from server.event_worker.worker import Worker


class InternalAppendEvent(RequestHandler):

    @staticmethod
    def get_mapping():
        return "/internal.appendEvent"

    def data_received(self, chunk):
        pass

    def post(self, *args, **kwargs):
        event = json.loads(self.request.body)
        event = ApiEvent(event)
        Worker.push(event)


class ApiEvent:
    def __init__(self, json_obj):
        self.event_type = json_obj["event_type"]
        self.timestamp = json_obj["timestamp"]
        self.lat = json_obj["lat"]
        self.lon = json_obj["lon"]
