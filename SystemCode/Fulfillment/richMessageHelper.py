# import urllib.parse as urllib
# import os
import random
# import requests
# import configparser

BOT_NAME = 'AudioPhil'
BOT_TYPE = 'shopping bot'
BOT_DOMAIN = 'earphones and headphones'
# CONFIG_PATH = './SystemCode/Fulfillment/config.ini'
# PAGE_ACCESS_TOKEN = 'EAAgHkQdJywIBAF01w2xrZCd2dmTct1QQqZAqbVDol5dwqrS57yt60fbhOnXpxZB8HH8ZBiVJwUfw99nz5WHtayinBA9INfsldC00OR628rUZBUNDBGVKp4lMeXpjsQscNVUbEkThgsyRNHr9gNfkhBpZBIzawycGSI1w34sRLdWgZDZD'

# if os.path.isfile(CONFIG_PATH):
#     # Get values in config file
#     config = configparser.ConfigParser()
#     config.read(CONFIG_PATH)
#     PAGE_ACCESS_TOKEN = config['MESSENGER']['PAGE_ACCESS_TOKEN']


# def getUserName(intentRequest):

#     if intentRequest['payload'] == {}:
#         return None

#     if intentRequest['source'] == 'facebook':
#         sender_id = intentRequest['payload']['data']['sender']['id']

#         # send POST call to Facebook Graph API to get user's name
#         user_details_url = "https://graph.facebook.com/v2.6/%s" % sender_id
#         user_details_params = {'fields': 'first_name,last_name,profile_pic', 'access_token': PAGE_ACCESS_TOKEN}
#         user_details = requests.get(user_details_url, user_details_params).json()
#         first_name = user_details['first_name']
#         # print(user_details['first_name'])
#         return first_name

#     return None


def displayWelcomeBase(default_header_msg=None, additional_header=None, first_name=None):
    # Components of introduction message
    greet = random.choice(["Hi", "Hello there", "Good day", "Hey", "How's it going"])
    emoji = random.choice(["😁", "😊", "😎", "😀", "😬"])

    if first_name is not None: greet = greet + " " + first_name

    introArr = [
        f"! I am {BOT_NAME}, your personal {BOT_TYPE} for {BOT_DOMAIN}! {emoji} ",
        f"! I am {BOT_NAME}, the {BOT_TYPE} for {BOT_DOMAIN} {emoji} ",
        f"! 👋 {BOT_NAME} here. How can I help you today? 😊 ",
        f"! {emoji} I'm {BOT_NAME}, the {BOT_TYPE} for {BOT_DOMAIN}. What would you like to do today?"
    ]
    intro = greet + random.choice(introArr) if not additional_header else additional_header

    intro2 = "  🎧 Find headphones that match your preferences\n" \
             "  💰 Get the price and buying information for a specific headphone model\n" \
             "  📰 Learn more about headphone/earphone terminology"

    # body2 = "" # body2 = "Or just click one of the buttons below:"

    header_msg1 = intro + "\n\nHere's a couple of the things you can do:\n" + intro2

    # remove mrkdown characters
    if (default_header_msg is None): default_header_msg = ''.join([c for c in header_msg1 if c not in ['•', '_', '*']])

    return default_header_msg


# https://dialogflow.com/docs/reference/v1-v2-migration-guide-fulfillment#webhook_responses
def display_google_assistant(public_url, msg, basic_card, suggestions):
    res = {
        "expectUserResponse": True,
        "richResponse": {
            "items": [
                {
                    "simpleResponse": {
                        "displayText": msg,
                        "platform": "google",
                        "textToSpeech": msg.encode('ascii', 'ignore').decode('ascii')
                    }
                }
            ]
        }
    }

    if basic_card is not None:
        res_basic_card = {
            "basicCard": {
                "title": basic_card.get('title', ""),
                "subtitle": basic_card.get('subtitle', ""),
                "formattedText": basic_card.get('formattedText', ""),
                "image": {
                    "url": basic_card.get('image', ""),
                    "accessibilityText": basic_card.get('accessibilityText', "")
                },
            }
        }

        # if basic_card.get('image', None) is not None:
        # if True:
        #     res_basic_card["basicCard"]["image"] = {
        #         "url": basic_card.get('image', ""),
        #         "accessibilityText": basic_card.get('accessibilityText', "")
        #     }
        #     res_basic_card["basicCard"]["imageDisplayOptions"] = "DEFAULT"

        if 'buttons' in basic_card:
            res_basic_card["basicCard"]["buttons"] = []
            for but in basic_card.get('buttons'):
                res_basic_card["basicCard"]["buttons"].append({
                    "title": but['title'],
                    "openUrlAction": {
                        "url": but['url']
                    }
                })

        res['richResponse']["items"].append(res_basic_card)

    if suggestions is not None and len(suggestions) > 0:
        res_suggestions = []
        for s in suggestions:
            res_suggestions.append({"title": s})

        res['richResponse']["suggestions"] = res_suggestions

    return res


def display_response(public_url, msg, sim_msg=None, basic_card=None, suggestions=None, platform=""):
    if sim_msg is None: sim_msg = msg

    google_payload = display_google_assistant(public_url, msg, basic_card, suggestions)

    webhook_response = {
        # "fulfillmentMessages": [{"text": {"text": [sim_msg]}}],  # bug-fix: so that kommunicate will not display both
        "payload": {
            "google": google_payload,
        },
        "fulfillmentMessages": []
    }

    if platform == "": webhook_response['fulfillmentMessages'] = [{"text": {"text": [sim_msg]}}]
    return webhook_response


def displayWelcome(public_url, default_header_msg=None, additional_header=None, first_name=None, platform=""):
    default_header_msg = displayWelcomeBase(default_header_msg, additional_header, first_name)
    return display_response(public_url, default_header_msg, platform=platform)
