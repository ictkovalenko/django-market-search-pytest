import json
from collections import OrderedDict

from django_json_widget.widgets import JSONEditorWidget as BaseJSONEditorWidget


class JSONEditorWidget(BaseJSONEditorWidget):
    def render(self, name, value, attrs=None):
        # Sort keys alphabetically
        items = sorted(json.loads(value).items(), key=lambda x: x[0])
        return super().render(name, json.dumps(OrderedDict(items)), attrs)
