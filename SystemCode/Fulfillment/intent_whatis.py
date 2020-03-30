"""
    Module for 'what is' intent

"""

import csv
import random
import string
from os import chdir
from os.path import dirname, realpath
from flask import make_response, jsonify
from rasa_helper import get_value_based_on_similar_key
from richMessageHelper import display_response

# import spacy
# # nlp = None  # spacy.load('en_core_web_md')
# nlp = spacy.load('en_core_web_md')

# **********************
# UTIL FUNCTIONS : END
# **********************
global WHATIS_DIC
WHATIS_DIC = {}
WHATIS_SOURCE = './data/glossary_cleaned.csv'


def initialise_lookup_table():
    """Initialise lookup table for "What is" queries
    """
    global WHATIS_DIC

    dir_path = dirname(realpath(__file__))
    chdir(dir_path)
    print(dir_path)

    with open(WHATIS_SOURCE, mode='r', encoding="utf-8-sig") as infile:
        reader = csv.reader(infile)
        for row in reader:
            WHATIS_DIC[row[0].strip().lower()] = (row[1], row[2])  # tuple of description, source

            # Expand synonyms / Copy description and source
            if (row[3] != ''):
                synonyms = row[3].split(',')
                for s in synonyms:
                    WHATIS_DIC[s.strip().lower()] = (row[1], row[2])


def whatis_intent_handler(req, public_url, platform=""):
    # global nlp

    returnText = ""
    returnText_simple = ""
    postText = []

    item = req["queryResult"]["parameters"].get("ent_whatis_query", None)
    item = ''.join([t for t in item if t not in string.punctuation]).lower()

    if item is None or item == "":
        print('Warning: Intent is detected but failed to extract entity')
        followupEvent = {"name": "WELCOME", "parameters": {"num_fail": 1}}
        return make_response(jsonify({"followupEventInput": followupEvent}))

    query = item.strip().lower()
    item = item.strip().upper()

    # lazy initialisation of WHATIS_DIC from a file.
    # alternatively we can query a DB
    if (not bool(WHATIS_DIC)): initialise_lookup_table()
    # if (nlp is None):
    #     if 'heroku' in public_url: nlp = spacy.load('en_core_web_sm')  # quickfix, due to R14 memory error in Heroku (similarity results will NOT be good!)
    #     else: nlp = spacy.load('en_core_web_md')

    # Try to get description from WHATIS_DIC based on exact match
    dic_val = WHATIS_DIC.get(query, None)

    # Try NLP methods to get a match
    if (dic_val is None or dic_val[0] is None):

        # Perform word similarity with keys
        sim_key = get_value_based_on_similar_key(WHATIS_DIC, query)

        if (sim_key is not None):
            dic_val = WHATIS_DIC.get(sim_key, None)

            starter = random.choice([
                f"😁 Well, there was no exact match for {item}, but here's what I can tell you for {sim_key.upper()}:",
                f"😊 Okay, I am not exactly sure what {item} is, but I do know what {sim_key.upper()} is:",
                f"Oops, the closest match for your query is {sim_key.upper()}. And here's what it is:"
            ])
            # returnText = random.choice(arr1) + "\n" + dic_val[0] + "\n\n(Source: " + dic_val[1] + ")"
            returnText_simple = starter + "\n" + dic_val[0] + "\n\n(Source: " + dic_val[1] + ")"
            returnText = starter
            postText = [dic_val[0], "source: " + dic_val[1]]

        else:
            # Say dunno
            dunnoArray = [
                "Hmm.. I am not sure what " + item + " is too!",
                "Oops! I don't know what " + item + " is too!"
            ]
            returnText = random.choice(dunnoArray)
            returnText_simple = returnText
    else:
        description = dic_val[0]
        returnText_simple = item + ":\n" + description + "\n(From: " + dic_val[1] + ")"

        returnText = "Here's what I've got for " + item
        postText = [description, "source: " + dic_val[1]]

    return make_response(jsonify(display_response(public_url,
        sim_msg=returnText_simple, msg=returnText, post_msg=postText, platform=platform)))
