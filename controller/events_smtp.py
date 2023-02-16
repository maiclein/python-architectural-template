import local
from flask_classy import FlaskView, route
from controller.common import http_status
from controller.common.invalid_use import InvalidUsage
from common.metaclass_members import OrderedClass
from controller.common.marshall_response import MarshallResponse
from controller.common.parse_request import RequestParser
from controller.models.smtp_event_schema import SmtpEventSchema
from controller.models.error_schema import ErrorSchema


__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'


class SmtpEvent(FlaskView, metaclass=OrderedClass):
    def __init__(self):
        ''' Primary endpoint ownership defined / stubbed '''
        self.primary_name = self.this_class_name
        self.primary_data = None
        self.session_data = None
        self.primary_unique = False
        self.device_id = None
        self.person_id = None
        self.device_session = None
        self.collection_service = CollectionService()
        '''Initialize our request and response handlers'''
        self.marshall_error = MarshallResponse('error', True, ErrorSchema())
        self.marshall = MarshallResponse(self.primary_name, self.primary_unique, SmtpEventSchema())
        self.parser = RequestParser(self.primary_name, CollectionSchema())

    def before_request(self, context, unparsed_collection_id=None):
        if unparsed_collection_id:
            self.primary_data, self.session_data = self.parser.get(context, collection_id=unparsed_collection_id)
        else:
            self.primary_data, self.session_data = self.parser.get(context)

        self.device_id = self.session_data.get('device_id')
        self.person_id = self.session_data.get('person_id')
        self.device_session = self.session_data.get('device_session')

    def after_request(self, context, response):
        self.primary_data = None
        self.session_data = None
        return response

    def index(self):

        try:
            persona = self.persona_service.get(self.person_id)
            rv = self.collection_service.get(self.person_id)

            response = self.marshall.jsonapi(rv, persona=persona)

        except Exception:
            raise InvalidUsage('Profile data not found', http_status.HTTP_400_BAD_REQUEST)

        return response

    @route('<unparsed_collection_id>')
    def get(self, unparsed_collection_id=None):

        try:
            rv = self.collection_service.get(self.person_id, self.primary_data.get('collection_id'))

            response = self.marshall.jsonapi(rv)

        except Exception:
            raise InvalidUsage('Collection not found', http_status.HTTP_400_BAD_REQUEST)

        return response

    def patch(self, unparsed_collection_id):

        try:
            rv = self.collection_service.update(self.person_id, self.primary_data)

            response = self.marshall.jsonapi(rv)

        except Exception:
            raise InvalidUsage('Collection update failed', http_status.HTTP_400_BAD_REQUEST)

        return response
