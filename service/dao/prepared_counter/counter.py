from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from common.cassandra_session import CassandraSession
from service.dao.cassandra_parent import CassandraParent

__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'


class Counter(Model):
    # __keyspace__ = local.CASSANDRA_KEYSPACE
    __table_name__ = 'counter'

    subscription_id = columns.TimeUUID(primary_key=True)
    person_id = columns.TimeUUID(primary_key=True)
    count_like = columns.Counter()
    count_favorite = columns.Counter()
    count_shared = columns.Counter()

class CountSubscriptionTable(CassandraParent):

    def __init__(self):
        cassandra_db = CassandraSession()
        self.__my_db_session = cassandra_db.get_session()
        self.__model = CountSubscription()
        super(CountSubscriptionTable, self).__init__()


    @property
    def db_session(self):
        return self.__my_db_session

    @property
    def columns(self):
        return self.__model.keys()

    @property
    def table_name(self):
        return 'counter'

    @property
    def keys(self):
        return ['subscription_id', 'person_id']

    @property
    def date_audit_columns(self):
        return []

    @property
    def order_by(self):
        return {}

    @property
    def record_expiry(self):
        return None
