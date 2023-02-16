from collections import OrderedDict
from datetime import datetime
import logging

__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'

class CassandraParent(object):
    table_name = None
    primary_key = None
    additional_keys = None
    db_session = None
    request_format = None
    keys = None

    def __init__(self):
        if not self.db_session:
            raise Exception('Database Session is required.')

        if not self.table_name:
            raise Exception('Table Name is required.')

        if not self.keys:
            raise Exception('At least one Primary Key is required.')

    def get_count(self, key):
        count_stmt = 'SELECT COUNT(*) FROM %s' % (self.table_name)

        where_clause, bind_vals = self.__generate_dml_where_clause_and_bind_list(key)

        stmt = count_stmt + where_clause
        prepared = self.db_session.prepare(stmt)

        row = self.db_session.execute(prepared.bind((bind_vals)))

        if row:
            zipped = dict(zip('c', row[0]))
            result = zipped.get('c')
        else:
            result = 0

        return result

    def get_unique(self, key):
        '''
        Get unique row by primary key
        @param key: unique primary key to use in where clause
        @param consistency_level (optional): Cassandra consistency level to use in query
        @return: dictionary of fields
        '''
        result = {}
        if key:
            row = self.__get_by_fields(key, None, [], [], [])

            if row is None or len(row) == 0:
                result = None
            elif len(row) > 1:
                raise Exception("Primary key is not unique")
            else: # len(row_list) == 1
                result = row[0]

        return result

    def get_by_key(self, key, **kwargs):
        '''
        Get unique row by primary key
        @param key: unique primary key to use in where clause
        @param consistency_level (optional): Cassandra consistency level to use in query
        @return: dictionary of fields
        '''
        result = []

        if key:
            result = self.__get_by_fields(
                key, kwargs.get('row_limit', None), kwargs.get('greater_than', []), kwargs.get('less_than', []),
                kwargs.get('in_clause', [])
            )

        return result


    # def get_nested(self, key):
    #     '''
    #     Get unique row by primary key
    #     @param key: unique primary key to use in where clause
    #     @param consistency_level (optional): Cassandra consistency level to use in query
    #     @return: dictionary of fields
    #     '''
    #     result_set = {}
    #
    #     rows = self.__get_by_fields(key)
    #
    #     if rows:
    #         for row in rows:
    #             for container in self.__response_format:
    #                 row_zip = {}
    #
    #                 if container not in result_set:
    #                     result_set[container] = []
    #
    #                 for a, field in enumerate(self.__response_format[container]):
    #                     row_zip[field] = row[field]
    #
    #                 result_set[container].append(row_zip)
    #
    #     return result_set

    def update(self, key, ttl=None):

        update, bind_vals = self.__create_update_statement(key, ttl)

        logging.debug(update)
        prepared = self.db_session.prepare(update)

        self.db_session.execute(prepared.bind(bind_vals))

        return key

    def insert(self, key, if_not_exists=False):
        '''
        create a row using the passed instance of the object
        @param obj: a dict of the object to insert
        @param unique_uuid_pk: an optional boolean for forcing a unique PK UUID.  If this is set to true
               then this method will check if the current PK UUID is unique, if it is not, a new
               UUID will be generated and checked.  If the PK for this table is not a UUID and this
               value is set to true, an exception will be raised.
        @return: primary key value.
        '''

        if self.record_expiry:
            ttl = self.record_expiry
        else:
            ttl = None

        insert, insert_object = self.__create_insert_statement(key, if_not_exists, ttl)

        # print "INSERT STATEMENT:::::::"
        # print insert
        # print insert_object

        # logging.debug(insert)
        prepared = self.db_session.prepare(insert)
        insert_query = prepared.bind(insert_object.values())


        self.db_session.execute(insert_query)

        return key

    def delete(self, key):
        '''
        Delete a row using the primary key and other fields
        @param fields: an instance of collections.OrderedDict where the first key/value pair must be the primary key

        '''
        if key and len(key) > 0:
            delete_stmt, bind_vals = self.__create_delete_statement(key)
            prepared = self.db_session.prepare(delete_stmt)

            return self.db_session.execute(prepared.bind((bind_vals)))

        else:
            raise Exception("Invalid parameter.  'key' cannot be empty")

    def add_set_value(self, key, attribute, value):
        # print(key)
        return self.__manage_sets_lists(key, attribute, value, 'set', '+')

    def remove_set_value(self, key, attribute, value):

        return self.__manage_sets_lists(key, attribute, value, 'set', '-')

    def add_list_value(self, key, attribute, value):

        return self.__manage_sets_lists(key, attribute, value, 'list', '+')

    def remove_list_value(self, key, attribute, value):

        return self.__manage_sets_lists(key, attribute, value, 'list', '-')

    def __create_update_statement(self, fields, ttl):
        bindvals = []
        first_where = True
        first_stmt = True

        if ttl:
            ttl_stmt = " USING TTL %d" % ttl
        else:
            ttl_stmt = ""

        stmt_start = "UPDATE %s%s SET" % (self.table_name, ttl_stmt)

        for k, a in fields.items():
            if k.lower() in self.columns and k.lower() not in self.keys:
                if a is not None:
                    if first_stmt:
                        stmt_items = " " + k + " = ?"
                        first_stmt=False
                    else:
                        stmt_items += " , " + k + " = ?"

                    # bindvals[k] = a
                    bindvals.append(a)

        for k in self.keys:
            if fields.get(k, None) is not None:
                if first_where is True:
                    stmt_where = ' WHERE %s = ?' % k
                    first_where = False
                else:
                    stmt_where += ' AND %s = ?' % k

                # bindvals[k] = fields.get(k)
                bindvals.append(fields.get(k))

        update_stmt = stmt_start + stmt_items + stmt_where

        return update_stmt, bindvals

    def __manage_sets_lists(self, key, attribute, value, type, operation):

        if type == 'set':
            first = "{"
            second = "}"
        elif type == "list":
            first = "["
            second = "]"
        else:
            raise Exception('Invalid type passed for management.')

        stmt = "UPDATE %s SET %s = %s %s %s %s %s" % (self.table_name, attribute, attribute, operation, first, value, second)
        where_clause, bind_vals = self.__generate_dml_where_clause_and_bind_list(key)

        stmt += where_clause

        # print(stmt)

        prepared = self.db_session.prepare(stmt)
        rv = self.db_session.execute(prepared.bind(bind_vals))

        return rv

    def __create_delete_statement(self, fields):
        delete_stmt = 'DELETE FROM %s' % (self.table_name)
        where_clause, bind_vals = self.__generate_dml_where_clause_and_bind_list(fields)

        delete_stmt += where_clause

        return delete_stmt, bind_vals

    def __create_insert_statement(self, obj, if_not_exists=False, ttl=None):
        insert_obj = OrderedDict()

        for key, val in obj.items():
            if key.lower() in self.columns or key.lower() in self.keys:
                insert_obj[key] = val

        if self.date_audit_columns:
            for date_key in self.date_audit_columns:
                insert_obj[date_key] = datetime.utcnow()

        place_holders = ", ".join('?' * len(insert_obj))
        insert_stmt = "INSERT INTO %s (%s) VALUES (%s)" % (self.table_name, ', '.join(insert_obj.keys()), place_holders)

        if if_not_exists:
            insert_stmt += " IF NOT EXISTS "

        if ttl:
            insert_stmt += self.__generate_ttl_clause(ttl)

        return insert_stmt, insert_obj


    def __get_by_fields(self, fields, row_limit, greater_than, less_than, in_clause):
        '''
        Get rows by field values
        @param fields: name value pairs to us in where clause of query
        @param consistency_level: Cassandra consistency level to use in query
        @param row_limit: maximum number of rows to return.
        @return: ResultSet object (can be iterated like a list).
        '''
        rv = []
        bindvals = []

        select = 'SELECT %s FROM %s' % (', '.join(self.columns), self.table_name)
        first = True
        for a, k in enumerate(self.keys):
            if k in fields:
                if fields.get(k, None) is not None:
                    if not first:
                        select += ' AND '
                    else:
                        select += ' WHERE '
                        first = False

                    if k in greater_than:
                        select +=  '%s > ?' % k

                    if k in less_than:
                        select += '%s < ?' % k

                    if k in in_clause:
                        select += '%s in ?' % k

                    if k not in in_clause and k not in less_than and k not in greater_than:
                        select += '%s = ?' % k

                    bindvals.append(fields.get(k))

        if row_limit:
            select += " LIMIT " + str(row_limit) + " "

        prepared = self.db_session.prepare(select)
        for row in self.db_session.execute(prepared.bind((bindvals))):
            rv.append(row)

        return rv

    def __generate_ttl_clause(self, ttl):
        ttl_stmt = ""
        if ttl:
            try: # make sure this is an int
                tmp = int(ttl)
                ttl_stmt = " USING TTL " + str(tmp)
            except:
                pass

        return ttl_stmt

    def __generate_dml_where_clause_and_bind_list(self, keyValue):

        first = True
        bindvals = []
        clause = ''
        for a, k in enumerate(self.keys):
            if k in keyValue:
                if first is True:
                    clause += ' WHERE %s = ?' % (k)
                    first = False
                else:
                    clause += ' AND %s = ?' % (k)

                bindvals.append(keyValue.get(k))

        return clause, bindvals

