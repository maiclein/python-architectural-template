import json
import pprint
import logging
from flask import current_app as app
from dateutil.tz import tzutc
from copy import copy, deepcopy
from controller.common import http_status
# from controller.common.invalid_use import InvalidUsage

__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'


class MarshallResponse(object):

    def __init__(self, primary_name, unique, primary_schema, **kwargs):
        self.primary_name = primary_name
        self.primary_name_id = self.primary_name + '_id'
        self.primary_schema = primary_schema
        self.unique = unique
        self.pp = pprint.PrettyPrinter(indent=2)
        self.rel_obj_schemas = {}
        for rel_obj_schema in kwargs:
            self.rel_obj_schemas.update({rel_obj_schema: kwargs.get(rel_obj_schema)})

    def jsonapi(self, primary_data_raw, **kwargs):
        data_response_counter = 0

        try:

            if primary_data_raw:
                if isinstance(primary_data_raw, list):
                    primary_data = primary_data_raw
                elif isinstance(primary_data_raw, dict):
                    primary_data = [primary_data_raw]
                elif isinstance(primary_data_raw, tuple):
                    primary_data = [dict(primary_data_raw)]
                else:
                    msg = 'marshall_response: uniqueness conflict: {}'.format(self.primary_name)
                    logging.error(msg)
                    raise Exception(msg)

                data = []
                included = []
                logging.debug("-=-=-=-=-=-=--= primary data =-=-=-=-=-=\n")
                logging.debug("Primary Data Raw: ", primary_data_raw, "\n")
                for primary_data_item_raw in primary_data:
                    # Cleaning up outgoing data.
                    # #TODO: Handle errors better
                    logging.debug("Primary Data Item Raw: ", primary_data_item_raw, "\n")

                    primary_item, item_errors = self.primary_schema.dump(primary_data_item_raw)
                    primary_id = primary_item.get('id')
                    related_data = {
                        self.primary_name: primary_item
                    }
                    logging.debug("Primary Item: ", primary_item, "\n")

                    for rel_obj_name in kwargs:
                        if self.primary_name != rel_obj_name:
                            rel_data = []
                            rel_obj_id = rel_obj_name + '_id'
                            logging.debug("-=-=-=-=-=-=--= found data item in kwargs =-=-=-=-=-=\n")

                            logging.debug("Data item name: ", rel_obj_name, "\n")
                            logging.debug("Data item id: ", rel_obj_id, "\n")

                            rel_obj_raw = kwargs.get(rel_obj_name)
                            rel_obj_schema = self.rel_obj_schemas.get(rel_obj_name, None)

                            # Covert whatever it is to an array for easy processing.
                            if isinstance(rel_obj_raw, list):
                                rel_obj_data = rel_obj_raw
                            elif isinstance(rel_obj_raw, dict):
                                rel_obj_data = [rel_obj_raw]
                            elif isinstance(rel_obj_raw, tuple):
                                rel_obj_data = [dict(rel_obj_raw)]
                            else:
                                msg = 'marshall_response: other data passed in bad format {} {}'.format(type(rel_obj_raw), rel_obj_name)
                                logging.error(msg)
                                raise Exception(msg)

                            logging.debug("Other Data: ", rel_obj_data, "\n")

                            for rel_obj in rel_obj_data:
                                logging.debug("Data payload: ", rel_obj, "\n")
                                # print("Data payload: ", rel_obj, "\n")
                                if primary_data_item_raw.get(rel_obj_id, None):
                                    if primary_data_item_raw.get(rel_obj_id) == rel_obj.get(rel_obj_id):
                                        logging.debug("Found match by data item id: ", primary_item, "\n")
                                        rel_data.append(rel_obj.get(rel_obj_id))
                                        rel_obj_clean, rel_obj_error = rel_obj_schema.dump(rel_obj)
                                        included.append(self.data_to_jsonapi_obj(rel_obj_name, rel_obj_clean))

                                elif self.primary_name_id in rel_obj_data:
                                    if primary_id == rel_obj.get(self.primary_name_id):
                                        logging.debug("Found match by primary item id: ", primary_item, "\n")
                                        rel_data.append(rel_obj.get(rel_obj_id))
                                        rel_obj_clean, rel_obj_error = rel_obj_schema.dump(rel_obj)
                                        included.append(self.data_to_jsonapi_obj(rel_obj_name, rel_obj_clean))
                                else:
                                    print("No match found")
                                    logging.debug("No match found")

                                related_data.update({
                                    rel_obj_name: rel_data
                                })
                                logging.debug("-=-=-=-=-=-=--= /found data item in kwargs =-=-=-=-=-=\n")

                    logging.debug("-=-=-=-=-=-=--= related data =-=-=-=-=-=")
                    logging.debug(related_data)
                    logging.debug("-=-=-=-=-=-=--= /related data =-=-=-=-=-=")

                    primary_data_item = self.__one_full_jsonapi(**related_data)
                    data.append(primary_data_item)
                    data_response_counter += 1

                # Put together our final JSON-API data object
                if self.primary_name == 'error':
                    status_code = primary_data_raw.get('status_code', http_status.HTTP_400_BAD_REQUEST)
                    response_data = {
                        'count': data_response_counter,
                        'links': {},
                        'data': data[0],
                    }
                elif len(data) == 1:
                    response_data = {
                        'count': data_response_counter,
                        'links': {},
                        'data': data[0],
                    }
                    status_code = http_status.HTTP_200_OK

                elif len(data) > 1 and not self.unique:
                    response_data = {
                        'count': data_response_counter,
                        'links': {},
                        'data': data,
                    }
                    status_code = http_status.HTTP_200_OK

                elif len(data) > 1 and self.unique:
                    logging.error('Uniqueness declared, but more than one item given to parse.')
                    raise Exception('marshall_response: 91')

                else:
                    response_data = None
                    status_code = http_status.HTTP_204_NO_CONTENT

                if len(included) >= 1 and response_data:
                    response_data.update({
                        'included': included,
                    })

            else:
                status_code = http_status.HTTP_204_NO_CONTENT
                response_data = None

            logging.debug('-=-=-=-=-=-=--= jsonapi response data =-=-=-=-=-=')
            self.pp.pprint(response_data)
            logging.debug('-=-=-=-=-=-=--= jsonapi response data =-=-=-=-=-=')

            # Clean it all up and send it!
            json_data = ComplexJSONRenderer(encoder=TypeSafeJSONEncoder).render(response_data, 2)
            rv = app.response_class(json_data, mimetype='application/vnd.api+json')

            # print('PRIMARY NAME: ', self.primary_name)
            # if self.primary_name == 'error':
            #     print('changing status code:', status_code)
            #     status_code = response_data.get('status_code', status_code)

            rv.status_code = status_code
        except Exception:
            logging.error('Uncaught error in marshall response.')
            raise

        return rv

    def __one_full_jsonapi(self, **kwargs):
        include_obj = None

        if self.primary_name in kwargs:
            if isinstance(kwargs.get(self.primary_name), dict):
                primary_data = kwargs.get(self.primary_name)
                include_obj = []

                for rel_data_name in kwargs:
                    relationships_data = []

                    if self.primary_name != rel_data_name:
                        logging.debug('RELATIONSHIP DATA NAME: ', rel_data_name, '\n')
                        logging.debug('RELATIONSHIP DATA: ', kwargs.get(rel_data_name), '\n')
                        for rel_data_id in kwargs.get(rel_data_name):
                            # rel_data = deepcopy(kwargs.get(rel_data_name))
                            relationships_data.append({'type': rel_data_name, 'id': rel_data_id})

                    if len(relationships_data) == 1:
                        relationships = {
                            rel_data_name: {'data': relationships_data[0]}
                        }
                    elif len(relationships_data) > 1:
                        relationships = {
                                rel_data_name: {'data': relationships_data}
                        }

                    else:
                        relationships = None

                    if relationships:
                        primary_data['relationships'] = relationships

                response = self.data_to_jsonapi_obj(self.primary_name, primary_data)

                response.update({
                    'links': {},
                })

            else:

                raise Exception('Marshall: Unknown primary data type sent.')
        else:
            response = None

        return response

    @staticmethod
    def data_to_jsonapi_obj(primary_name, data_dict):

        if isinstance(data_dict, dict):
            data_dict_copy = copy(data_dict)

            if 'relationships' in data_dict_copy:
                response = {
                    'relationships': data_dict_copy.pop('relationships'),
                }
            else:
                response = {}

            response.update({
                'id': data_dict_copy.pop('id'),
                'type': primary_name,
                'attributes': data_dict_copy,
            })

        else:
            response = None

        return response

    def jsonstandard(self, primary_data_raw):

        primary_item, item_errors = self.primary_schema.dump(primary_data_raw)

        logging.debug('-=-=-=-=-=-=--= plane jane json response data =-=-=-=-=-=')
        #self.pp.pprint(primary_item)
        logging.debug('-=-=-=-=-=-=--= plane jane json response data =-=-=-=-=-=')

        if isinstance(primary_item, dict):

            json_data = ComplexJSONRenderer(encoder=TypeSafeJSONEncoder).render(primary_item, 2)
            rv = app.response_class(json_data, mimetype='application/json')

            if self.primary_name == 'error':
                logging.error('Error being returned from jsonstandard')
                status_code = primary_item.get('status_code', http_status.HTTP_200_OK)
            else:
                status_code = http_status.HTTP_200_OK

        else:
            rv = app.response_class()
            status_code = http_status.HTTP_204_NO_CONTENT

        rv.status_code = status_code

        return rv

class MultiDimensionalArrayEncoder(json.JSONEncoder):

    def encode(self, obj):
        def hint_tuples(item):

            # #TODO: Encode all data resonse types according to contract here.
            if isinstance(item, tuple):
                return {'__tuple__': True, 'items': item}
            if isinstance(item, list):
                return [hint_tuples(e) for e in item]
            elif isinstance(item, dict):
                rv = {}
                for k in item.keys():
                    rv[k] = hint_tuples(item.get(k))
                return rv
            elif hasattr(item, 'isoformat'):
                # Formatting dates into ISO 8601 format for return
                return item.replace(tzinfo=tzutc()).isoformat()
            else:
                return item

        return super(MultiDimensionalArrayEncoder, self).encode(hint_tuples(obj))

    def default(self, o):
        return o.__class__.__name__


class TypeSafeJSONEncoder(MultiDimensionalArrayEncoder):
    def default(self, o):
        return str(o)


class ComplexJSONRenderer(object):
    encoder_class = MultiDimensionalArrayEncoder

    def __init__(self, encoder=MultiDimensionalArrayEncoder):
        super(ComplexJSONRenderer, self).__init__()
        self.encoder_class = encoder

    def render(self, data, indent=None):
        if data is None:
            return bytes()

        try:
            if indent:
                indent = max(min(int(indent), 8), 0)
        except (ValueError, TypeError):
            indent = None

        return json.dumps(data, cls=self.encoder_class, indent=indent,
                          ensure_ascii=True)
