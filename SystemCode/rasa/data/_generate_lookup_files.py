"""
    Helper file to generate lookup files for RASA training
    The contents of these files should also be transferred (manually)
        to the respective entities of the chatito files
        to generate training and test samples
"""
# %%
import sys
import os
import csv
# import pandas as pd
import pickle
from shutil import copyfile

print('Executing from ', os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))
print(os.getcwd())

# sys.path.append("SystemCode/Fulfillment")
sys.path.append("../../Fulfillment")  # Adds parent directory to python modules path.
# from ...Fulfillment.utils import cleanup_product_list
from utils import cleanup_product_list, generate_brand_model_data

visualise = False

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

# %%
# Generate lookup file for intent 'price', for entity 'model' and 'brand'
# For Treoo - save lookup tables
# brand_model_dict = {}
BRAND_MODEL_SRC = '../../Fulfillment/data/data_treoo.xls'
BRAND_MODEL_INFO_DEST = 'p_treoo_brand_model_info.pickle'
BRAND_MODEL_DEST = 'p_treoo_brand_model.pickle'
MODEL_BRAND_DEST = 'p_treoo_model_brand.pickle'

treoo_brands, treoo_models, treoo_brand_model_dict, treoo_model_brand_dict, treoo_brand_model_info_dict = generate_brand_model_data(BRAND_MODEL_SRC, BRAND_MODEL_INFO_DEST,
    BRAND_MODEL_DEST, MODEL_BRAND_DEST, "Brand", "ProductModelName", "Product Price", ['Product Price', 'Product Image URL', 'Product URL', 'ProductFeatures'])

# %%
# For Amazon - save lookup tables
BRAND_MODEL_SRC = '../../Fulfillment/data/data_amazon.xlsx'
BRAND_MODEL_INFO_DEST = 'p_amazon_brand_model_info.pickle'
BRAND_MODEL_DEST = 'p_amazon_brand_model.pickle'
MODEL_BRAND_DEST = 'p_amazon_model_brand.pickle'

amazon_brands, amazon_models, amazon_brand_model_dict, amazon_model_brand_dict, amazon_brand_model_info_dict = generate_brand_model_data(BRAND_MODEL_SRC, BRAND_MODEL_INFO_DEST,
    BRAND_MODEL_DEST, MODEL_BRAND_DEST, "Organziation", "ProductModelName", "new_price", ["new_price", "url", "Image", "ProductFeatures"])

# %%
# Combine brands and models from Treoo and Amazon
BRAND_DEST = 'entity_brand.txt'
MODEL_DEST = 'entity_model.txt'
PRICE_CHATITO_BASE = './chatito/_base_intent_price.chatito'

unique_brands = sorted(set(treoo_brands.tolist() + amazon_brands.tolist()))
unique_models = sorted(set(treoo_models.tolist() + amazon_models.tolist()))

intersect_brands = set(treoo_brands).intersection(amazon_brands)
intersect_models = set(treoo_models).intersection(amazon_models)

a = amazon_brand_model_info_dict
t = treoo_brand_model_info_dict

# standardise keys for a with t's
for k in a.keys():
    for m in a[k].keys():
        a[k][m]["Product Price"] = a[k][m].pop("new_price")
        # a[k][m]["Product URL"] = "http://" + a[k][m].pop("url")  # spreadsheet did not include http:// prefix!
        a[k][m]["Product URL"] = a[k][m].pop("url")  # spreadsheet did not include http:// prefix!
        a[k][m]["Product Image URL"] = a[k][m].pop("Image")

# %%
# Combine a & t into 1 brand_model_info_dict

combined = {**a, **t}  # combine a and t, t takes precedence
for brand in combined.keys():
    # we want to consider brand common in both a and t
    if brand in intersect_brands:
        combined[brand] = {**a[brand], **t[brand]}  # combine models, t takes precedence

        for model in combined[brand].keys():
            # we want to get the model with lower price
            # if model in intersect_models: # model same name but maybe it is for different brand
            if model in a[brand] and model in t[brand]:
                a_price = a[brand][model]["Product Price"]
                t_price = t[brand][model]["Product Price"]
                print(f"{brand}, {model}, {a_price}, {t_price}")
                if a_price < t_price:
                    combined[brand][model] = a[brand][model]

BRAND_MODEL_INFO_DEST = 'p_brand_model_info.pickle'
with open(BRAND_MODEL_INFO_DEST, 'wb+') as f:
    pickle.dump(combined, f)

# %%
# Combine a & t into 1 model_brand_dict
mt = treoo_model_brand_dict
ma = amazon_model_brand_dict
mb_dict = {**ma, **mt}

for model in mb_dict.keys():
    if model in ma and model in mt:
        print(model, ma[model], mt[model])
        mb_dict[model] = list(set(ma[model] + mt[model]))

MODEL_BRAND_DEST = 'p_model_brand.pickle'
with open(MODEL_BRAND_DEST, 'wb+') as f:
    pickle.dump(mb_dict, f)

# %%
if visualise:
    import matplotlib.pyplot as plt
    from matplotlib_venn import venn2
    nb = (len(treoo_brands), len(amazon_brands), len(intersect_brands))
    nm = (len(treoo_models), len(amazon_models), len(intersect_models))

    venn2(subsets=(nb[0]-nb[2],nb[1]-nb[2],nb[2]), set_labels=('Treoo', 'Amazon'))
    plt.title('Headphone Brands')
    plt.show()

    venn2(subsets=(nm[0]-nm[2],nm[1]-nm[2],nm[2]), set_labels= ('Treoo', 'Amazon') )
    plt.title('Headphone Models')
    plt.show()


# %%
# Save entity files for dialogflow and rasa
# dialogflow
with open(MODEL_DEST.replace('entity_', 'dialogflow_entity_'), 'w+') as f:
    f.writelines(['\"' + b + '\",\"' + b + '\"\n' for b in unique_models])

with open(BRAND_DEST.replace('entity_', 'dialogflow_entity_'), 'w+') as f:
    f.writelines(['\"' + b + '\",\"' + b + '\"\n' for b in unique_brands])

# rasa
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

print('Appending entities to chatito file for intent_price')
price_chatito = PRICE_CHATITO_BASE.replace('_base_', '')
copyfile(PRICE_CHATITO_BASE, price_chatito)
with open(price_chatito, 'a') as f:
    f.write('\n@[brand]\n')
    f.writelines([' ' * 4 + i for i in unique_brands])
    f.write('\n@[model]\n')
    f.writelines([' ' * 4 + i for i in unique_models])
print()

# if visualise:
#     import networkx as nx
#     import matplotlib.pyplot as plt
#     brand_model_dict = df.groupby(['Brand'])['ProductModelName'].apply(list).to_dict()

#     g = nx.DiGraph()


# %%
