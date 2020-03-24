"""
    Module for 'price' intent

"""

from flask import make_response, jsonify


def price_intent_handler(req, public_url):

    returnText = ['This is price intent with query:']
    item = req["queryResult"]["parameters"].get("ent_whatis_query", None)
    if item is None or item == "":
        print('Warning: Intent is detected but failed to extract entity')
        followupEvent = {"name": "WELCOME", "parameters": {"num_fail": 1}}
        return make_response(jsonify({"followupEventInput": followupEvent}))

    query = item.strip().lower()

    return make_response(jsonify({
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [returnText + query]
                }
            }
        ]
    }))
