import string
import re
import unidecode
# from json import dumps, loads
import requests
from requests.exceptions import HTTPError
import nltk
sb_stemmer = nltk.stem.snowball.SnowballStemmer("english", ignore_stopwords=True)

# Lookup table to convert RASA entity to DialogFlow entity
rasa_to_dialogFlow_entity = {
    "term": "ent_whatis_query",
    "model": "ent_price_query"
}

# Lookup table to convert RASA intents to DialogFlow intents
rasa_to_dialogFlow_intent = {
    "intent_whatis": "intent_whatis_query",
    "intent_price": "intent_price_query"
}

# Our users will be singaporeans - Remove singlish end-words
singlish_base = ['la', 'lo', 'le', 'ar']
singlish_stopwords = singlish_base.copy()
singlish_stopwords.extend([s + 'r' for s in singlish_base])
singlish_stopwords.extend([s + 'h' for s in singlish_base])
singlish_stopwords.extend(['eh', 'er', 'liao'])
singlish_list = '[.?!]?$|'.join(singlish_stopwords)  # for regex - match words at end of sentence

# Common synonyms that we can replace
synonyms_dict = {
    "b&o": "Bang & Olufsen"
}


def get_response_from_rasa(payload, rasa_base_url):
    # rasa_server_url = "http://localhost:5015/model/parse"
    # rasa_server_url = "https://testshop1606.herokuapp.com/model/parse"
    rasa_server_url = rasa_base_url + "/model/parse"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        # send POST call to RASA to perform intent classification and entity recognition
        # https://rasa.com/docs/rasa/api/http-api/
        response = requests.post(url=rasa_server_url, headers=headers, json={"text": payload})
        # print("----------------------RASA!!!! _------------")
        # print(dumps(response.json()))

        return response.json()

    except HTTPError as http_err:
        print(f'Ensure that RASA server is running. {http_err}')
        return None


def perform_intent_entity_recog_with_rasa(queryText, rasa_base_url):

    # convert any unicode string to closest ASCII (eg motörheadphönes --> motorheadphones)
    unaccentedText = unidecode.unidecode(u'' + queryText)

    # remove singlish stopwords at end of sentence
    queryText_no_singlish = re.sub(singlish_list, '', unaccentedText.lower().trim())

    # strip punctuation, convert to lower before passing to RASA-NLU server
    payload = ''.join([t for t in queryText_no_singlish if t not in string.punctuation]).lower()

    # perform stemming using snowball (this helps to make words singular)
    payload_stemmed = sb_stemmer.stem(payload)

    rasa_response = get_response_from_rasa(payload_stemmed, rasa_base_url)

    if (rasa_response is not None):
        rasa_intent_name = rasa_response['intent']["name"]
        rasa_intent_confidence = rasa_response['intent']['confidence']
        rasa_entities = [(e['entity'], e['value']) for e in rasa_response['entities']]

        # translate rasa to dialogflow
        dialogflow_entities = [(rasa_to_dialogFlow_entity.get(r[0], None), r[1]) for r in rasa_entities]
        dialogflow_intent_name = rasa_to_dialogFlow_intent.get(rasa_intent_name, rasa_intent_name)

        return {
            "rasa_intent_name": rasa_intent_name,
            "rasa_entities": rasa_entities,
            "confidence": rasa_intent_confidence,
            "intent_name": dialogflow_intent_name,
            "entities": dialogflow_entities
        }

    else:
        return None
