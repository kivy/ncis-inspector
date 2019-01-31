from kivy.factory import Factory as F
from kivy.properties import StringProperty, NumericProperty
from kivy.network.urlrequest import UrlRequest
from kivy.event import EventDispatcher
from kaki.app import App
from kivy.lang import global_idmap

from os import listdir
from os.path import splitext
from importlib import import_module
from urllib.parse import urlencode


def discover_classes():
    dirs = listdir('widgets')
    for d in dirs:
        if not d.endswith(('.py', '.pyc', '.pyo', '.pyd')):
            continue

        modname = splitext('widgets.{}'.format(d))[0]
        mod = import_module(modname, package=modname)
        symbols = mod.__all__
        for symbol in symbols:
            yield modname, modname


class DebuggerController(EventDispatcher):

    @classmethod
    def instance(cls):
        if not hasattr(self, "_instance"):
            self._instance = DebuggerController()
        return self._instance

    def request(self, path, callback=None, **kwargs):
        if not (self.target_ip and self.target_port):
            return False

        def handle_success(request, response):
            callback(True, response)

        def handle_failure(request, error):
            callback(False, error)

        def handle_error(request, error):
            callback(False, error)

        url = 'http://{host}:{port}{path}'.format(
            host=self.target_ip,
            port=self.target_port,
            path=path,
        )
        print(url)
        UrlRequest(
           url,
            on_success=handle_success,
            on_failure=handle_failure,
            on_error=handle_error,
        )
        return True


class DebuggerApplicationRoot(F.FloatLayout):
    def __init__(self, **kwargs):
        global app
        app = self
        self.ctl = DebuggerController.instance()
        global_idmap["dbg"] = self.ctl



class Application(App):
    CLASSES = dict(discover_classes())

    AUTORELOADER_PATHS = [
        ('.', {'recursive': True}),
    ]

    target_ip = StringProperty()
    target_port = NumericProperty()

    def build_app(self):
        return F.AppRoot()


if __name__ == '__main__':
    Application().run()
