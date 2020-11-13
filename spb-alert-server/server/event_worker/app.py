from tornado.web import Application
from tornado.ioloop import IOLoop
from server.event_worker.worker import Worker
import _thread

controllers = [

]


def create_application():
    urls = list(map(lambda handler: (handler.get_mapping(), handler), controllers))
    return Application(urls)


if __name__ == '__main__':
    app = create_application()
    app.listen(8889)
    worker = Worker()
    _thread.start_new_thread(worker.run, ())
    IOLoop.instance().start()
