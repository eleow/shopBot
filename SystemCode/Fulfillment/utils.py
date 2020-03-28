from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import sys
import argparse
import unidecode
import re
import string

def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
    """Decorator function that allows crossdomain requests.
      Courtesy of
      https://blog.skyred.fi/articles/better-crossdomain-snippet-for-flask.html
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """ Determines which methods are allowed
        """
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        """The decorator function
        """
        def wrapped_function(*args, **kwargs):
            """Caries out the actual cross domain code
            """
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


def sizeof_fmt(num, suffix='B'):
    ''' by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified'''
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def get_memory_size_locals(scope):
    for name, size in sorted(((name, sys.getsizeof(value)) for name, value in scope.items()),
                             key=lambda x: -x[1])[:10]:
        print("{:>30}: {:>8}".format(name, sizeof_fmt(size)))


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def cleanup_product_list(d, brand_col='Brand', model_col='ProductModelName',
                         price_col='Product Price',
                         info_arr=['Product Price', 'Product Image URL', 'Product URL']):

    # Filter away null rows for brand, model or price
    # make a copy of the slice () otherwise http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-view-versus-copy
    df = d[d[brand_col].notnull() & d[model_col].notnull() & d[price_col].notnull()].copy()

    # Clean-up Price - convert to decimal
    if df.dtypes[price_col] != float:
        prices = df[price_col].str.replace('[S$,]', '', regex=True).astype(float)
        df[price_col] = prices

    # Clean-up Brand - perform unidecode
    brands = df[brand_col].str.strip().str.lower()
    brands = [unidecode.unidecode(u'' + b) for b in brands]
    brands = [b.replace('senneheiser', 'sennheiser') for b in brands]
    df[brand_col] = brands

    # Clean-up ProductModelName
    blacklist = [
        'quietpoint(r) active', 'metal /',
        'quincy jones signature series', 'waterproof walkman neckband',
        '2nd generation',
        '+remote'
    ]
    temp = []

    # Clean-up Model
    for m in df[model_col]:
        # remove symbols, unidecode
        m = re.sub(r'[®+]', '', unidecode.unidecode(str(m)).strip().lower())

        # manual removal of certain words that we know are 'wrong'
        # probably not the most efficient method to do this, but whatever..
        for black in blacklist:
            m = m.replace(black, "")

        # strip punctuation because preprocessing step will also do likewise
        m = ''.join([t for t in m if t not in string.punctuation])

        # perform stemming using snowball (this helps to make words singular)
        # m = sb_stemmer.stem(m)

        # join lone letters to string containing digits (k 450 -> k450)
        m = re.sub(r'^([a-zA-Z]){1}\s(\w?\d{1}\w)', r'\1\2', m)
        m = re.sub(r'(.*)\s{1}([a-zA-Z]){1}\s(\w?\d{1}\w)', r'\1 \2\3', m)

        temp.append(m.strip())

    df[model_col] = temp

    # Generate list of brands and models for rasa training
    unique_brands = df[brand_col].unique()
    unique_models = df[model_col].unique()

    # Generate brand_model_info_dict
    brand_model_info_dict = df.groupby([brand_col])[model_col].apply(list).to_dict()
    # brand_model_info_dict = brand_model_dict.copy()
    for k, v in brand_model_info_dict.items():
        # for each brand, have a dict with model as key, and info as values
        model_info_dict = {}
        for m in v:
            # print(k, m)
            temp = df[(df[brand_col] == k) & (df[model_col] == m)].iloc[0]  # just get first match
            temp = temp[info_arr].to_dict()
            model_info_dict[m] = temp

        brand_model_info_dict[k] = model_info_dict

    return df, unique_brands, unique_models, brand_model_info_dict


def generate_brand_model_data(brand_model_src, brand_model_info_dest,
    brand_model_dest, model_brand_dest, brand_col_name, model_col_name, price_col_name, info_arr):

    import pickle
    import pandas as pd

    df = pd.read_excel(brand_model_src, index_col=0)
    df, unique_brands, unique_models, brand_model_info_dict = cleanup_product_list(df, brand_col_name, model_col_name, price_col_name, info_arr)

    brand_model_dict = df.groupby([brand_col_name])[model_col_name].apply(list).to_dict()
    model_brand_dict = df.groupby([model_col_name])[brand_col_name].apply(list).to_dict()

    for k, v in model_brand_dict.items():
        v = list(dict.fromkeys(v))  # remove duplicates
        model_brand_dict[k] = v

    print('Writing pickle files for brand, model, info dictionaries')
    with open(brand_model_dest, 'wb+') as f:
        pickle.dump(brand_model_dict, f)
    with open(model_brand_dest, 'wb+') as f:
        pickle.dump(model_brand_dict, f)
    with open(brand_model_info_dest, 'wb+') as f:
        pickle.dump(brand_model_info_dict, f)

    return unique_brands, unique_models, brand_model_dict, model_brand_dict, brand_model_info_dict
