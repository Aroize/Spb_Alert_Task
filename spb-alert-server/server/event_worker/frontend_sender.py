import requests

REASON_DESCRIPTIONS = {
    "unusual_temperature": "Аномальная температура воздуха",
    "unusual_pressure": "Аномальное давление",
    "unusual_wetness": "Аномальная влажность",
    "unusual_visibility": "Аномальная видимость"
}


class FrontendClusterSender:

    def __init__(self):
        self.base_url = "{}://{}:{}".format(
            "http", "localhost", 8889
        )

    @staticmethod
    def get_mapping():
        return r"/"

    def send(self, clusters):
        method = "/showClusters"
        url = self.base_url + method
        requests.get(url, json=clusters)

    def send_emergency_reasons(self, event_type, lat, lon, reasons: dict):
        method = "/notifyEmergencyDescription"
        reason = max(reasons.items(), key=lambda x: x[1])[0]
        description = REASON_DESCRIPTIONS.get(reason, "Unknown")
        json_data = {
            "event": event_type,
            "lat": lat,
            "lon": lon,
            "description": description
        }
        url = self.base_url + method
        requests.get(url, json=json_data)
