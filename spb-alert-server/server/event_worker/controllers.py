import logging
from tornado.web import RequestHandler


class TestHandler(RequestHandler):

    @staticmethod
    def get_mapping():
        return "/test"

    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        logging.warning("accepted get request to Test Handler")
