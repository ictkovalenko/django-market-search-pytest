from web.analytics.models import Event


class Analytics(object):
    @staticmethod
    def track(event=None, user=None, entity_id=None, properties=None, commit=True):
        ev = Event()

        ev.event = event

        if user is not None and user.id is not None:
            ev.user = user

        if entity_id is not None:
            ev.entity_id = entity_id

        ev.properties = properties or {}

        print("TRACKING....", ev)
        print(event)
        print(properties)

        if commit:
            ev.save()

        return ev
