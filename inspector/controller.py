from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty)
from kivy.network.urlrequest import UrlRequest
from kivy.event import EventDispatcher
from kivy.lang import global_idmap
from itertools import chain

from os import listdir, environ
from os.path import splitext, realpath, join
from importlib import import_module
from urllib.parse import urlencode

INSPECTOR_HOST = environ.get("INSPECTOR_HOST", "")
INSPECTOR_PORT = int(environ.get("INSPECTOR_PORT", 8765))

ctl = None

def discover_classes():
    import inspector
    import inspector.views
    import inspector.widgets

    rootdir = realpath(inspector.__path__._path[0])
    dirs = inspector.__path__._path
    dirs += inspector.views.__path__._path
    dirs += inspector.widgets.__path__._path

    for directory in dirs:
        for filename in listdir(directory):
            if not filename.endswith(('.py', '.pyc', '.pyo', '.pyd')):
                continue
            filename = splitext(filename)[0]
            d = realpath(directory).replace(rootdir, "")
            if d[1:]:
                # handle submodules (inspector.X.Y)
                d = "inspector." + d[1:]
                modname = d + "." + filename
            else:
                # handle root modules (inspector.X)
                modname = "inspector." + filename
            mod = import_module(modname, package=modname)
            symbols = getattr(mod, "__all__", [])
            for symbol in symbols:
                yield modname, modname


class InspectorController(EventDispatcher):
    target_host = StringProperty(INSPECTOR_HOST)
    target_port = NumericProperty(INSPECTOR_PORT)
    is_connected = BooleanProperty(False)
    is_connecting = BooleanProperty(False)
    error = StringProperty()

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            global ctl
            cls._instance = InspectorController()
            ctl = cls._instance
        return cls._instance

    def __init__(self, **kwargs):
        super(InspectorController, self).__init__(**kwargs)
        if self.target_host and self.target_port:
            self.connect()

    def request(
        self, path, callback=None, force=False, method='GET',
        params=None
    ):
        if not self.is_connected and not force:
            return False

        def handle_success(request, response):
            status = response["status"]
            if status == "ok":
                callback("ok", response["response"])
            elif status == "error":
                callback("error", response["error"])

        def handle_failure(request, error):
            callback("error", error)

        def handle_error(request, error):
            callback("error", error)

        if method == 'GET':
            url = 'http://{host}:{port}{path}{args}'.format(
                host=self.target_host,
                port=self.target_port,
                path=path,
                args=('?' + urlencode(params)) if params else ''
            )
            UrlRequest(
                url,
                on_success=handle_success,
                on_failure=handle_failure,
                on_error=handle_error,
            )
        elif method == 'POST':
            url = 'http://{host}:{port}{path}'.format(
                host=self.target_host,
                port=self.target_port,
                path=path,
            )
            UrlRequest(
                url,
                on_success=handle_success,
                on_failure=handle_failure,
                on_error=handle_error,
                req_body=urlencode(params or {}),
            )
        else:
            raise ValueError(
                "method must be one of ['GET', 'POST'] got '{}' instead"
                .format(method)
            )
        return True

    def connect(self):
        self.is_connecting = False
        self.error = ""

        def callback(status, resp):
            self.is_connecting = False
            if status == "ok":
                self.is_connected = True
            else:
                self.is_connected = False
                self.error = repr(resp)

        self.request("/_/version", callback, force=True)

    def disconnect(self):
        self.is_connected = False
        self.error = ""
