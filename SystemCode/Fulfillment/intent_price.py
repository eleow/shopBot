"""
    Module for 'price' intent

"""
import os
import pickle
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


def price_intent_handler(req, public_url, platform=""):

    msg = ""
    simple_msg = ""
    basic_card = None

    model = req["queryResult"]["parameters"].get("ent_model", "")
    brand = req["queryResult"]["parameters"].get("ent_brand", "")

    if model == "":
        msg = "Ok let's get the price for your desired headphones. I will need the model name!"
    else:
        # check if there is an exact match for model
        if model not in model_brand_dict.keys():
            sim_model = get_value_based_on_similar_key(model_brand_dict, model)

            if sim_model is None:
                msg = "Oops, I could find that specific model. Anything else you have in mind?"
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
                msg = "There are multiple brands selling this model! What brand would this be for?"
                if len(possible_brands) < 5:
                    msg = msg + "\nThese are the possible brands: " + ", ".join(possible_brands)
                    return make_response(jsonify({"fulfillmentMessages": [{"text": {"text": [msg]}}]}))
            else:
                brand = possible_brands[0]  # one-to-one matching! Great!

        # finally, let's get details for the given brand and model
        info = brand_model_info_dict.get(brand).get(model)
        msg = f"You can get {brand.upper()} {model.upper()} at S${info['Product Price']:,.2f}!"
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

    return make_response(jsonify(display_response(public_url, msg, simple_msg, basic_card=basic_card, platform=platform)))
