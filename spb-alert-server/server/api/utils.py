from datetime import datetime


# TODO(): Move to config
EVENT_MAPPER = {
    "fire": 0,
    "accident": 1,
    "bad_cold_water": 2,
    "bad_hot_water": 3
}

# TODO(): Move to config
DISTRICT_MAPPER = {}


class ApiPushEvent:

    def __init__(self, json):
        # mandatory parameters
        date = json["date"]
        self.timestamp = self.parse_date(date)
        event = json["event"]
        self.event_type = EVENT_MAPPER[event]
        lat = json["lat"]
        self.lat = self.parse_coordinate(lat)
        lon = json["lon"]
        self.lon = self.parse_coordinate(lon)

        # optional parameters
        self.address_eac = json.get("address_eac", 0)
        self.building_eac = json.get("building_eac", 0)
        district = json.get("district", "")
        self.district_id = DISTRICT_MAPPER.get(district, -1)

    @staticmethod
    def parse_date(date):
        time_pattern = "%m/%d/%y %H:%M"
        return int(datetime.strptime(date, time_pattern).timestamp())

    @staticmethod
    def parse_coordinate(coord):
        return float(coord.replace(",", "."))

    def __str__(self):
        return "ApiPushEvent\n[\n\tevent = {}\n\ttimestamp = {}\n\tlat = {}\n\tlon = {}\n]"\
            .format(self.event_type, self.timestamp, self.lat, self.lon)
