from kivy.factory import Factory as F
from kaki.app import App
from os import listdir
from os.path import splitext
from importlib import import_module


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


class AppRoot(F.FloatLayout):
    pass


class Application(App):
    CLASSES = dict(discover_classes())

    AUTORELOADER_PATHS = [
        ('.', {'recursive': True}),
    ]

    def build(self):
        return F.AppRoot()


if __name__ == '__main__':
    Application().run()
