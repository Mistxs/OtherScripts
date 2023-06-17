import math
import json
import requests
from math import ceil
import pprint
import datetime
from config import headers


salon_id = [309926]
stdate = "2000-01-01"
enddate = datetime.date.today()
card_type = 33439
dataset = [{}]
clid = []
recdata = []
phones = []

usertoken = ""

def findrec(salon, client):
    url = f"https://api.yclients.com/api/v1/records/{salon}?count=100&client_id={client}"
    payload = ""
    response = requests.request("GET", url, headers=headers, data=payload)
    request_data = response.json()
    rdata = []
    for i in range(len(request_data["data"])):
        if request_data["data"][i]["attendance"] == 1:
            rdata = request_data["data"]
            break
    return rdata





def delete(salon, id):
    url = f"https://api.yclients.com/api/v1/loyalty/cards/{salon}/{id}"
    payload = {}
    response = requests.request("DELETE", url, headers=headers, data=payload)
    print(response.text)

def create(salon, number, phone):
    url = f"https://api.yclients.com/api/v1/loyalty/cards/{salon}"
    payload = json.dumps({
        "loyalty_card_number": f"{number}",
        "loyalty_card_type_id": card_type,
        "phone": f"{phone}"
    })
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def getcard(clid,phone):
    url = f"https://api.yclients.com/api/v1/loyalty/client_cards/{clid}"
    payload = {}
    number = 0
    id = 0
    response = requests.request("GET", url, headers=headers, data=payload)
    responsepretty = response.json()
    # print(responsepretty)
    for i in range(len(responsepretty["data"])):
        if responsepretty["data"][i]["type_id"] == card_type:
            number = responsepretty["data"][i]["number"]
            id = responsepretty["data"][i]["id"]
    print(number, id)
    delete(salon_id[0], id)
    create(salon_id[0], number, phone)


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
      'Authorization': usertoken
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

# это рабочая штука, забрать все clid и salon_id на выходе словарь {"salon" : [clid]}
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

# print(len(data[0]["phone"]))

# print(dataset)
# print(dataset)
print(f'длина {len(dataset[0]["clid"])}')
cnt = 0
for i in range(len(dataset[0]["clid"])):
    print(f"Step: {i+1}")
    print(dataset[0]["phone"][i])
    getcard(dataset[0]["clid"][i],dataset[0]["phone"][i])
    cnt += 1
print(f"перевыпущено карт: {cnt}")
# getcard(174016687,79933504416)

