from kaki.app import App
from kivy.factory import Factory as F
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

    def build_app(self):
        return F.InspectorApplicationRoot()


if __name__ == '__main__':
    Application().run()
