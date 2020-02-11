'''
    @author Edmund Leow

    # Script to invoke DialogFlow backend to perform unit-testing of intents
    # Takes in path of DialogFlow CREDENTIALS and TEST_FILE from config.ini

'''


import os
from os.path import dirname, join, realpath
import json
import errno
import re
import dialogflow_v2 as dialogflow
from dialogflow_v2.types import TextInput, QueryInput

import argparse
import configparser


###############################################################################
# Function definitions
###############################################################################
def relativeToAbsolutePath(dir_path, relative_path):
    # convert relative to absolute path, removing extra " and ' if present
    return join(dir_path, re.sub(r'[\'\"]+', '', relative_path))


def check_params(detected_params, expected_params, verbose):
    match_p = []
    for p in expected_params:
        k = p['key']
        v = p['value']
        t = p['type']

        match = False
        # check if entity value matches what is expected
        if (t == 'number'):
            match = (detected_params.fields[k].number_value == v)
        else:
            match = (detected_params.fields[k].string_value == v)

        match_p.append(match)
        if (verbose and not match):
            print('Parameter:', k, 'Detected Value', detected_params.fields[k], 'Expected Value:', v)
    if (verbose):
        print()
    return all(match_p)  # all params must match to pass


def send_input(project_id, session_id, text, language_code,
               expected_intent, expected_params, threshold_confidence=0.6, verbose=0):
    """Sends a text input and matches detected intent with expected intent

        Returns True if 'detected intent' matches expected_intent, and is above threshold_confidence,
        else returns False
    """

    session_client = dialogflow.SessionsClient()
    session_path = session_client.session_path(project_id, session_id)
    text_input = TextInput(text=text, language_code=language_code)
    query_input = QueryInput(text=text_input)

    response = session_client.detect_intent(session=session_path, query_input=query_input)
    detected_params = response.query_result.parameters
    result_intent = (response.query_result.intent.display_name == expected_intent
                     and response.query_result.intent_detection_confidence > threshold_confidence)

    if (verbose > 0):
        print('Session path: {}'.format(session_path))
        print('Query text: {}'.format(response.query_result.query_text))
        print('Detected intent: {} (confidence: {})'.format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence))
        print('Expected intent: {} (confidence > {})'.format(
            expected_intent,
            threshold_confidence))
        # print('Fulfillment text: {}'.format(response.query_result.fulfillment_text))
        print('Intent matching: {}'.format('Pass' if result_intent else 'Fail'))

    result_params = check_params(detected_params, expected_params, verbose)
    return result_intent, result_params

###############################################################################
# Main script
###############################################################################


# Read in input parameters from a configuration file
# - Remember to add your own config.ini and own json file in test-directory
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", default="./config.ini", help="""Location of config file. The configuration file should contain the following:
    (i) CREDENTIALS - path to the DialogFlow JSON file, relative to script,
    (ii) TEST_FILE - path to file containing test cases, relative to script""")

parser.add_argument("-v", "--verbose", default=1, help="0-Only print out results. 1-Print out details of each testcase")
parser.add_argument("-t", "--threshold", default=0.6, help="Minimum confidence to consider intent as passed")
# if len(sys.argv) < 2:
#     parser.print_help()
#     sys.exit(1)
args = parser.parse_args()
config = configparser.ConfigParser()

# Change working directory to path of this file
dir_path = dirname(realpath(__file__))
os.chdir(dir_path)

# Retrieve actual input parameters in config file
TEST_FILE = ""
CREDENTIALS = ""
PROJECT_ID = ""
if os.path.isfile(args.config):

    # Get values in config file
    config.read(args.config)
    TEST_FILE = relativeToAbsolutePath(dir_path, config['DIALOGFLOW']['TEST_FILE'])
    CREDENTIALS = relativeToAbsolutePath(dir_path, config['DIALOGFLOW']['CREDENTIALS'])

    # Retrieve PROJECT_ID from CREDENTIALS file
    with open(CREDENTIALS) as f:
        data = json.load(f)
    PROJECT_ID = data['project_id']

    # Verify that TEST_FILE exists
    isFile = os.path.isfile(TEST_FILE)
    if (not isFile):
        # print('[ERROR] Test file for testcases not found at ' + TEST_FILE)
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), TEST_FILE)

    print()
    print("CONFIG FILE:", args.config)
    print("TEST FILE:", TEST_FILE)
    print("CREDENTIALS:", CREDENTIALS)
    print("PROJECT ID:", PROJECT_ID)
else:
    # print('[ERROR] Config file for DialogFlow credentials not found at ' + args.config)
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), args.config)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS


# Read in testcases and test
with open(TEST_FILE) as f:
    test_cases = json.load(f)['testcases']

total_cases = len(test_cases)
total_intent_pass = 0
total_param_pass = 0

print('=' * 20)
for t in test_cases:
    session_id = os.urandom(24).hex()  # separate session for each test-case
    utterance = t['utterance']
    expected_intent = t['intent']
    params = t['entities']

    result_intent, result_param = send_input(PROJECT_ID, session_id,
                                             utterance, 'en', expected_intent, params,
                                             threshold_confidence=args.threshold,
                                             verbose=args.verbose)
    if result_intent:
        total_intent_pass += 1
    if result_param:
        total_param_pass += 1

print('=' * 20)
print('Total testcases: {}'.format(total_cases))
print('Total intents passed: {}'.format(total_intent_pass))
print('Total params passed: {}'.format(total_param_pass))
