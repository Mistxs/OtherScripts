import requests
import json
import pandas as pd
from config import headers

def gettransaction():
    url = "https://api.yclients.com/api/v1/chain/491886/loyalty/transactions"

    payload = json.dumps({
        "created_after": "2023-04-04",
        "created_before": "2023-04-29",
        "count": "1000"
    })
    response = requests.request("GET", url, headers=headers, data=payload).json()
    return response["data"]

def recinfo(rec):
    url = f"https://api.yclients.com/api/v1/record/365609/{rec}"
    response = requests.request("GET", url, headers=headers).json()
    return response["data"]["date"]

list = [{}]
data = gettransaction()
for i in range(len(data)):
    if data[i]["abonement_id"] == 5517111 and data[i]["type_id"] == 9:
        list[-1]["transaction_type"] = data[i]["type_id"]
        list[-1]["transaction_id"] = data[i]["id"]
        list[-1]["created"] = data[i]["created_date"]
        list[-1]["amount"] = data[i]["amount"]
        list[-1]["visit_id"] = data[i]["visit_id"]
        list[-1]["record_id"] = data[i]["item_record_id"]
        list[-1]["record_date"] = recinfo(data[i]["item_record_id"])
        list[-1]["url"] = f"https://yclients.com/timetable/365609#main_date=2023-03-31&open_modal_by_record_id={data[i]['item_record_id']}&mode=1"

        list.append({})

print(len(list)-1)
print(list)
df = pd.json_normalize(list)
df.to_excel('loyalty2.xlsx', index=False)