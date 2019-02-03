from os.path import exists, dirname
from os import makedirs

from kaki.app import App
from kivy.factory import Factory as F
from kivy.properties import StringProperty
from inspector.controller import discover_classes


class Application(App):
    CLASSES = {
        "InspectorApplicationRoot": "inspector.app",
        "KivyInspectorView": "inspector.views.view_kivy"
    }
    # CLASSES = dict(discover_classes())  # Doesn't work cause self deps

    AUTORELOADER_PATHS = [
        ('inspector', {'recursive': True}),
    ]

    name = StringProperty("NCIS-Dash")

    def build_app(self):
        self.load_config()
        return F.InspectorApplicationRoot()

    def load_config(self):
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


if __name__ == '__main__':
    Application().run()
