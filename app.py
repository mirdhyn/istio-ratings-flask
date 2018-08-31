from os import getenv
import json
import logging

from flask import Flask, Response, request

from jaeger_client import Config
from flask_opentracing import FlaskTracer
from opentracing_instrumentation.client_hooks import install_all_patches

import mysql.connector
from mysql.connector import errorcode

mysql_config = {
  'user': getenv('MYSQL_DB_USER'),
  'password': getenv('MYSQL_DB_PASSWORD'),
  'host': getenv('MYSQL_DB_HOST'),
  'database': 'test'
}


app = Flask(__name__)
log_level = logging.DEBUG
logging.getLogger('').handlers = []
logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)

config = Config(config={'sampler': {'type': 'const', 'param': 1},
                        'logging': True,
                        'propagation': 'b3',
                        'local_agent':
                        # Also, provide a hostname of Jaeger instance to send traces to.
                        {'reporting_host': 'jaeger-agent.istio-system'}},
                # Service name can be arbitrary string describing this particular web service.
                service_name="ratings")
install_all_patches()
jaeger_tracer = config.initialize_tracer()
tracer = FlaskTracer(jaeger_tracer)

@app.route("/ratings/<id>")
@tracer.trace()
def ratings(id=None):
    parent_span = tracer.get_span(request)
    logging.debug("parent_span_start")
    logging.debug(parent_span)
    logging.debug("parent_span_end")
    with jaeger_tracer.start_span("python webserver internal span of ratings method",
                                                  child_of=parent_span) as span:
        conn = cur = None
        result = {}

        try:
            conn = mysql.connector.connect(**mysql_config)
        except mysql.connector.Error as err:
            print(err)
        else:
            cur = conn.cursor()
            cur.execute('SELECT Rating FROM ratings;')
            rows = cur.fetchall()

            result = {
              'id': id,
              'ratings': {
                'Reviewer1': rows[0][0],
                'Reviewer2': rows[1][0]
              }
            }
        finally:
            if cur:
                  cur.close()
            if conn:
                  conn.close()

        return Response(json.dumps(result), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, debug=True)
