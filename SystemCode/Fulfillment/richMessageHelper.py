import urllib.parse as urllib
import random

BOT_NAME = 'AudioPhil'
BOT_TYPE = 'shopping bot'
BOT_DOMAIN = 'earphones and headphones'


def displayWelcome_slack(public_url, default_header_msg=None, additional_header=None):
    fulfillmentMessage = []
    slackBlocks = []

    # Components of introduction message
    introArr = [
        "Hi! I am %s, your personal %s for %s! 👩 " % (BOT_NAME, BOT_TYPE, BOT_DOMAIN),
        "Hello there! I am %s, the %s for %s 😋 " % (BOT_NAME, BOT_TYPE, BOT_DOMAIN),
        "👋 %s here. How can I help you today? 😊 " % BOT_NAME,
        "Good day! 😁 I'm %s, the %s for %s. What would you like to do today?" % (BOT_NAME, BOT_TYPE, BOT_DOMAIN)
    ]
    intro = random.choice(introArr) if not additional_header else additional_header

    intro2 = "• Find headphones that match your preferences\n• Learn more about headphone/earphone terminology "
    # body2 = "" # body2 = "Or just click one of the buttons below:"

    header_msg1 = intro + "\n\nHere's a couple of the things you can do:\n" + intro2
    # header_msg = header_msg1 + "\n\n" + body2

    # populate slackBlocks
    # TODO

    if (default_header_msg is None): default_header_msg = ''.join([c for c in header_msg1 if c not in ['•', '_', '*']])  # remove mrkdown characters
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
