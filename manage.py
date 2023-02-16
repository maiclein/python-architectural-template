import os
import sys
import getopt
import local
import traceback
import logging
from flask import Flask, jsonify
from cassandra.cqlengine import connection
from common.encryption_factory import EncryptionFactory


__author__ = 'mhoward'
__tag__ = 'pvi50Dm1v4s741oCN8Ul_aYrtb5nexB$8dh3ZJlVZdRejIGonT'


class Usage(Exception):
    def __init__(self, msg, code):
        Exception.__init__(self)
        self.msg = msg
        self.code = code


def main(argv=None):

    if argv is None:
        argv = sys.argv
    try:

        try:
            # TODO: List the flags that will be allowed
            opts, args = getopt.getopt(argv[1:], local.CMD_FLAGS, local.CMD_FLAG_WORDS)
        except Exception(getopt.error, "An error occured"):
            raise Usage("An error occured", 2)

        # process options
        for o, a in opts:
            # TODO: Process any flags
            if o in ("-h", "--help"):
                usage_msg = "\n-d <directory>"
                usage_msg += "\n-h this message"
                usage_msg += "<directory>\n"
                raise Usage(usage_msg, 0)

            elif o in("-d", "--dir"):
                # TODO: Directory checking here as an example
                if os.path.isdir(a):
                    directory = a
                else:
                    usage_msg = "%s is is not accessible." % a
                    raise Usage(usage_msg, 2)

        # process(arg) # process() is defined elsewhere
        for arg in args:
            # TODO: Process any arguments
            continue

        # TODO: Deal with arguments and flags, leaving the argument parsing part of program.

    except Exception:

        print(sys.stderr)
        print(sys.stderr, "for help use --help")
        if __doc__:
            print(__doc__)
        Usage("An error occured", 2)
        return None

    start_api_service()


def start_api_service(flask_ip=None, flask_port=None):

    # Encryption Singleton
    EncryptionFactory()

    # try:
    #     symmetric = EncryptionFactory().get_default_symmetric_class()
    #     asymmetric = EncryptionFactory().get_default_asymmetric_class()
    # except Exception as e:
    #     logging.error('Default encryption key not set: %s' % e.message)
    #     os.kill(os.getpid(), signal.SIGINT)

    app = Flask(__name__.split('.')[0], instance_relative_config=True)
    # Load the default configuration
    app.config.from_object('config.default')

    # Load the configuration from the instance folder
    # print("Hey, lets find this config.py")
    # filename = os.path.join(renderer.instance_path, 'config.py')
    # print(filename)
    app.config.from_pyfile('/opt/simpledata/auth-person/instance/config.py')

    # Load the file specified by the APP_CONFIG_FILE environment variable
    # Variables defined here will override those in the default configuration
    app.config.from_envvar('APP_CONFIG_FILE')

    # renderer.config['UPLOAD_FOLDER'] = l.PHOTO_UPLOAD_FOLDER
    app.url_map.strict_slashes = False

    app.config.update(
        DEBUG=app.config.get('DEBUG', False),
        TESTING=app.config.get('TESTING', False),
        TEMPLATES_AUTO_RELOAD=app.config.get('TEMPLATES_AUTO_RELOAD', False)
    )

    if flask_ip is None:
        flask_ip = app.config.get('DEFAULT_IP')

    if flask_port is None:
        flask_port = app.config.get('DEFAULT_PORT')

    # Setup our Cassandra connections.
    connection.setup(app.config.get('CASSANDRA_NODES'), app.config.get('CASSANDRA_KEYSPACE'), protocol_version=3)

    # Did.register(app, route_prefix='/api')
    # Authn.register(app, route_prefix='/api')
    # Healthcheck.register(app, route_prefix='/api')
    # Token.register(app, route_prefix='/api/authn')
    # Person.register(app, route_prefix='/api')
    # Collection.register(app, route_prefix='/api')
    # Persona.register(app, route_prefix='/api')
    # Email.register(app, route_prefix='/api')

    print(app.url_map)

    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        # We don't send traces to the outside world.
        # traceback.print_exc(file=sys.stdout)
        trace = traceback.format_exc()
        logging.error(trace)
        return error.jsonapi()

    @app.errorhandler(ValueError)
    def handle_invalid_usage(error):
        print('here in valueerror')
        trace = traceback.format_exc()
        status_code = getattr(error, 'status_code', 500)
        response_dict = dict(getattr(error, 'payload', None) or ())
        response_dict['message'] = getattr(error, 'message', None)
        response_dict['traceback'] = trace

        response = jsonify(response_dict)
        response.status_code = status_code
        print('error response..')
        print(response)
        traceback.print_exc(file=sys.stdout)
        return response

    @app.errorhandler(Exception)
    def _(error):
        print('here in base exception')
        trace = traceback.format_exc()
        status_code = getattr(error, 'status_code', 400)
        response_dict = dict(getattr(error, 'payload', None) or ())
        response_dict['message'] = getattr(error, 'message', None)
        response_dict['traceback'] = trace

        response = jsonify(response_dict)
        response.status_code = status_code
        print('error response..')
        print(response)
        traceback.print_exc(file=sys.stdout)
        return response

    app.run(host=flask_ip, port=flask_port)


if __name__ == "__main__":

    main()
