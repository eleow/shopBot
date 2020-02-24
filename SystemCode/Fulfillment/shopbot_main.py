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
from flask import render_template
import sys
import random
from flask import Flask, request, make_response, jsonify
from intent_whatis import whatis_intent_handler
from richMessageHelper import displayWelcome_slack
from rasa_helper import perform_intent_entity_recog_with_rasa

USE_RASA = True
RASA_CONFIDENCE_THRESHOLD = 0.7

global RUN_NGROK
RUN_NGROK = False
if len(sys.argv) == 2:
    RUN_NGROK = False if sys.argv[1] != '1' else True


# import colorama
# colorama.init()

# For running ngok directly from python
PUBLIC_URL = ""
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
    print("--------------------------------------------------------------------")
    print(" Flask will be run from ngrok")
    print("--------------------------------------------------------------------")
else:
    PUBLIC_URL = "https://shopbotsg.herokuapp.com/"  # Use heroku url
    print("--------------------------------------------------------------------")
    print(" Flask will be run from Heroku / Ngrok will be run separately")
    print("--------------------------------------------------------------------")

print(" * PUBLIC URL: " + PUBLIC_URL)
app = Flask(__name__)


# def perform_intent_entity_recog_with_rasa(payload):
#     rasa_server_url = "http://localhost:5005/model/parse"
#     headers = {
#         "Accept": "application/json",
#         "Content-Type": "application/json"
#     }

#     try:
#         # send POST call to RASA to perform intent classification and entity recognition
#         # https://rasa.com/docs/rasa/api/http-api/
#         response = requests.post(url=rasa_server_url, headers=headers, json={"text": payload})
#         print("----------------------RASA!!!! _------------")
#         print(dumps(response.json()))

#         return response.json()

#     except HTTPError as http_err:
#         print(f'Ensure that RASA server is running. {http_err}')
#         return None

# *****************************
# WEBHOOK MAIN ENDPOINT : START
# *****************************
@app.route('/', methods=['POST', 'GET'])
def webhook():
    if (request.method == 'GET'):
        message = "Flask Webhook is running @ " + PUBLIC_URL
        return render_template('index.html', message=message, img="/static/logo.png")

    elif (request.method == 'POST'):

        req = request.get_json(silent=True, force=True, cache=False)
        intent_name = req["queryResult"]["intent"]["displayName"].lower()  # get intent in lower characters
        action = req["queryResult"].get("action", None)

        # Intent for query of terms
        if (intent_name == "intent_whatis_query"):
            return whatis_intent_handler(req, PUBLIC_URL)

        elif action in ["WELCOME"] or "Default Welcome Intent" in intent_name:
            # wasRedirected = (req["queryResult"].get("outputContexts") is not None and any(
            #     "welcome" in d["name"] for d in req["queryResult"].get("outputContexts")))
            num_fail = req["queryResult"]["parameters"].get("num_fail", None)
            wasRedirected = num_fail is not None and num_fail > 0
            print('num failed', num_fail)

            dontUnderstand = [
                "I don't really understand that. Could you say that again?",
                "Erm.. I didn't catch that."
                "Sorry, could you rephrase that?"
            ]
            returnDontUnderstand = random.choice(dontUnderstand)

            additional_header = None if not wasRedirected else returnDontUnderstand
            return make_response(jsonify(displayWelcome_slack(PUBLIC_URL, additional_header=additional_header)))

        else:

            if USE_RASA:
                # print(req["queryResult"])
                queryText = req["queryResult"]["queryText"]
                rasa = perform_intent_entity_recog_with_rasa(queryText)
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
            followupEvent = {"name": "WELCOME", "parameters": {"unknown": True, "num_fail": 1}}
            return make_response(jsonify({"followupEventInput": followupEvent}))


# ***************************
# WEBHOOK MAIN ENDPOINT : END
# ***************************
# from pml import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=True, host='0.0.0.0', port=port)
