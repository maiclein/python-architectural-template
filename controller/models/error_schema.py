import logging
from marshmallow import Schema, fields, validates_schema, ValidationError

__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'


class ErrorSchema(Schema):
    id = fields.Integer(required=True, missing=1000)
    message = fields.Str()
    status_code = fields.Integer()
    validation = fields.Dict(fields.Str())

    def handle_error(self, exc, data):
        """Log and raise our custom exception when (de)serialization fails."""
        logging.error(exc.messages)
        logging.error(data)
        raise ValidationError(exc.messages)
