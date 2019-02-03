import json
from kivy.utils import escape_markup


class PythonObjectRepr(object):
    def __init__(self, o, refs=None, panel=None):
        super(PythonObjectRepr, self).__init__()
        self.o = o
        self.refs = refs
        self.panel = panel

    def render_full(self, oneline=False, noref=False, max=None):
        result = []
        size = 0
        for count, line in self._render_full(
                self.o, oneline=oneline, noref=noref, max=max):
            result.append(line)
            size += count
            if max and size > max:
                break
        joinchar = "" if oneline else "\n"
        return joinchar.join(result)

    def _render_full(self, o, oneline, noref, max):
        indent_str = "" if oneline else "  "
        commachr = ", " if oneline else ""
        if isinstance(o, (str, int, float, bytes)):
            repr_o = repr(o)
            yield len(repr_o), escape_markup(repr_o)

        elif isinstance(o, (list, tuple)):
            yield 1, (escape_markup("[") if isinstance(o, list) else "(")
            for index, entry in enumerate(o):
                is_last = index == len(o) - 1
                lines = list(self._render_full(entry, oneline, noref, max))
                for indexline, line in enumerate(lines):
                    count, line = line
                    is_last_indexline = indexline == len(lines) - 1
                    comma = commachr if (is_last_indexline and not is_last) else ""
                    count += len(indent_str) + len(comma)
                    yield count, indent_str + line + comma
            yield 1, (escape_markup("]") if isinstance(o, list) else ")")

        elif self.is_pyobject(o):
            yield self.convert_pyobject(o, noref=noref)

        elif isinstance(o, dict):
            yield 1, "{"
            items = list(o.items())
            for index, (key, entry) in enumerate(items):
                is_last = index == len(items) - 1
                count_key, repr_key = list(
                    self._render_full(key, oneline, noref, max))[0]
                lines = list(self._render_full(entry, oneline, noref, max))
                for indexline, line in enumerate(lines):
                    count, line = line
                    is_last_indexline = indexline == len(lines) - 1
                    comma = commachr if (is_last_indexline and not is_last) else ""
                    if indexline == 0:
                        count += len(indent_str) + count_key + count + len(comma) + 1
                        yield count, indent_str + repr_key + ": " + line + comma
                    else:
                        count += len(indent_str) + count + len(comma)
                        yield count, indent_str + line + comma
            yield 1, "}"

        elif o is None:
            yield 4, "[i][color=#909090]None[/color][/i]"
        else:
            msg = "<missing repr for {}>".format(type(o))
            yield len(msg), msg

    def is_pyobject(self, o):
        return isinstance(o, dict) and o.get("__pyobject__")

    def convert_pyobject(self, o, noref):
        pyo = o["__pyobject__"]
        if not noref:
            ref = self.panel.create_ref(o)
            if ref:
                text = "<{} object at 0x{:x}>".format(
                    pyo["type"], pyo["id"]
                )
                markup = "[color=#03A9F4][ref={}]{}[/ref][/color]".format(
                    ref, escape_markup(text))
                return len(text), markup

        text = "<{} object>".format(pyo["type"])
        return len(text), text
