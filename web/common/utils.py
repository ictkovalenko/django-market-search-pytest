from django.core.serializers.json import DjangoJSONEncoder


class PythonJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)
        return super().default(o)
