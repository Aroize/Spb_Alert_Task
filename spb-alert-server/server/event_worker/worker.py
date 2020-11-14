import time
import logging
import random
from collections import deque
from threading import Lock
from server.event_worker.model_connection import ModelEventSender
from server.event_worker.frontend_sender import FrontendClusterSender


# TODO(): need to set some threshold from stat conclusion
SLEEP_TIME = 5

# TODO(): move to config
EVENT_IDS = {0, 1, 2, 3}


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

    """
    {event, lat, lon, ts, c_id}
    """
    def handle_queue(self, mutex: Lock, queue: deque):
        events = list()
        try:
            mutex.acquire()
            # TODO(): need to handle ts to understand do we need to process the queue
            while len(queue) != 0:
                # TODO(): remove popping elements from queue
                events.append(queue.popleft())
        finally:
            mutex.release()
        # queue is cleared, so we need no mutex now
        model_output = self.model_sender.send(events)
        clusters = self.create_clusters(model_output)
        self.frontend_sender.send(clusters)

    def create_clusters(self, events):
        clusters = self.rearrange_cluster_events(events)
        collapsed_clusters = []
        for c_id, events in clusters:
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

    def collapse_events(self, events):
        event_type = events[0]["event"]
        lat_mean = sum(map(lambda event: event["lat"], events))
        lon_mean = sum(map(lambda event: event["lon"], events))
        event_size = random.randint(0, 2)
        return {
            "lat": lat_mean,
            "lon": lon_mean,
            "size": event_size,
            "type": event_type
        }
