"""
    Module for 'what is' intent

"""

import csv
import random
from os import chdir
from os.path import dirname, realpath
from flask import make_response, jsonify

import spacy
nlp = spacy.load('en_core_web_md')

# **********************
# UTIL FUNCTIONS : END
# **********************
global WHATIS_DIC
WHATIS_DIC = {}
WHATIS_SOURCE = './data/glossary.csv'


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


def get_value_based_on_similar_key(glossary, query, threshold=0.6, verbose=0):
    """Retrieve top similar key for the query using
    word vector/embeddings similarity for the word vectors model.

        Returns: key of the top result if similarity > threshold, else None
    """
    query_nlp = nlp(query)
    keys_nlp = [nlp(k) for k in list(glossary.keys())]
    similarity_nlp = [(k, query_nlp.similarity(k)) for k in keys_nlp]
    results = sorted(similarity_nlp, key=lambda x: x[1], reverse=True)

    if verbose > 1:
        print(results[0:5])

    if results[0][1] > threshold:
        return results[0][0].text
    else:
        return None


def whatis_intent_handler(req, public_url):
    returnText = []
    item = req["queryResult"]["parameters"].get("ent_whatis_query", None)
    query = item.strip().lower()

    # lazy initialisation of WHATIS_DIC from a file.
    # alternatively we can query a DB
    if (not bool(WHATIS_DIC)): initialise_lookup_table()

    # Try to get description from WHATIS_DIC based on exact match
    dic_val = WHATIS_DIC.get(query, None)

    # Try NLP methods to get a match
    if (dic_val is None or dic_val[0] is None):

        # Perform word similarity with keys
        sim_key = get_value_based_on_similar_key(WHATIS_DIC, query)

        if (sim_key is not None):
            dic_val = WHATIS_DIC.get(sim_key, None)

            arr1 = [
                "😁 Well, there was no exact match for %s, but here's what I can tell you:" % item,
                "😊 Okay, I am not exactly sure what %s is, but I do know what %s is:" % (item, sim_key),
                "Oops, the closest match for your query is %s. And here's what it is:"
            ]
            returnText = random.choice(arr1) + "\n" + dic_val[0] + "\n\n(Source: " + dic_val[1] + ")"

        else:
            # TODO - search on Google/Wiki for what that is
            # Say dunno
            dunnoArray = [
                "Hmm.. I am not sure what " + item + " is too!",
                "Oops! I don't know what " + item + " is too!"
            ]
            returnText = random.choice(dunnoArray)
    else:
        description = dic_val[0]
        returnText = "*" + item.strip().capitalize() + "*:"
        returnText = returnText + "\n" + description

    return make_response(jsonify({
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [returnText]
                }
            }
        ]
    }))
