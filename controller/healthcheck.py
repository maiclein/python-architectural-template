from flask_classy import FlaskView
from flask import current_app as app
from controller.common import http_status
from controller.common.invalid_use import InvalidUsage
from common.metaclass_members import OrderedClass

__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'

# Health check for load balancing purposes
# #TODO: Make the healthcheck smarter


class Healthcheck(FlaskView, metaclass=OrderedClass):


    def index(self):
        try:
            rv = app.response_class()
            status_code = http_status.HTTP_204_NO_CONTENT

            rv.status_code = status_code

            response = rv

        except Exception:
            raise InvalidUsage('Health check Failed Somehow', http_status.HTTP_400_BAD_REQUEST)

        return response
