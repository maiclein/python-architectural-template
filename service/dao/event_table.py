import local
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'


class Event(Model):
    __table_name__ = 'event'

    person_id = columns.TimeUUID(primary_key=True)
    email_id = columns.Text(primary_key=True)
    label = columns.Text()
    last_verified_when = columns.DateTime()
    is_identifier = columns.Boolean()
    created = columns.DateTime()
