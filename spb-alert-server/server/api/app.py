from tornado.web import Application
from tornado.ioloop import IOLoop
from server.api.controllers import ApiPushEventHandler

controllers = [
    ApiPushEventHandler
]


# As it is main enter point to
def create_application():
    urls = list(map(lambda handler: (handler.get_mapping(), handler), controllers))
    return Application(urls)


if __name__ == '__main__':
    app = create_application()
    app.listen(8888)
    IOLoop.instance().start()
