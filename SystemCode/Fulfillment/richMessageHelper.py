# import urllib.parse as urllib
import os
import random
import requests
import configparser

BOT_NAME = 'AudioPhil'
BOT_TYPE = 'shopping bot'
BOT_DOMAIN = 'earphones and headphones'
CONFIG_PATH = './SystemCode/Fulfillment/config.ini'
PAGE_ACCESS_TOKEN = 'EAAgHkQdJywIBAF01w2xrZCd2dmTct1QQqZAqbVDol5dwqrS57yt60fbhOnXpxZB8HH8ZBiVJwUfw99nz5WHtayinBA9INfsldC00OR628rUZBUNDBGVKp4lMeXpjsQscNVUbEkThgsyRNHr9gNfkhBpZBIzawycGSI1w34sRLdWgZDZD'

if os.path.isfile(CONFIG_PATH):
    # Get values in config file
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    PAGE_ACCESS_TOKEN = config['MESSENGER']['PAGE_ACCESS_TOKEN']


def getUserName(intentRequest):

    if intentRequest['payload'] == {}:
        return None

    if intentRequest['source'] == 'facebook':
        sender_id = intentRequest['payload']['data']['sender']['id']

        # send POST call to Facebook Graph API to get user's name
        user_details_url = "https://graph.facebook.com/v2.6/%s" % sender_id
        user_details_params = {'fields': 'first_name,last_name,profile_pic', 'access_token': PAGE_ACCESS_TOKEN}
        user_details = requests.get(user_details_url, user_details_params).json()
        first_name = user_details['first_name']
        # print(user_details['first_name'])
        return first_name

    return None


def displayWelcome_slack(public_url, default_header_msg=None, additional_header=None, first_name=None):
    fulfillmentMessage = []
    slackBlocks = []

    # Components of introduction message
    greetArr = ["Hi", "Hello there", "Good day", "Hey", "How's it going"]
    greet = random.choice(greetArr)

    if first_name is not None:
        greet = greet + " " + first_name

    # introArr = [
    #     "Hi! I am %s, your personal %s for %s! 👩 " % (BOT_NAME, BOT_TYPE, BOT_DOMAIN),
    #     "Hello there! I am %s, the %s for %s 😋 " % (BOT_NAME, BOT_TYPE, BOT_DOMAIN),
    #     "👋 %s here. How can I help you today? 😊 " % BOT_NAME,
    #     "Good day! 😁 I'm %s, the %s for %s. What would you like to do today?" % (BOT_NAME, BOT_TYPE, BOT_DOMAIN)
    # ]

    introArr = [
        "! I am %s, your personal %s for %s! 👩 " % (BOT_NAME, BOT_TYPE, BOT_DOMAIN),
        "! I am %s, the %s for %s 😋 " % (BOT_NAME, BOT_TYPE, BOT_DOMAIN),
        "! 👋 %s here. How can I help you today? 😊 " % BOT_NAME,
        "! 😁 I'm %s, the %s for %s. What would you like to do today?" % (BOT_NAME, BOT_TYPE, BOT_DOMAIN)
    ]
    intro = greet + random.choice(introArr) if not additional_header else additional_header

    intro2 = "• Find headphones that match your preferences\n• Learn more about headphone/earphone terminology "
    # body2 = "" # body2 = "Or just click one of the buttons below:"

    header_msg1 = intro + "\n\nHere's a couple of the things you can do:\n" + intro2
    # header_msg = header_msg1 + "\n\n" + body2

    # populate slackBlocks
    # TODO

    # remove mrkdown characters
    if (default_header_msg is None): default_header_msg = ''.join([c for c in header_msg1 if c not in ['•', '_', '*']])
    fulfillmentMessage.append({
        "text": {
            "text": [default_header_msg]
        }
    })

    RichMessages = {
        # "fulfillmentText": defaultPayload,
        "fulfillmentMessages": fulfillmentMessage,
        "payload": {
            "slack": {
                "attachments": [{
                    "blocks": slackBlocks
                }]
            },
        }
    }
    return RichMessages
