"""
    Module for 'price' intent

"""
import os
import pickle
import random
from flask import make_response, jsonify
from rasa_helper import get_value_based_on_similar_key
from richMessageHelper import display_response

file_path = os.path.dirname(__file__)
brand_model_src = os.path.join(file_path, 'data/p_brand_model_info.pickle')
model_brand_src = os.path.join(file_path, 'data/p_model_brand.pickle')
with open(brand_model_src, 'rb+') as f:
    brand_model_info_dict = pickle.load(f)
with open(model_brand_src, 'rb+') as f:
    model_brand_dict = pickle.load(f)


def price_intent_get_model_handler(req, public_url, platform=""):

    ent_model = req['queryResult']['parameters'].get('ent_model', "")
    ent_brand = req['queryResult']['parameters'].get('ent_brand', "")
    suggest = None

    if (ent_model == ""):
        if (ent_brand != ""):
            # user has already specific a brand
            msg = random.choice([
                f"Okay, {ent_brand.upper()} headphones. Which models?",
                f"Sure, let's narrow down to {ent_brand.upper()} headphones. Which models are you interested in?",
                f"Got it. {ent_brand.upper()} headphones. Model?"
            ])

            if ent_brand in brand_model_info_dict.keys():
                possible_models = brand_model_info_dict[ent_brand].keys()

                # be helpful and list out available models if less than 5
                if len(possible_models) < 5:
                    suggest = [m.upper() for m in possible_models]  # suggestion chips
                    sim_msg = msg + ", ".join(possible_models)
                else:
                    sim_msg = msg
            # msg = msg + "\n" + list_brands

        else:
            msg = random.choice([
                "Ok let's get the price for your desired headphones. I will need the model name!",
                "Sure let's get more information for your desired headphones. What's the model name?",
                "Oops, I didn't quite catch the model name",
            ])
            sim_msg = msg
        return make_response(jsonify(display_response(public_url, msg, sim_msg, platform=platform, suggestions=suggest)))
    else:
        followupEvent = {
            "name": "intent_price_query_event",
            "parameters": {"ent_model": ent_model, "ent_brand": ent_brand}}
        return make_response(jsonify({"followupEventInput": followupEvent}))


def price_intent_get_brand_handler(req, public_url, platform=""):

    ent_brand = req['queryResult']['parameters'].get('ent_brand', "")
    ent_model = req["queryResult"]["parameters"].get("ent_model", "")
    # possible_brands = req["queryResult"]["parameters"].get("possible_brands", "") # in output context
    suggest = None

    for oc in req["queryResult"]['outputContexts']:
        if ("possible_brands" in oc.get('parameters', {})):
            possible_brands = oc['parameters']["possible_brands"]
            break

    if (ent_brand == ""):
        msg = random.choice([
            f"There are {len(possible_brands)} brands selling \"{ent_model.upper()}\"! 😲",
            f"😅 Oops! {len(possible_brands)} brands have this specific model \"{ent_model.upper()}\"!",
            f"Seems like \"{ent_model.upper()}\" is a popular model name! {len(possible_brands)} brands have this model."
        ])

        if len(possible_brands) < 5:
            list_brands = random.choice([
                "These are the possible brands: ",
                "Which of these brands are you looking at: "
            ])
            msg = msg + "\n" + list_brands
            sim_msg = msg + ", ".join(possible_brands)
            suggest = [b.upper() for b in possible_brands]  # suggestion chips
        else:
            sim_msg = msg
        # return make_response(jsonify({"fulfillmentMessages": [{"text": {"text": [msg]}}]}))
        return make_response(jsonify(display_response(public_url, msg, sim_msg, suggestions=suggest, platform=platform)))

    else:
        followupEvent = {
            "name": "intent_price_query_event",
            "parameters": {"ent_model": ent_model, "ent_brand": ent_brand}}
        return make_response(jsonify({"followupEventInput": followupEvent}))


def price_intent_handler(req, public_url, platform=""):

    intent_name = req["queryResult"]["intent"]["displayName"].lower()  # get intent in lower characters
    if (intent_name == 'intent_price_get_brand'): return price_intent_get_brand_handler(req, public_url, platform)
    if (intent_name == 'intent_price_get_model'): return price_intent_get_model_handler(req, public_url, platform)

    msg = ""
    simple_msg = ""
    basic_card = None

    model = req["queryResult"]["parameters"].get("ent_model", "")
    brand = req["queryResult"]["parameters"].get("ent_brand", "")

    if model == "":
        followupEvent = {"name": "intent_price_get_model_event", "parameters": {"ent_brand": brand}}
        return make_response(jsonify({"followupEventInput": followupEvent}))

    else:
        # check if there is an exact match for model
        if model not in model_brand_dict.keys():
            sim_model = get_value_based_on_similar_key(model_brand_dict, model)

            if sim_model is None:
                msg = "Oops, I could not find that specific model. Anything else you have in mind?"
                return make_response(jsonify({"fulfillmentMessages": [{"text": {"text": [msg]}}]}))
            else:
                print('Model:', model, 'Closest Model:', sim_model)
                model = sim_model

        # check brand
        if (brand == "" or brand not in brand_model_info_dict.keys()):
            # brand was either not specified or specified but not valid,
            # but model is valid - we will be able to get a brand for it
            possible_brands = model_brand_dict.get(model, "")
            if len(possible_brands) > 1:
                # need to ask for brand
                followupEvent = {
                    "name": "intent_price_get_brand_event",
                    "parameters": {
                        "ent_model": model,
                        "possible_brands": possible_brands
                    }
                }
                return make_response(jsonify({"followupEventInput": followupEvent}))

            else:
                brand = possible_brands[0]  # one-to-one matching! Great!

        # finally, let's get details for the given brand and model
        info = brand_model_info_dict.get(brand).get(model, {})
        if (info != {}):
            msg = random.choice([
               f"🎉 You can get {brand.upper()} {model.upper()} at S${info['Product Price']:,.2f}!",
               f"Woohoo! It's your lucky day! 🤩 {brand.upper()} {model.upper()} is available at S${info['Product Price']:,.2f}!"
            ])

            simple_msg = msg + f"\n🎁 Get it now at {info['Product URL']}"
            # print(simple_msg)

            # format into a card for display as a rich message if available
            basic_card = {
                "title": "Available at Treoo" if 'treoo' in info['Product URL'] else "Available at Amazon SG",
                "image": info.get("Product Image URL", ""),  # may or may not have an image
                "accessibilityText": f"{brand.upper()} {model.upper()}",
                "buttons": [
                    {
                        "title": "🎁 Get it now",
                        "url": info["Product URL"]
                    }
                ]
            }
            pdf = info.get("ProductFeatures", "")
            if type(pdf) == str and pdf != "": basic_card["formattedText"] = "Features: " + pdf.replace(",", ", ")
        else:
            # some mismatch between brand and model (maybe wrong entity got recognised)
            if model not in model_brand_dict.keys():
                req["queryResult"]["parameters"]["ent_model"] = ""

            if brand not in brand_model_info_dict.keys():
                req["queryResult"]["parameters"]["ent_brand"] = ""

            # reset both and hope user rephrases
            if model in model_brand_dict and brand in brand_model_info_dict.keys():
                req["queryResult"]["parameters"]["ent_model"] = ""
                req["queryResult"]["parameters"]["ent_brand"] = ""

            # recursive call - get brand/model again if required
            return price_intent_handler(req, public_url, platform)

    res = display_response(public_url, msg, simple_msg, basic_card=basic_card, platform=platform)
    res['outputContexts'] = []  # reset contexts, as intent has ended

    return make_response(jsonify(res))
