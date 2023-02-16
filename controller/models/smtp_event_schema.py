import logging
from marshmallow import Schema, fields, validates_schema, ValidationError


__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'


class SmtpEventSchema(Schema):
    did = fields.Method('encrypt_did', deserialize='decrypt_uuid', load_from='DID')
    id = fields.UUID(dump_only=True)
    aid = fields.Str(load_from='AID')
    user_agent = fields.Method('parse_user_agent', load_only=True, load_from='USER-AGENT', required=True)
    device_id = fields.Method(load_from='DID', load_only=True, deserialize='decrypt_uuid')
    device_session = fields.UUID(load_from='DSID', load_only=True)
    authorization_orig = fields.Str(load_only=True, load_from='AUTHORIZATION', allow_none=True)
    authorization = fields.Method(
        deserialize='process_authorization', load_only=True, load_from='AUTHORIZATION'
    )
    accelerometer = fields.Str(load_only=True)
    bluetooth_address = fields.Str(load_only=True)
    imei = fields.Str(load_only=True)
    meid = fields.Str(load_only=True)
    accept_language = fields.Method('parse_language', load_only=True, load_from='ACCEPT-LANGUAGE')
    network_operator = fields.Str(load_only=True)
    gyroscope = fields.Str(load_only=True)
    device_model = fields.Str(load_only=True)
    mac_address = fields.Str(load_only=True)
    nfc = fields.Str(load_only=True)
    serial_number = fields.Str(load_only=True)
    sim_operator = fields.Str(load_only=True)
    sim_serial_number = fields.Str(load_only=True)
    screen_resolution = fields.Str(load_only=True)
    screen_depth = fields.Str(load_only=True)
    browser_plugins = fields.Str(load_only=True)

    # @validates('quantity')
    # def validate_quantity(self, value):
    #     if value < 0:
    #         raise ValidationError('Quantity must be greater than 0.')
    #     if value > 30:
    #         raise ValidationError('Quantity must not be greater than 30.')

    def handle_error(self, exc, data):
        """Log and raise our custom exception when (de)serialization fails."""
        logging.error(exc.messages)
        logging.error(data)
        raise ValidationError(exc.messages)


