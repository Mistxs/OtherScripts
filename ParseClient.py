import datetime
import json
import math

import requests

user_token = ""
salon_id = [543449]
stdate = "2000-01-01"
enddate = datetime.date.today()
card_type = 33439
dataset = [{}]
clid = []
recdata = []
phones = []

def parseclient(salon, page):

    url = f"https://api.yclients.com/api/v1/company/{salon}/clients/search"

    payload = json.dumps({
      "page": page,
      "page_size": 200,
      "fields": [
        "id",
        "name",
        "phone"
      ]
    })
    headers = {
      'Accept': 'application/vnd.yclients.v2+json',
      'Content-Type': 'application/json',
      'Authorization': user_token
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    pretty_response = response.json()
    global clid
    global phones
    total_count = pretty_response["meta"]["total_count"]
    iterations = math.ceil(total_count/200)
    # print(iterations)

    for i in range(len(pretty_response["data"])):
        clid.append(pretty_response["data"][i]["id"])
        phones.append(pretty_response["data"][i]["phone"])
    print(len(clid))
    print(clid)
    print(response.text)
    return iterations

for x in range(len(salon_id)):
    page = 1
    it = parseclient(salon_id[x],page)
    for i in range(2,it+1):
        parseclient(salon_id[x],i)
    dataset[-1]["salon"] = salon_id[x]
    dataset[-1]["clid"] = clid
    dataset[-1]["phone"] = phones
    clid = []
    phones = []
    dataset.append({})