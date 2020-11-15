from threading import Thread
from tornado.web import Application
from tornado.ioloop import IOLoop
from server.event_worker.worker import Worker
from server.event_worker.controllers import InternalAppendEvent

controllers = [
    InternalAppendEvent
]


def create_application():
    urls = list(map(lambda handler: (handler.get_mapping(), handler), controllers))
    return Application(urls)


if __name__ == '__main__':
    app = create_application()
    app.listen(8889)
    worker = Worker()
    thread = Thread(target=worker.run)
    thread.start()
    IOLoop.instance().start()

