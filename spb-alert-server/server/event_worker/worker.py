import time
import logging
from queue import LifoQueue


# TODO(): need to set some threshold from stat conclusion
SLEEP_TIME = 5

# TODO(): move to config
EVENT_IDS = {0, 1, 2, 3}


class Worker:

    queues = { i: LifoQueue() for i in EVENT_IDS }

    @staticmethod
    def push(event):
        queue: LifoQueue = Worker.queues[event.event_type]
        queue.put(event)

    def run(self):
        logging.info("Worker is started")
        while True:
            try:
                time.sleep(SLEEP_TIME)
                self.handle_events()
            except Exception as e:
                logging.info(e)

    def handle_events(self):
        # need to specify count
        pass
