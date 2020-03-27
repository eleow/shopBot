"""
    Main file for fulfillment backend for dialogFlow
    Each intent will be in separate files
"""

# import requests
# import json
# from lxml import html

# import builtins as exceptions
# from time import sleep
# import re,urllib.parse as urllib
# import argparse

import os
import argparse
import random
from flask import render_template
from flask import Flask, request, make_response, jsonify
from intent_whatis import whatis_intent_handler
from intent_price import price_intent_handler
from richMessageHelper import displayWelcome
from rasa_helper import perform_intent_entity_recog_with_rasa
from utils import crossdomain, str2bool  # , get_memory_size_locals
from colorama import Fore, Style
# import flask_profiler

# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--ngrok", type=str2bool, default=False, help='Bool indicating whether to automatically launch ngrok')
parser.add_argument("-s", "--server", type=str2bool, default=False, help='Bool indicating whether running on heroku server')
parser.add_argument("-r", "--rasa", type=str2bool, default=True,
    help='Bool indicating whether to enable RASA NLU server. If running locally, ensure that you launch RASA server on your own')
parser.add_argument("-t", "--threshold", type=float, default=0.7, help='RASA threshold to pass RASA intent classification. Range 0-1')
parser.add_argument("-d", "--debug", type=str2bool, default=False, help='Flask debug mode')
# args = vars(parser.parse_args())
args, unknown = parser.parse_known_args()
args = vars(args)
RUN_NGROK = args['ngrok']
RUN_ON_SERVER = args['server']
USE_RASA = args['rasa']
RASA_CONFIDENCE_THRESHOLD = args['threshold']
DEBUG = args['debug']

PUBLIC_URL = ""
RASA_URL = ""

print("--------------------------------------------------------------------")
if RUN_ON_SERVER:
    # running on server, no need to run ngrok
    PUBLIC_URL = "https://shopbotsg.herokuapp.com/"  # ShopBot main logic
    RASA_URL = "http://testshop1606.herokuapp.com"   # Rasa NLU server (app will be either rename or hopefully combined into shopbot)
    print(" Flask is executed from Heroku")
else:
    # running locally. We can either automatically run ngrok or not
    # The disadvantage of running ngrok automatically is that
    # any restarting of flask will require ngrok to be restarted & therefore reconfiguration on dialogflow fulfillment page
    if RUN_NGROK:
        from pyngrok import ngrok
        from os.path import dirname, join, realpath

        dir_path = dirname(realpath(__file__))
        ngrok.DEFAULT_CONFIG_PATH = join(dir_path, "ngrok.yml")
        # ngrok.DEFAULT_NGROK_PATH = join(dir_path, "ngrok.exe")
        # tunnels = ngrok.get_tunnels(ngrok_path=join(dir_path, "ngrok.exe"))
        tunnels = ngrok.get_tunnels()
        if (len(tunnels) == 0):
            PUBLIC_URL = ngrok.connect(port=5000, proto="http")
        else:
            PUBLIC_URL = tunnels[0].public_url

        print(" Flask is executed locally and ngrok will be started automatically")
    else:
        print(Fore.RED + " Flask is executed locally")
        print(" Run ngrok manually to get a public URL for DialogFlow fulfillment webhook and enter below:"
              + Style.RESET_ALL)
        PUBLIC_URL = input().strip()
        print()
    #
    if USE_RASA:
        RASA_URL = "http://localhost:5015"
        print(" RASA will be used for Intent classification and entity detection")
        print(Fore.RED + " RASA server should be started manually and point to localhost:5015")
        print(" In the root directory, use command: make rasa_run" + Style.RESET_ALL)
    else:
        print(" DialogFlow will be used for Intent classification and entity detection")


print("--------------------------------------------------------------------")
print(Fore.GREEN)
print(" * PUBLIC URL: " + PUBLIC_URL)
print(" * RASA URL: " + RASA_URL)
print(Style.RESET_ALL)
app = Flask(__name__)
# app.config["DEBUG"] = True
# app.config["flask_profiler"] = {
#     "enabled": app.config["DEBUG"],
#     "storage": {
#         "engine": "sqlite"
#     },
#     "basicAuth": {
#         "enabled": True,
#         "username": "admin",
#         "password": "admin"
#     },
#     "ignore": [
#         "^/static/.*"
#     ]
# }

# *****************************
# WEBHOOK MAIN ENDPOINT : START
# *****************************
@app.route('/', methods=['POST', 'GET'])
@crossdomain(origin='*')
def webhook():
    if (request.method == 'GET'):
        message1 = "Flask Webhook is running @ " + PUBLIC_URL
        message2 = "RASA server is hosted @ " + RASA_URL
        return render_template('index.html', message1=message1, message2=message2, img="/static/logo.png")

    elif (request.method == 'POST'):
        req = request.get_json(silent=True, force=True, cache=False)
        intent_name = req["queryResult"]["intent"]["displayName"].lower()  # get intent in lower characters
        action = req["queryResult"].get("action", None)
        # print(intent_name)

        # check for kommunicate web client
        intentRequest = req['originalDetectIntentRequest']

        platform = ""
        if (intentRequest.get('payload', None) is not None and intentRequest['payload'].get('kommunicate', None) is not None):
            platform = "kommunicate"

        # Intent for query of terms
        if (intent_name == "intent_whatis_query"):
            return whatis_intent_handler(req, PUBLIC_URL, platform)
        elif (intent_name == "intent_price_query"):
            return price_intent_handler(req, PUBLIC_URL, platform)

        elif action in ["WELCOME"] or "default welcome intent" in intent_name:

            # # Try to get first name of user from platform's API
            # intentRequest = req['originalDetectIntentRequest']
            # first_name = getUserName(intentRequest)
            first_name = None

            # wasRedirected = (req["queryResult"].get("outputContexts") is not None and any(
            #     "welcome" in d["name"] for d in req["queryResult"].get("outputContexts")))
            num_fail = req["queryResult"]["outputContexts"][0].get('parameters', {}).get("num_fail", None)
            wasRedirected = num_fail is not None and num_fail > 0
            # print('num failed', num_fail)

            dontUnderstand = [
                "I don't really understand that. Could you say that again?",
                "Erm.. I didn't catch that.",
                "Sorry, could you rephrase that?"
            ]
            returnDontUnderstand = random.choice(dontUnderstand)

            additional_header = None if not wasRedirected else returnDontUnderstand
            return make_response(jsonify(displayWelcome(PUBLIC_URL, additional_header=additional_header, first_name=first_name, platform=platform)))
            # return make_response(jsonify(displayWelcome_slack(PUBLIC_URL,
            #     additional_header=additional_header, first_name=first_name)))

        else:

            if USE_RASA:
                # print(req["queryResult"])
                queryText = req["queryResult"]["queryText"]
                rasa = perform_intent_entity_recog_with_rasa(queryText, RASA_URL)
                dialogflow_intent_name = rasa['intent_name']

                if rasa is not None:
                    if (rasa["confidence"] > RASA_CONFIDENCE_THRESHOLD):
                        # redirect intent
                        eventName = dialogflow_intent_name + "_event"
                        followupEvent = {
                            "name": eventName,
                            "parameters": {
                                "rasa": {
                                    "intent_name": rasa['rasa_intent_name'],
                                    "intent_confidence": rasa['confidence'],
                                    "entities": rasa['rasa_entities']
                                }
                            }
                        }
                        for r in rasa['entities']:
                            if r[0] is not None: followupEvent["parameters"][r[0]] = r[1]

                        return make_response(jsonify({"followupEventInput": followupEvent}))

            # If not using RASA or if rasa confidence < RASA_CONFIDENCE_THRESHOLD
            followupEvent = {"name": "WELCOME", "parameters": {"num_fail": 1}}
            return make_response(jsonify({"followupEventInput": followupEvent}))


@app.route('/privacypolicy', methods=['POST', 'GET'])
def privacy():
    return render_template('privacypolicy.html', img="/static/logo.png")


@app.route('/shopbot', methods=['POST', 'GET'])
def home():
    return render_template('shopbot.html', img="/static/logo.png")


# flask_profiler.init_app(app)

# ***************************
# WEBHOOK MAIN ENDPOINT : END
# ***************************
# from pml import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=DEBUG, host='0.0.0.0', port=port)
