from tornado.web import Application

controllers = [

]


def create_application():
    urls = list(map(lambda handler: (handler.get_mapping(), handler), controllers))
    return Application(urls)

if __name__ == '__main__':
    app = create_application()
    app.listen(8889)
    