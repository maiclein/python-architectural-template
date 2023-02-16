from service.dao.cassandra_parent import CassandraParent

__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'

table_name = None
primary_key = None
additional_keys = None
db_session = None
request_format = None


class CassandraCounterParent(CassandraParent):
    counter_key = 'count'

    def __init__(self):

        if not self.db_session:
            raise Exception('Database Session is required.')

        if not self.table_name:
            raise Exception('Table Name is required.')

        if not self.keys:
            raise Exception('At least one Primary Key is required.')

        super().__init__()

    @property
    def default_counter_key_name(self):

        return self.counter_key

    def get_count(self, keys_and_values, **kwargs):
        """Returns only the counter value"""
        rows = super().get_by_key(keys_and_values, **kwargs)
        counter_key = kwargs.get('counter_key', self.default_counter_key_name)
        total_count = 0
        if rows:
            for row in rows:
                total_count += row.get(counter_key)

        return rows, total_count

    def decrement_counter(self, key, **kwargs):
        """Decrement the count of a counter_models by a specific value"""
        response = 0
        value = kwargs.get('value', 1)
        counter_key = kwargs.get('counter_key', self.default_counter_key_name)
        rows = self.__execute_statement(self.__create_counter_update_statement('-', value, key))

        if rows:
            for row in rows:
                row_dict = dict(zip([counter_key], row))
                response += row_dict.get(counter_key)

        return response

    def increment_counter(self, key, **kwargs):
        """Increment the count of a counter_models by a specific value"""
        response = 0
        value = kwargs.get('value', 1)
        counter_key = kwargs.get('counter_key', self.default_counter_key_name)
        rows = self.__execute_statement(self.__create_counter_update_statement('+', value, counter_key), key)

        for row in rows:
            row_dict = dict(zip([counter_key], row))
            response += row_dict.get(counter_key)

        return response

    def reset_counter(self, key):

        return "blah"

    def delete_counter(self, key):

        # super().delete(key)
        self.__execute_statement(self.__create_delete_statement(), key)

    def __create_delete_statement(self):

        return "DELETE FROM %s " % (self.table_name,)


    def __create_counter_query_statement(self, response_columns):

        query = "SELECT "
        last = len(response_columns) - 1
        count = 0
        for column in response_columns:
            query = query + column

            if count != last:
                query += ", "
                count += 1

            else:
                query += " "

        query = query + "FROM %s " % self.table_name

        return query

    def __create_counter_update_statement(self, operator, operand, counter_key):
        response = "UPDATE %s SET %s = %s %s %s " % (
            self.table_name, counter_key, counter_key, operator, str(operand)
        )

        return response

    def __execute_statement(self, statement, keys):
        where, bind_value = self.__generate_dml_where_clause_and_bind_list(keys)
        statement += where

        # print "::::::::::::::::::::::::::STATMENET::::::::::::::::::::::::::"
        # print statement

        prepared = self.db_session.prepare(statement, keys)
        rows = self.db_session.execute(prepared.bind(bind_value))

        return rows

    def __generate_dml_where_clause_and_bind_list(self, key_value):

        first = True
        bindvals = []
        for a, k in enumerate(self.keys):
            if k in key_value:
                if first is True:
                    clause = ' WHERE %s = ?' % (k)
                    first = False
                else:
                    clause += ' AND %s = ?' % (k)

                bindvals.append(key_value.get(k))

        return clause, bindvals

