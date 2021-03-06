import logging
import os

from flask import Flask, request
from flask_cors import CORS
from flasgger import Swagger

from common.configure.config import load_config
from api.controllers import rule_engine_controller


# print a nice greeting.
def say_hello(username="World"):
    return '<p>Hello %s!</p>\n' % username


header_text = '''
    <html>\n<head> <title>Simple Serverless Rule Engine</title> </head>\n<body>'''

instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

__logger = logging.getLogger(__name__)

__logger.info("Loading environment........")
env_name = os.environ.get('env')

if not env_name:
    env_name = 'sandbox'

load_config(env_name)

application = Flask(__name__)
Swagger(application)

application.debug = False

# add a rule for the index page.
application.add_url_rule(
    '/',
    'index',
    (
        lambda: header_text + say_hello() + instructions + footer_text
    )
)

# add a rule when the page is accessed with a name appended to the site
# URL.
application.add_url_rule(
    '/<username>',
    'hello',
    (
        lambda username: header_text + say_hello(username) + home_link + footer_text
    )
)


@application.route('/api_rules_engine/v1/rules/<rule_name>/execute', methods=['POST'])
def execute_rule_post(rule_name):
    """
    Use this endpoint to execute the rule engine for a rule for a fact set.
    ---
    tags:
        - Execute Rule Engine
    parameters:
        - name: rule_name
          in: path
          type: string
          required: true
          description: Rule name
        - name: facts
          in: body
          type: string
          required: true
          description: Facts JSON. The root node must be facts
    responses:
        200:
            description: Rule result
    """
    body = request.get_json()
    return rule_engine_controller.execute_rule_engine(rule_name, body)


@application.route('/api_rules_engine/v1/rules/<rule_name>', methods=['GET'])
def get_rule_get(rule_name):
    return rule_engine_controller.get_rule(rule_name)


@application.route('/api_rules_engine/v1/rules', methods=['GET'])
def get_all_rules_get():
    return rule_engine_controller.get_all_rules()


CORS(application)

if __name__ == "__main__":
    application.run(host='0.0.0.0')
