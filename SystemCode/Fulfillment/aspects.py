# https://stackoverflow.com/questions/49589508/webhooks-for-slot-filling

from flask import make_response, jsonify
import pickle
import pandas as pd
import os
import emoji
import math
import random

file_path = os.path.dirname(__file__)
df_src = os.path.join(file_path, 'data//df_aspect.pkl')
with open(df_src, 'rb+') as f:
    df = pickle.load(f)


def aspect_intent_handler(req, public_url):
    global nlp

    allBrands = list(set([df[("a", "Organization")][i].lower() for i in range(
        len(df[("a", "Organization")])) if not df[("a", "Organization")].isna()[i]]))
    # print(allBrands)
    # brandsNotFound = []
    brandsFound = []
    lowerLimit = 2
    upperLimit = 10

    new_df = pd.DataFrame()
    event = None
    followupEvent = {}

    # intent_name = req["queryResult"]["intent"]["displayName"].lower()
    action = req["queryResult"].get("action", "")
    productType = req["queryResult"]["parameters"].get("product_type", [])
    wired = req["queryResult"]["parameters"].get("wired", [])
    ent_brand = req["queryResult"]["parameters"].get("ent_brand", [])
    affirmBrand = req["queryResult"]["parameters"].get("affirm_brand", "")
    confirm = req["queryResult"]["parameters"].get("confirm", "")
    # print("action", action)
    # print("confirm", confirm, type(confirm))
    # print("productType", productType)
    # print("wire", wired)
    # print("ent_brand", ent_brand)
    # print("affirm", affirmBrand)

    productTypeEmpty = (productType == [])
    wiredEmpty = (wired == [])
    brandEmpty = (affirmBrand == "" and ent_brand == [])
    brandPartial = (affirmBrand == "yes" and ent_brand == [])

    oneEmpty = (productTypeEmpty or wiredEmpty or brandEmpty or brandPartial)

    # print("oneEmpty", oneEmpty)

    if oneEmpty:
        if productTypeEmpty:
            event = "event_ask_product_type"
        elif wiredEmpty:
            event = "event_ask_wired"
        elif brandEmpty:
            event = "event_ask_brand"
        elif brandPartial:
            event = "event_ask_brand_partial"

        followupEvent = {
            "name": event,
            "parameters": {
                "product_type": productType,
                "wired": wired,
                "affirm_brand": affirmBrand,
                "ent_brand": ent_brand,
            }
        }

        # print(followupEvent)
        return make_response(jsonify({"followupEventInput": followupEvent}))

    elif (action != "intent_confim_recommend.intent_confim_recommend-yes"):
        event = "event_confirm_recommend"

        if (set(["earphones", "headphones"]).issubset(set(productType))) or ("both" in productType):
            productType = ["earphones/headphones"]
        if (set(["wired", "wireless"]).issubset(set(wired))) or ("both" in wired):
            wired = ["wired/wireless"]
        brand_mod = "" if (affirmBrand == "no" or ent_brand == [
                           "all"]) else ", ".join(ent_brand)

        #print("now confirming")
        #print("productType", productType)
        #print("wired", "wired")
        #print("ent_brand", ent_brand)
        # print("affirmBrand confirm", affirmBrand)

        followupEvent = {
            "name": event,
            "parameters": {
                "product_type": productType,
                "wired": wired,
                "ent_brand": ent_brand,
                "brand_mod": brand_mod,
                "affirm_brand": affirmBrand,
                "confirm": confirm
            }
        }

        # print(followupEvent)
        return make_response(jsonify({"followupEventInput": followupEvent}))

    else:
        if (set(["earphones", "headphones"]).issubset(set(productType))) or ("both" in productType):
            productType = ["earphones/headphones"]
        if (set(["wired", "wireless"]).issubset(set(wired))) or ("both" in wired):
            wired = ["wired/wireless"]

        brandAll = ((affirmBrand == "no" and ent_brand == [])
                    or ent_brand == ["all"])

        if not brandAll:
            # brandsNotFound = [b.capitalize() for b in brand if b not in allBrands]
            brandsFound = [b for b in ent_brand if b in allBrands]

        productTypeAll = (productType == ["earphones/headphones"])
        wiredAll = (wired == ["wired/wireless"])
        productType = productType[0]
        wired = wired[0]

        # product type, wired and brand not filtered
        if productTypeAll and wiredAll and brandAll:
            # print("cond 1")
            new_df = df
        # brand and wire not filtered
        elif not productTypeAll and wiredAll and brandAll:
            # print("cond 2")
            new_df = df[df[("a", "ProductType")] == productType]
        # brand and product type not filtered
        elif not wiredAll and productTypeAll and brandAll:
            # print("cond 3")
            new_df = df[df[("a", "Connectivity")] == wired]
        # wired and product type not filtered
        elif not brandAll and productTypeAll and wiredAll:
            # print("cond 4")
            new_df = df[df[("a", "Organization")
                           ].str.lower().isin(brandsFound)]
        # brand not filtered
        elif not productTypeAll and not wiredAll and brandAll:
            # print("cond 5")
            new_df = df[(df[("a", "ProductType")] == productType)
                        & (df[("a", "Connectivity")] == wired)]
        # wired not filtered
        elif not productTypeAll and not brandAll and wiredAll:
            # print("cond 6")
            new_df = df[(df[("a", "ProductType")] == productType) & (
                df[("a", "Organization")].str.lower().isin(brandsFound))]
        # product type not filtered
        elif not wiredAll and not brandAll and productTypeAll:
            # print("cond 7")
            new_df = df[(df[("a", "Connectivity")] == wired) & (
                df[("a", "Organization")].str.lower().isin(brandsFound))]
        else:
            # print("cond 8")
            new_df = df[(df[("a", "ProductType")] == productType) & (df[("a", "Connectivity")] == wired) & (
                df[("a", "Organization")].str.lower().isin(brandsFound))]

        if len(new_df) >= lowerLimit:
            new_df = new_df.sort_values(
                by=[("a", "overall_rating"), ("a", "num_reviews")], ascending=False)
            new_df = new_df[:upperLimit]

            return make_response(jsonify(display_carousel_browse(req, new_df, "google")))
        else:
            textArray = ["Oops, we could not find any products.",
                         "Sorry, no results were returned.",
                         "We were able to return any results. Please make other selections."]
            text = random.choice(textArray)
            fulfillmentMsg = [
                {
                    "text": {
                        "text": [
                            text
                        ]
                    }
                }
            ]
            return make_response(jsonify({"fulfillmentMessages": fulfillmentMsg, "outputContexts": clear_contexts(req)}))


def get_rating():
    rating_list = [":new_moon::new_moon::new_moon::new_moon::new_moon:",
                   ":last_quarter_moon::new_moon::new_moon::new_moon::new_moon:",
                   ":full_moon::new_moon::new_moon::new_moon::new_moon:",
                   ":full_moon::last_quarter_moon::new_moon::new_moon::new_moon:",
                   ":full_moon::full_moon::new_moon::new_moon::new_moon:",
                   ":full_moon::full_moon::last_quarter_moon::new_moon::new_moon:",
                   ":full_moon::full_moon::full_moon::new_moon::new_moon:",
                   ":full_moon::full_moon::full_moon::last_quarter_moon::new_moon:",
                   ":full_moon::full_moon::full_moon::full_moon::new_moon:",
                   ":full_moon::full_moon::full_moon::full_moon::last_quarter_moon:",
                   ":full_moon::full_moon::full_moon::full_moon::full_moon:"
                   ]
    emoji_rating = [emoji.emojize(rating) for rating in rating_list]

    return emoji_rating


def clear_contexts(req):
    outputContexts = req["queryResult"]["outputContexts"]
    contextNames = ["context_recommend", "context_headphones", "context_wired", "context_brand",
                    "intent_confim_recommend-followup", "intent_confim_recommend-followup"]
    outputContextList = []

    for context in outputContexts:
        for contextName in contextNames:
            if context["name"].split('/')[-1] == contextName:
                outputContextList.append(
                    {"name": context["name"], "lifespanCount": 0})

    return outputContextList


def display_carousel_browse(req, df, platform=""):
    textArray = ["Here are {} products from Amazon SG!".format(len(df)),
                 "We found {} products from Amazon SG!".format(len(df)),
                 "There are {} products from Amazon SG!".format(len(df))]
    text = random.choice(textArray)
    response = {
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": text
                            }
                        },
                        {
                            "carouselBrowse": {
                                "items": [
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }

    emoji_rating = get_rating()
    carouselBrowseItems = []
    for i in range(len(df)):

        # carouselBrowseItem = {"title": "", "openUrlAction": {
        #     "url": ""}, "description": "", "footer": "", "image": {"url": "", "accessibilityText": ""}}
        design_rating = emoji_rating[int(df[("a", "design_rating_round")][i] / 0.5) -
                                     1] if not math.isnan(df[("a", "design_rating_round")][i]) else "??"
        fit_rating = emoji_rating[int(df[("a", "fit_rating_round")][i] / 0.5)
                                  ] if not math.isnan(df[("a", "fit_rating_round")][i]) else "??"
        price_rating = emoji_rating[int(df[("a", "price_rating_round")][i] / 0.5)
                                    ] if not math.isnan(df[("a", "price_rating_round")][i]) else "??"
        sound_rating = emoji_rating[int(df[("a", "sound_rating_round")][i] / 0.5)
                                    ] if not math.isnan(df[("a", "sound_rating_round")][i]) else "??"
        review_rating = emoji_rating[int(df[("a", "review_rating_round")][i] / 0.5)
                                     ] if not math.isnan(df[("a", "review_rating_round")][i]) else "??"

        rating_over_5 = int(df[("a", "review_rating_round")][i])

        price = "SGD$" + str(df[("a", "new_price")][i]
                             ) if not math.isnan(df[("a", "new_price")][i]) else "??"

        carouselBrowseItem = {
            "title": df[("a", "Name")][i],
            "subtitle": "",
            "header": {
                "overlayText": price,
                "imgSrc": ""
            },
            "description": "Design: {}".format(design_rating) + "\n" + "Fit: {}".format(fit_rating) + "\n" + "Value: {}".format(
                price_rating) + "\n" + "Sound: {}".format(sound_rating),
            "titleExt": f"{rating_over_5}/5",
            "buttons": [
                {
                    "name": "Get it!",
                    "action": {
                        "type": "link",
                        "payload": {
                            "url": df[("a", "url")][i]
                        }
                    }
                }
            ]
        }
        carouselBrowseItems.append(carouselBrowseItem)

    custom_carousel = {
        "message": "Carousel",
        "platform": "kommunicate",
        "metadata": {
            "contentType": "300",
            "templateId": "10",
            "payload": carouselBrowseItems
        }
    }

    response["fulfillmentMessages"] = [{"payload": custom_carousel}]
    response["outputContexts"] = clear_contexts(req)
    # print(response)

    return response
