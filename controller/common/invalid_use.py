from controller.common.marshall_response import MarshallResponse
from controller.common import http_status
from controller.models.error_schema import ErrorSchema


class InvalidUsage(Exception):

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code:
            self.status_code = status_code
        else:
            self.status_code = http_status.HTTP_400_BAD_REQUEST

        self.payload = payload
        self.primary_name = 'error'
        self.primary_data = None
        self.session_data = None
        self.primary_unique = True

        '''Initialize our request and response handlers'''
        self.marshall = MarshallResponse(self.primary_name, self.primary_unique, ErrorSchema())

    def jsonapi(self):
        if self.payload:
            if isinstance(self.payload, dict):
                self.payload.update({
                    'message': self.message,
                    'status_code': self.status_code,
                    'id': 1
                })
        else:
            self.payload = {
                'message': self.message,
                'status_code': self.status_code,
                'id': 1
            }

        return self.marshall.jsonapi(self.payload)
