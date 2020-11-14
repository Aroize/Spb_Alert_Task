import time
import logging
import random
from collections import deque
from threading import Lock
from server.event_worker.model_connection import ModelEventSender
from server.event_worker.frontend_sender import FrontendClusterSender

# TODO(): need to set some threshold from stat conclusion
SLEEP_TIME = 5

QUEUE_EVENT_TIME = 12 * 60 * 60

# TODO(): move to config
EVENT_IDS = {0, 1, 2, 3}

NO_CLUSTER_ID = 0

EMERGENCY_THRESHOLD = 0.7


class Worker:
    queues = {i: (Lock(), deque()) for i in EVENT_IDS}

    @staticmethod
    def push(event):
        pair = Worker.queues[event.event_type]
        mutex: Lock = pair[0]
        queue: deque = pair[1]
        try:
            mutex.acquire()
            queue.appendleft(event)
        finally:
            mutex.release()

    def __init__(self):
        self.model_sender = ModelEventSender()
        self.frontend_sender = FrontendClusterSender()

    def run(self):
        logging.warning("Worker is started")
        while True:
            try:
                time.sleep(SLEEP_TIME)
                self.handle_events()
            except Exception as e:
                logging.warning(e)

    def handle_events(self):
        for queue in Worker.queues.values():
            self.handle_queue(*queue)

    def handle_queue(self, mutex: Lock, queue: deque):
        events = list()
        try:
            mutex.acquire()
            if len(queue) == 0:
                return
            last_event_timestamp = queue[0].timestamp
            # Drop events which are out of queue split time
            while len(queue) > 0:
                event = queue[-1]
                if last_event_timestamp - event.timestamp < QUEUE_EVENT_TIME:
                    break
                events.append(queue.pop())
            # merge last events
            for event in queue:
                events.append(event)
        finally:
            mutex.release()

        model_output = self.model_sender.send(events)
        clusters = self.create_clusters(model_output)
        self.frontend_sender.send(clusters)

    def create_clusters(self, events):
        clusters = self.rearrange_cluster_events(events)
        collapsed_clusters = []
        for c_id, events in clusters:
            if c_id == NO_CLUSTER_ID:
                events = self.map_no_cluster(events)
                collapsed_clusters.extend(events)
            else:
                collapsed_clusters.append(self.collapse_events(events))
        return collapsed_clusters

    def rearrange_cluster_events(self, events):
        clusters = {}
        for event in events:
            c_id = event["c_id"]
            if c_id not in clusters:
                clusters[c_id] = list()
            clusters[c_id].append(event)
        return clusters

    def map_no_cluster(self, events):
        events = list(map(
            lambda e: {
                "event": e["event"],
                "lat": e["lat"],
                "lon": e["lon"],
                "size": 0
            }, events))
        return events

    def collapse_events(self, events):
        event_type = events[0]["event"]
        lat_mean = sum(map(lambda event: event["lat"], events))
        lon_mean = sum(map(lambda event: event["lon"], events))
        prob = self.get_emergency_probability(events)
        if prob > EMERGENCY_THRESHOLD:
            # need to get cause of emergency
            event_size = 2
            reasons = self.request_cluster_reasons(events)
            self.send_emergency_reasons(event_type, lat_mean, lon_mean, reasons)
        else:
            event_size = 1
        return {
            "lat": lat_mean,
            "lon": lon_mean,
            "size": event_size,
            "type": event_type
        }

    def get_emergency_probability(self, cluster):
        response = self.model_sender.get_cluster_emergency(cluster)
        probability = response["prob"]
        return probability

    def request_cluster_reasons(self, cluster):
        reasons = self.model_sender.get_cluster_emergency_reasons(cluster)
        return reasons

    def send_emergency_reasons(self, event_type, lat, lon, reasons):
        self.frontend_sender.send_emergency_reasons(event_type, lat, lon, reasons)
