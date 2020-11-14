import logging
import requests

REASON_DESCRIPTIONS = {}


class FrontendClusterSender:

    schema = "http"
    host = "localhost"
    port = 8891

    def __init__(self):
        self.base_url = "{}://{}:{}".format(
            FrontendClusterSender.schema,
            FrontendClusterSender.host,
            FrontendClusterSender.port
        )

    def send(self, clusters):
        method = "/showClusters"
        url = self.base_url + method
        requests.post(url, json=clusters)

    def send_emergency_reasons(self, event_type, lat, lon, reasons: dict):
        method = "/notifyEmergencyDescription"
        url = self.base_url + method
        reason = max(reasons.items(), key=lambda x: x[1])[0]
        description = REASON_DESCRIPTIONS.get(reason, "Unknown")
        json_data = {
            "event": event_type,
            "lat": lat,
            "lon": lon,
            "description": description
        }
        requests.post(url, json=json_data)
