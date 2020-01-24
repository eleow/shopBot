"""
    Module for 'what is' intent

"""

import csv
import random
from os import chdir
from os.path import dirname, realpath
from flask import make_response, jsonify

# **********************
# UTIL FUNCTIONS : END
# **********************
global WHATIS_DIC
WHATIS_DIC = {}

WHATIS_SOURCE = 'whatIs.csv'

def initialise_lookup_table():
    """Initialise lookup table for "What is" queries
    """
    global WHATIS_DIC

    dir_path = dirname(realpath(__file__))
    chdir(dir_path)

    with open(WHATIS_SOURCE, mode='r', encoding="utf-8-sig") as infile:
        reader = csv.reader(infile)
        for row in reader:
            WHATIS_DIC[row[0].strip().lower()] = row[1]


def whatis_intent_handler(req, public_url):
    returnText = []
    item = req["queryResult"]["parameters"].get("item", None)

    # lazy initialisation of WHATIS_DIC from a file.
    # alternatively we can query a DB
    if (not bool(WHATIS_DIC)): initialise_lookup_table()

    # get description from WHATIS_DIC
    description = WHATIS_DIC.get(item.strip().lower(), None)
    if (description == None):
        # TODO - search on Google/Wiki for what that is
        #

        # Say dunno
        dunnoArray = [
            "Hmm.. I am not sure what " + item + " is too!",
            "Oops! I don't know what " + item + " is too!"
        ]
        returnText = [random.choice(dunnoArray)]
    else:
        returnText = "*" + item.strip().capitalize() +"*:"
        returnText = returnText + "\n" + description

    return make_response(jsonify({
            "fulfillmentMessages": [
                {
                    "text" : {
                        "text": returnText
                    }
                }
            ]
        }))





