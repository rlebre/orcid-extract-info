import json
import sys
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
import argparse

personal_details = None

# CONST PARSERS
jsonpath_expr = {}
jsonpath_expr["doi"] = parse('external-ids.external-id[?(external-id-type = "doi")].external-id-value')
jsonpath_expr["url"] = parse('url.value')
jsonpath_expr["created"] = parse('created-date.value')
jsonpath_expr["contrib"] = parse('contributors.contributor[*].credit-name.value')


# PERSON
jsonpath_expr["orcid"] = parse('person.name.path')
jsonpath_expr["name"] = parse('person.name.credit-name.value')
jsonpath_expr["scopus"] = parse('person.external-identifiers.external-identifier[?(external-id-type = "Scopus Author ID")].external-id-value')


#TODO: will PR to JSONPATH-nG
def find_first(jsonpath_expr, datum):
    m = jsonpath_expr.find(datum)
    if len(m) > 0:
        return m[0].value

    return m

def get_work_codes(personal_details):

    put_codes = []

    try:
        for work_grp in personal_details["activities-summary"]["works"]["group"]:
            for work_summary in work_grp["work-summary"]:
                put_code = work_summary["put-code"]
                put_codes.append(put_code)
    except:
        pass

    return put_codes

def parse_work_entry(work_entry):
    return_dict = { }

    try:
        return_dict['title'] = work_entry["title"]["title"]["value"]
    except:
        return_dict['title'] = ""

    try:
        return_dict['journal'] = work_entry["journal-title"]["value"]
    except: 
        return_dict['journal'] = ""
 
    try:
        return_dict['year'] = work_entry["publication-date"]["year"]["value"]
    except:
        return_dict['year'] = ""

    try:
        return_dict['type'] = work_entry["type"]
    except:
        return_dict['type'] = ""

    try:
        return_dict['doi'] = [ m.value for m in jsonpath_expr["doi"].find(work_entry)]
    except:
        return_dict['doi'] = []
   
    try:
        if find_first(jsonpath_expr["url"], work_entry) == []:
            return_dict['url'] = ""
        else:
            return_dict['url'] = find_first(jsonpath_expr["url"], work_entry)
            
    except:
        return_dict['url'] = ""

    try:
        return_dict['created'] = find_first(jsonpath_expr["created"], work_entry)
    except:
        return_dict['created'] = ""

    try:
        return_dict['contributions'] = [m.value for m in jsonpath_expr["contrib"].find(work_entry)]
    except:
        return_dict['contributions'] = []

    return return_dict


def parse_personal_details(datum):
    return {
        "name": find_first(jsonpath_expr["name"], datum),
        "orcid": find_first(jsonpath_expr["orcid"], datum),
        "scopus": find_first(jsonpath_expr["scopus"], datum),

    }

    # }
    #             eid: "",-
    #             url: "",
    #             created: "",
    #             contributors: ["name1", "name2", "nameN"]
    #         }

def parse_works_bulkdata(bulk_data):
    l = []
    for b in bulk_data["bulk"]:
        w = parse_work_entry(b["work"])
        l.append(w)

    return l

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Parser for ORCID-API Services. This program analyses JSON files similar to the returned by ORCID 2.0 API.')
    parser.add_argument("-p", "--publications", help="File/List of files with bulkdata from the 'works' endpoint", type=str, nargs='+', required=False)
    parser.add_argument("-i", "--profile", help="File with the json response from the 'orcid profile root' endpoint",
                        type=str, required=False)
    parser.add_argument('-o', '--output', help='Saves the output in the specified file in JSON.', default="stdout")

    args = parser.parse_args()
    #print(args)

    ret = {}

    if args.publications:
        ret["publications"] = []
        for fname in args.publications:
            with open(fname, "r") as f:
                d = json.load(f)
                ret["publications"].append(parse_works_bulkdata(d))

    if args.profile:
        with open(args.profile, "r") as f:
            personal_details = json.load(f)
            ret["profile"] = parse_personal_details(personal_details)

    if args.output == "stdout":
        print(ret)
    else:
        with open(args.output, "w") as f:
            f.write(json.dumps(ret, sort_keys=True, indent=3))
