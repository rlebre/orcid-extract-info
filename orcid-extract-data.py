#!/usr/bin/env python
from flask import Flask, abort, request
import requests
import requests.auth
import urllib
import webbrowser
import datetime
import argparse
import json
import orcid_parser
import os

CLIENT_ID = 'APP-OOJAC0Y3XDYQQO9S'#None # Fill this in with your client ID
CLIENT_SECRET = '01ee56d6-89fb-4e94-9bf5-377aa52e9875'#None # Fill this in with your client secret
REDIRECT_URI = "http://localhost:65010/auth_callback"

API_URL = "https://pub.orcid.org/v2.0"

TOKEN = ""
args = {}

def user_agent():
    '''reddit API clients should each have their own, unique user-agent
    Ideally, with contact info included.
    
    e.g.,
    return "oauth2-sample-app by /u/%s" % your_reddit_username

    '''
    raise NotImplementedError()

def base_headers():
    return {"User-Agent": user_agent()}


app = Flask(__name__)
@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with ORCID</a>'
    return text % make_authorization_url()


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    #state = str(uuid4())
    #save_created_state(state)
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              #"state": state,
              "redirect_uri": REDIRECT_URI,
              "scope": "/authenticate"}
              
    url = "https://orcid.org/oauth/authorize?" + urllib.parse.urlencode(params)
    return url


# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache.
def save_created_state(state):
    pass
def is_valid_state(state):
    return True

@app.route('/auth_callback')
def auth_callback():
    code = request.args.get('code')
    access_token = get_token(code)

    return '<script>self.close();</script>'

def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    headers = {"Accept":"application/json"} 
    response = requests.post("https://orcid.org/oauth/token",
                             auth=client_auth,
                             headers=headers,
                             data=post_data)

    token_json = response.json()
    #print("OAUTH-TOKEN: ", token_json)

    if args.inputfile:
        entries = []

        with open(args.inputfile) as input_file:
            for i,line in enumerate(input_file):
                print("getting: ", line.rstrip('\n'))
                entries.append(get_personal_details(line.rstrip('\n'), token_json))
        
        if args.output:
            with open(args.output, "w") as f:
                print(json.dumps(entries, sort_keys=True, indent=3))
                f.write(json.dumps(entries, sort_keys=True, indent=3))
    elif args.id:
        info = get_personal_details(args.id, token_json)
        if args.output:
            with open(args.output, "w") as f:
                f.write(json.dumps(info, sort_keys=True, indent=3))

    return token_json["access_token"]

def get_personal_details(orcid, token_json):
    #print("WEIRD TOKEN: ", TOKEN)

    headers = {"Accept":"application/json", "Authorization" : token_json['access_token'] }

    url = API_URL + '/' + orcid
    response = requests.get(url,headers=headers).json()

    if args.save_requests:
        with open( os.path.join(args.save_requests, "{}.json".format(orcid)), 'w') as outfile:
            json.dump(response, outfile)

    ret = {}

    ret["profile"] = orcid_parser.parse_personal_details(response)
    ret["publications"] = []

    work_codes = orcid_parser.get_work_codes(response)
    print("Identified", len(work_codes), "works")

    get_publication_details(work_codes, orcid)

    for i in range(0, len(work_codes), 50):
        end = i + 50
        if end > len(work_codes):
            end = len(work_codes)
        arr = work_codes[i:end]

        tmp_pub_list = get_publication_details(arr, orcid)

        if args.save_requests:
            with open(os.path.join(args.save_requests,"{}-pubs-{}.json".format(orcid, i)), 'w') as outfile:
                json.dump(tmp_pub_list, outfile)

        ret["publications"].append(orcid_parser.parse_works_bulkdata(tmp_pub_list))


    return ret
    # if args.output:
    #     with open(args.output, "w") as f:
    #         f.write(json.dumps(ret, sort_keys=True, indent=3))

    # print("DONE", orcid)
    # print("Ctrl + C to terminate")


def get_publication_details(work_codes, orcid):
    headers = {"Accept":"application/json", "Authorization" : TOKEN}
    url = "{}/{}/works/{}".format(API_URL, orcid, ",".join( str(code) for code in work_codes ))
    response = requests.get(url,headers=headers).json()
    #print("Fetching: ",url)

    return response


def parse_args():
    parser = argparse.ArgumentParser(description='Script that reads records from OrcID and outputs to a json file')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-id', '--id', help='Provide the OrcID desired', type=str)
    group.add_argument('-i', '--inputfile', help='Provide a file containing a list of the OrcIDs desired (one per line)', type=str)

    parser.add_argument("-s", '--save_requests', help='Folder where to save the intermidiate request files', type=str, required=False)
    parser.add_argument("-o", '--output', help='JSON File where to save the simplified model', type=str, required=False)

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()

    if args.save_requests:
        os.makedirs(args.save_requests, exist_ok=True)

    url = "http://localhost:65010"
    webbrowser.open(make_authorization_url())

    app.run(debug=True, port=65010)


