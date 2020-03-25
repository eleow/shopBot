"""
    Helper file to generate lookup files for RASA training
    The contents of these files should also be transferred (manually)
        to the respective entities of the chatito files
        to generate training and test samples
"""

import csv
import os
import sys
import pandas as pd
import unidecode
import re

visualise = True

print('Executing from ', os.path.dirname(sys.argv[0]))
os.chdir(os.path.dirname(sys.argv[0]))


# Generate lookup file for intent 'whatis', for entity 'term'
WHATIS_SOURCE = '../../Fulfillment/data/glossary_cleaned.csv'
WHATIS_DEST = 'entity_whatis_term.txt'
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
print('Writing contents to ', WHATIS_DEST)
with open(WHATIS_DEST, 'w+') as f:
    f.writelines(whatis_list)


# Generate lookup file for intent 'price', for entity 'model' and 'brand'
brand_model_dict = {}
BRAND_MODEL_SRC = '../../Fulfillment/data/treoo_data.xls'
BRAND_DEST = 'entity_brand.txt'
MODEL_DEST = 'entity_model.txt'

df = pd.read_excel(BRAND_MODEL_SRC, index_col=0)

# Clean-up Brand
brands = df['Brand'].str.strip().str.lower()
brands = [unidecode.unidecode(u'' + b) for b in brands]
df['Brand'] = brands

# Clean-up ProductModelName
blacklist = [
    'quietpoint(r) active', 'metal /',
    'quincy jones signature series', 'waterproof walkman neckband',
    '2nd generation'
]
temp = []

for m in df['ProductModelName']:
    # remove symbols, unidecode
    m = re.sub(r'[®]', '', unidecode.unidecode(m).strip().lower())

    # manual removal of certain words that we know are 'wrong'
    # probably not the most efficient method to do this, but whatever..
    for black in blacklist:
        m = m.replace(black, "")

    # join lone letters to string containing digits (k 450 -> k450)
    m = re.sub(r'^([a-zA-Z]){1}\s(\w?\d{1}\w)', r'\1\2', m)
    m = re.sub(r'(.*)\s{1}([a-zA-Z]){1}\s(\w?\d{1}\w)', r'\1 \2\3', m)

    temp.append(m.strip())

df['ProductModelName'] = temp

# Generate list of brands and models for rasa training
# have to manually add newlines before writing to file
unique_brands = df['Brand'].unique()
unique_brands = [b + '\n' for b in unique_brands]
unique_models = df['ProductModelName'].unique()
unique_models = [m + '\n' for m in unique_models]


print('Writing contents to ', BRAND_DEST)
with open(BRAND_DEST, 'w+') as f:
    f.writelines(unique_brands)

print('Writing contents to ', MODEL_DEST)
with open(MODEL_DEST, 'w+') as f:
    f.writelines(unique_models)
    # for m in unique_models:
    #     print(m)
    #     f.write(m)

# if visualise:
#     import networkx as nx
#     import matplotlib.pyplot as plt
#     brand_model_dict = df.groupby(['Brand'])['ProductModelName'].apply(list).to_dict()

#     g = nx.DiGraph()
