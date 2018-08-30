import os
import json

from flask import Flask, Response

from opencensus.trace import config_integration
from opencensus.trace import tracer as tracer_module
from opencensus.trace.exporters import jaeger_exporter
from opencensus.trace.ext.flask.flask_middleware import FlaskMiddleware

import mysql.connector
from mysql.connector import errorcode

config = {
  'user': os.environ.get('MYSQL_DB_USER'),
  'password': os.environ.get('MYSQL_DB_PASSWORD'),
  'host': os.environ.get('MYSQL_DB_HOST'),
  'database': 'test'
}


app = Flask(__name__)

exporter = jaeger_exporter.JaegerExporter(
  service_name='ratings',
  agent_host_name='jaeger-agent.istio-system',
  agent_port=6831,
)

middleware = FlaskMiddleware(app, exporter=exporter)
config_integration.trace_integrations(['mysql'])

@app.route("/ratings/<id>")
def ratings(id=None):
    conn = cur = None
    result = {}

    try:
        conn = mysql.connector.connect(**config)
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
