import requests


class ModelEventSender:

    schema = "http"
    host = "localhost"
    port = 8890

    def __init__(self):
        self.base_url = "{}://{}:{}".format(ModelEventSender.schema, ModelEventSender.host, ModelEventSender.port)

    @staticmethod
    def process_event(event):
        return {
            "event": event.event_type,
            "ts": event.timestamp,
            "lat": event.lat,
            "lon": event.lon
        }

    def prepare_events_to_send(self, events):
        return {
            "data": list(map(self.process_event, events))
        }

    def send(self, events):
        method = "/processEvents"
        url = self.base_url + method
        data = self.prepare_events_to_send(events)
        response = requests.get(url, data)
        json_response = response.json()
        return json_response
