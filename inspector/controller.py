from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty, ObjectProperty)
from kivy.network.urlrequest import UrlRequest
from kivy.event import EventDispatcher
from kivy.lang import global_idmap
from kivy.clock import Clock
from itertools import chain
import threading
import requests
import traceback
import time
import sseclient
from collections import deque
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
    view = ObjectProperty(allownone=True)
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
        self._stream_q = deque()
        self._stream_clock = None
        self._stream_thread_args = {}
        self._stream_observers = []
        super(InspectorController, self).__init__(**kwargs)
        if self.target_host and self.target_port:
            self.connect()

    def request(
        self, path, callback=None, force=False, method='GET',
        params=None, headers=None
    ):
        if not self.is_connected and not force:
            return False

        headers = headers or {}

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
                req_headers=headers
            )
        elif method == 'POST':
            headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
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
                req_headers=headers
            )
        else:
            raise ValueError(
                "method must be one of ['GET', 'POST'] got '{}' instead"
                .format(method)
            )
        return True

    def connect(self):
        self.disconnect()

        def callback(status, resp):
            self.is_connecting = False
            if status == "ok":
                self.is_connected = True
                self._stream_start()
            else:
                self.is_connected = False
                self.error = repr(resp)

        self.request("/_/version", callback, force=True)

    def disconnect(self):
        self.is_connected = False
        self.error = ""
        self._stream_stop()

    def _stream_start(self):
        self._stream_q = deque()
        self._stream_thread_args = {
            "quit": False,
            "q": self._stream_q
        }
        self._stream_clock = Clock.schedule_interval(
            self._stream_read_queue, 1 / 30.)
        thread = threading.Thread(
            target=self._stream_listen,
            args=(self._stream_thread_args, ))
        thread.daemon = True
        thread.start()

    def _stream_stop(self):
        if self._stream_clock is not None:
            Clock.unschedule(self._stream_clock)
            self._stream_clock = None
        if self._stream_thread_args:
            self._stream_thread_args["quit"] = True

    def _stream_listen(self, args):
        while True:
            if args["quit"]:
                break
            try:
                self._stream_listen_once(args)
            except Exception as e:
                traceback.print_exc()
                # error while connecting to the stream?
                # retry after
                time.sleep(2)
                continue

    def _stream_listen_once(self, args):
        url = "http://{host}:{port}/_/stream".format(
            host=self.target_host, port=self.target_port)
        req = requests.get(url, stream=True)
        client = sseclient.SSEClient(req.iter_content())
        q = args["q"]
        for event in client.events():
            if args["quit"]:
                break
            q.appendleft(event)

    def _stream_read_queue(self, *largs):
        observers = self._stream_observers
        while True:
            try:
                event = self._stream_q.pop()
            except IndexError:
                break

            for observer in observers:
                ob_events = observer[1]
                if ob_events is None or event.event in ob_events:
                    try:
                        observer[0](event)
                    except Exception as e:
                        traceback.print_exc()

    def stream_bind(self, callback, events=None):
        self._stream_observers.append([callback, events])

    def stream_unbind(self, callback):
        self._stream_observers = [
            x for x in self._stream_observers
            if x[0] is not callback]