import logging
import pprint
import inflect
from flask import request
from werkzeug.contrib.cache import SimpleCache
from controller.common import http_status
from controller.common.invalid_use import InvalidUsage
from controller.models.did_schema import DidSchema
from controller.models.session_schema import SessionSchema
from controller.models.authenticated_schema import AuthenticatedSchema
from service.person import PersonService
from marshmallow import ValidationError


class RequestParser(object):

    def __init__(self, primary_name, primary_schema=None):
        self.primary_name = primary_name
        self.primary_schema = primary_schema
        self.session_schema = SessionSchema()
        self.authenticated_schema = AuthenticatedSchema()
        self.did_schema = DidSchema()
        self.return_data = ['POST', 'PATCH', 'PUT']
        self.no_authn = ['authn', 'token', 'did']
        self.cache = SimpleCache()
        self.person_service = PersonService()
        self.p = inflect.engine()
        self.pp = pprint.PrettyPrinter(indent=2)

    def get(self, context, strict=True, args=False, **kwargs):
        request_data = {}
        request_data = {**kwargs, **request_data}
        rv_error = None
        did_errors = None
        authn_errors = None

        if 'application/vnd.api+json' == request.content_type and context.upper() in self.return_data:
            try:
                # This will fail is there is no json data, skipping this.
                request_data_obj = request.get_json(force=True)

                # Check the type of the payload to make sure it's allowed
                obj_type = request_data_obj.get('data').get('type')

                if obj_type != self.primary_name and obj_type != self.p.plural(self.primary_name):
                    msg = 'Invalid json-api object passed: {} | {} / {}'.format(
                        obj_type, self.primary_name, self.p.plural(self.primary_name)
                    )
                    logging.error(msg)
                    raise InvalidUsage(msg, http_status.HTTP_400_BAD_REQUEST)

                request_data['id'] = request_data_obj.get('data').get('id')
                request_data['type'] = request_data_obj.get('data').get('type')
                request_data = {**request_data_obj.get('data').get('attributes'), **request_data}

            except Exception as e:
                # raise ValueError(e)
                logging.warning('APPLICATION/JSON-API Submitted with no content.')
                pass

        elif 'application/json' == request.content_type and context.upper() in self.return_data:
            try:
                request_data_obj = request.get_json()
                request_data = {**request_data_obj, **request_data}

            except Exception:
                logging.warning('APPLICATION/JSON Submitted with no content.')
                pass

        elif 'application/x-www-form-urlencoded' == request.content_type and context.upper() in self.return_data:

            try:
                request_data_obj = dict(request.form)
                if isinstance(request_data_obj, dict):
                    for key in request_data_obj:
                        if isinstance(request_data_obj[key], list):
                            if len(request_data_obj[key]) == 1:
                                request_data_obj[key] = request_data_obj[key][0]

                request_data = {**request_data_obj, **request_data}
            except Exception:
                logging.warning('X-WWW-FORM-URLENCODED Submitted with no content.')
                pass

        elif 'text/plain' == request.content_type or None is request.content_type:
            pass

        else:
            logging.error('Unknown Content type: {}'.format(request.content_type))
            raise InvalidUsage('', http_status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        cookies_raw = dict(request.cookies)
        cookies = {}
        for key in cookies_raw.keys():
            cookies.update({key.upper(): cookies_raw.get(key)})

        request_data = self.__add_other_request_info(strict, request_data, cookies)

        headers_raw = dict(request.headers)
        headers = {}

        for key in headers_raw.keys():
            if 'Cookie' != key:
                headers.update({key.upper(): headers_raw.get(key)})

            request_data = self.__add_other_request_info(strict, request_data, headers)

        if args:
            args = dict(request.args)
            request_data = self.__add_other_request_info(strict, request_data, args)

        else:
            logging.warning('Skipping Arg parsing')

        print('\n-=-=-=-=-=-=--= request data: response =-=-=-=-=-=')
        self.pp.pprint(request_data)
        print('-=-=-=-=-=-=--= request data: /response =-=-=-=-=-=\n')

        # Process our device and / or person data for the request.

        # print('\n-=-=-=-=-=-=--= did data: session =-=-=-=-=-=')
        try:
            did_data, did_errors = self.did_schema.load(request_data)

            self.pp.pprint(did_data)

            # print('\n-=-=-=-=-=-=--= did data: session =-=-=-=-=-=')
            # self.pp.pprint(did_data)
            # print('\n-=-=-=-=-=-=--= /did data: session =-=-=-=-=-=')

        except ValidationError as e:
            if isinstance(did_errors, dict):
                payload = {
                    'validation': did_errors,
                }
            else:
                payload = {
                    'validation': e.normalized_messages(),
                }
            logging.error('Attribute validation failed:\n', e.messages)

            raise InvalidUsage('Attribute validation failed', http_status.HTTP_400_BAD_REQUEST, payload)

        # Lets make the gate to the kingdom right here.

        session_data = {
            'device_id': did_data.get('device_id', None),
            'device_session': did_data.get('device_session', None),
            'authenticated': False
        }

        if self.primary_name not in self.no_authn:
            try:
                authn_data, authn_errors = self.authenticated_schema.load(did_data)
                # print('\n-=-=-=-=-=-=--= authorization data: response =-=-=-=-=-=')
                # self.pp.pprint(authn_data)
                # print('-=-=-=-=-=-=--= authorization data: /response =-=-=-=-=-=\n')
                session_data = self.person_service.get_session(
                    authn_data.get('device_id'),
                    authn_data.get('authorization'),
                    authn_data.get('device_session'),
                )

                if session_data:
                    session_data.update({'authenticated': True})
                else:
                    raise Exception('Session Expired.')


            except ValidationError as e:
                if isinstance(authn_errors, dict):
                    payload = {
                        'validation': authn_errors,
                    }
                else:
                    payload = {
                        'validation': e.normalized_messages(),
                    }
                logging.error('Attribute validation failed: {}\n'.format(e.messages))
                raise InvalidUsage('Authentication Required', http_status.HTTP_401_UNAUTHORIZED, payload)

        else:
            # Get the session even if not required

            if did_data.get('authorization', None):
                print('checking session', session_data)
                try:
                    existing_session = self.person_service.get_session(
                        did_data.get('device_id'),
                        did_data.get('authorization'),
                        did_data.get('device_session'),
                    )
                    print('existing session', existing_session)
                    if existing_session:
                        session_data.update(existing_session)
                except:
                    logging.warning('Invalid authorization header exits\n')

        self.pp.pprint(session_data)
        # print('-=-=-=-=-=-=--= did data: /session =-=-=-=-=-=\n')

        # Process our primary data for the request.
        print("\n-=-=-=-=-=-=-=-=-=-=-=-=--= request data: PRIMARY DATA =-=-=-=-=-=-=-=-=-=-=-=")
        try:
            if self.primary_schema and self.primary_schema == self.did_schema:
                rv = did_data

            elif self.primary_schema:
                rv, rv_error = self.primary_schema.load(request_data)

            else:
                rv = None

        except ValidationError as e:
            if isinstance(rv_error, dict):
                payload = {
                    'validation': did_errors,
                }
            else:
                payload = {
                    'validation': e.normalized_messages(),
                }
            raise InvalidUsage('Input processing failed', http_status.HTTP_400_BAD_REQUEST, payload)

        self.pp.pprint(rv)
        print('-=-=-=-=-=-=--= request data: PRIMARY ERRORS =-=-=-=-=-=')
        self.pp.pprint(rv_error)
        print('-=-=-=-=-=-=--= request data: /PRIMARY DATA =-=-=-=-=-=\n')

        return rv, session_data

    def __add_other_request_info(self, strict, response_obj, request_info):

        is_strict = self.__verify_strict(request_info, response_obj)

        if is_strict:
            rv = {**request_info, **response_obj}

        elif strict:
            raise InvalidUsage('Strict request parsing failed', http_status.HTTP_400_BAD_REQUEST)

        else:
            rv = {**request_info, **response_obj}
            logging.warning('Argument data is being overwritten by other data.')

        return rv

    @staticmethod
    def __verify_strict(dict_one, dict_two):
        response_set = frozenset(dict_one.keys())
        json_set = frozenset(dict_two.keys())
        intersection = response_set.intersection(json_set)
        rv = True

        # If the values are equal, it's just duplicate, let it pass.
        if intersection:
            for key in intersection:
                if dict_one.get(key) == dict_two.get(key):
                    pass
                else:
                    # Values aren't equal, not strict
                    msg = 'Argument data is being overwritten by other data: \n{}:\n{}\n{}'.format(key, dict_one.get(key), dict_two.get(key))
                    logging.warning(msg)
                    rv = False

        return rv
