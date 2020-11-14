from tornado.websocket import WebSocketHandler

REASON_DESCRIPTIONS = {}


class FrontendClusterSender(WebSocketHandler):

    def data_received(self, chunk):
        pass

    def on_message(self, message):
        pass

    @staticmethod
    def get_mapping():
        return "/"

    def send(self, clusters):
        self.write_message({"method": "/showClusters", "data": clusters})

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
        self.write_message({"method": method, "data": json_data})
