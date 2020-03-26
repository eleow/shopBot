"""
    Helper file to generate lookup files for RASA training
    The contents of these files should also be transferred (manually)
        to the respective entities of the chatito files
        to generate training and test samples
"""
import sys
import os
import csv
import pandas as pd
import pickle
from shutil import copyfile

print('Executing from ', os.path.dirname(sys.argv[0]))
os.chdir(os.path.dirname(sys.argv[0]))

sys.path.append("../../Fulfillment")  # Adds parent directory to python modules path.
# from ...Fulfillment.utils import cleanup_product_list
from utils import cleanup_product_list

visualise = True

# Generate lookup file for intent 'whatis', for entity 'term'
WHATIS_SOURCE = '../../Fulfillment/data/glossary_cleaned.csv'
WHATIS_DEST = 'entity_whatis_term.txt'
WHATIS_CHATITO_BASE = './chatito/_base_intent_whatis.chatito'
whatis_list = []


with open(WHATIS_SOURCE, mode='r', encoding="utf-8-sig") as infile:
    reader = csv.reader(infile)
    for row in reader:

        whatis_list.append(row[0].strip().lower() + '\n')

        # Expand synonyms / Copy description and source
        if (row[3] != ''):
            synonyms = row[3].split(',')
            for s in synonyms:
                whatis_list.append(s.strip().lower() + '\n')

# print(whatis_list)
print('Writing whatis_list to ', WHATIS_DEST)
with open(WHATIS_DEST, 'w+') as f:
    f.writelines(whatis_list)

print('Appending entities to chatito file for intent_whatis')
whatis_chatito = WHATIS_CHATITO_BASE.replace('_base_', '')
copyfile(WHATIS_CHATITO_BASE, whatis_chatito)
with open(whatis_chatito, 'a') as f:
    f.write('\n@[term]\n')
    f.writelines([' '*4 + i for i in whatis_list])
print()

# Generate lookup file for intent 'price', for entity 'model' and 'brand'
brand_model_dict = {}
BRAND_MODEL_SRC = '../../Fulfillment/data/treoo_data.xls'
BRAND_DEST = 'entity_brand.txt'
MODEL_DEST = 'entity_model.txt'
BRAND_MODEL_DEST = 'brand_model.pickle'
PRICE_CHATITO_BASE = './chatito/_base_intent_price.chatito'

df = pd.read_excel(BRAND_MODEL_SRC, index_col=0)
df, unique_brands, unique_models = cleanup_product_list(df, 'Brand', 'ProductModelName')
brand_model_dict = df.groupby(['Brand'])['ProductModelName'].apply(list).to_dict()

# have to manually add newlines before writing to file
unique_brands = [b + '\n' for b in unique_brands]
unique_models = [m + '\n' for m in unique_models]

print('Writing unique_brands to ', BRAND_DEST)
with open(BRAND_DEST, 'w+') as f:
    f.writelines(unique_brands)

print('Writing unique_models to ', MODEL_DEST)
with open(MODEL_DEST, 'w+') as f:
    f.writelines(unique_models)
    # for m in unique_models:
    #     print(m)
    #     f.write(m)

print('Writing brand_model_dict to ', BRAND_MODEL_DEST)
with open(BRAND_MODEL_DEST, 'wb+') as f:
    pickle.dump(brand_model_dict, f)

print('Appending entities to chatito file for intent_price')
price_chatito = PRICE_CHATITO_BASE.replace('_base_', '')
copyfile(PRICE_CHATITO_BASE, price_chatito)
with open(price_chatito, 'a') as f:
    f.write('\n@[brand]\n')
    f.writelines([' '*4 + i for i in unique_brands])
    f.write('\n@[model]\n')
    f.writelines([' '*4 + i for i in unique_models])
print()

# if visualise:
#     import networkx as nx
#     import matplotlib.pyplot as plt
#     brand_model_dict = df.groupby(['Brand'])['ProductModelName'].apply(list).to_dict()

#     g = nx.DiGraph()
