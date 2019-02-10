from os.path import exists, dirname
from os import makedirs, environ
from kivy.factory import Factory as F
from kivy.properties import StringProperty
from kivy.resources import resource_add_path
from ncis_inspector.controller import discover_classes

try:
    from kaki.app import App
    IS_KAKI_APP = True
except ImportError:
    IS_KAKI_APP = False
    if environ.get("DEBUG"):
        print("Kaki is missing, use Kivy app, but reloading will be missed")


class Application(App):
    CLASSES = {
        "InspectorApplicationRoot": "ncis_inspector.app",
        "KivyInspectorView": "ncis_inspector.views.view_kivy"
    }
    # CLASSES = dict(discover_classes())  # Doesn't work cause self deps

    AUTORELOADER_PATHS = [
        ('ncis_inspector', {'recursive': True}),
    ]

    name = StringProperty("NCIS-Dash")

    if IS_KAKI_APP:
        def build_app(self):
            self.load_config()
            return F.InspectorApplicationRoot()
    else:
        def build(self):
            self.load_config()
            return F.InspectorApplicationRoot()

    def load_config(self):
        resource_add_path(dirname(__file__))
        config = super(Application, self).load_config()
        if not config.filename:
            config.filename = self.get_application_config()

    def build_config(self, config):
        config.setdefaults('general', {
            'version': '0'
        })

    def get_application_config(self):
        if exists('{}.ini'.format(self.name)):
            path = '{}.ini'.format(self.name)
        else:
            path = '{}/%(appname)s.ini'.format(
                self.user_data_dir
            )

        cfg = super(Application, self).get_application_config(path)
        d = dirname(cfg)
        if d and not exists(d):
            makedirs(d)
        return cfg


def main():
    Application().run()


if __name__ == '__main__':
    main()
