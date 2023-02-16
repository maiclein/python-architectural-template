from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from common.cassandra_session import CassandraSession
from service.dao.cassandra_parent import CassandraParent


__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'


class Person(Model):
    __table_name__ = 'person'

    person_id = columns.TimeUUID(primary_key=True)
    entity_id = columns.Set(columns.TimeUUID())
    persona_id = columns.UUID()
    publisher_id = columns.UUID()
    name = columns.Text()
    image = columns.Text()
    account_plan = columns.Text()
    account_plan_expires = columns.DateTime()
    account_plan_purchased = columns.DateTime()
    birthday = columns.DateTime()
    language = columns.Text()
    passphrase = columns.Text()
    banned = columns.Boolean()
    disabled = columns.Boolean()
    default_socialmedia = columns.Map(columns.Text(), columns.Text())
    authn_identifier_id = columns.Text()
    identifier_id = columns.Text()
    identifier_id_2 = columns.Text()
    address_id = columns.TimeUUID()
    delivery_line_1 = columns.Text()
    delivery_line_2 = columns.Text()
    last_line = columns.Text()
    country = columns.Text()
    latitude = columns.Float()
    longitude = columns.Float()
    timezone = columns.Text()
    cookie_policy_signed = columns.DateTime()
    privacy_policy_signed = columns.DateTime()
    publisher_policy_signed = columns.DateTime()
    terms_of_use_signed = columns.DateTime()
    crowdsource_signed = columns.DateTime()
    require_secondary_authn = columns.Boolean()
    last_login = columns.DateTime()
    last_update = columns.DateTime()
    created = columns.DateTime()

class PersonTable(CassandraParent):

    def __init__(self):

        cassandra_db = CassandraSession()
        self.__my_db_session = cassandra_db.get_session()
        self.__model = Person()

        super(PersonTable, self).__init__()


    @property
    def db_session(self):
        return self.__my_db_session

    @property
    def columns(self):
        return self.__model.keys()

    @property
    def table_name(self):
        return 'person'

    @property
    def keys(self):
        return ['person_id']

    @property
    def date_audit_columns(self):
        return []

    @property
    def order_by(self):
        return {}

    @property
    def record_expiry(self):
        return None
