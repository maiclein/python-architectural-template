from uuid import uuid4
from service.dao.event_table import Event

__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'


class EventService:

    def create(self, person_id, persona_type, label=None, domain='simpledata.net', image=None, collection_id=None):

        q = Event(
            person_id=person_id,
            persona_id=uuid4(),
            type=persona_type,
            label=label,
            domain=domain,
            image=image,
            collection_id=collection_id,
        )

        response_obj = q.save()

        rv = dict(response_obj)
        print(rv)

        return rv

    def get(self, person_id, persona_id=None):

        if persona_id:
            filter_obj = Event.objects.filter(
                person_id=person_id,
                persona_id=persona_id,
            )

            response_obj = filter_obj.first()
            rv = dict(response_obj)

        else:
            filter_obj = Event.objects.filter(
                person_id=person_id,
            )
            rv = []
            persona_in = []
            for persona_set in filter_obj:
                persona_keys = dict(persona_set)
                persona_in.append(persona_keys.get('persona_id'))

            for persona in filter_obj.filter(persona_id__in=persona_in):
                rv.append(dict(persona))

        return rv

    def update(self, person_id, obj_data):

        obj_filter = Event.objects.filter(
            person_id=person_id,
            persona_id=obj_data.pop('persona_id'),
        )

        obj = obj_filter.get()
        obj.update(**obj_data)

        obj = obj.save()

        rv = dict(obj)

        return rv
