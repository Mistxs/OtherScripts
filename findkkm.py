import requests
import datetime
from config import headers

now = datetime.date.today()

salon_id = 232685
date = "2023-02-17"
enddate = "2023-05-23"

def get_kkm_id(salon_id,date, enddate):
    kkm = []
    docs = []
    url = f"https://api.yclients.com/api/v1/kkm_transactions/{salon_id}?start_date={date}&end_date={enddate}&editable_length=1000"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    pretty_response = response.json()
    print(pretty_response)
    for i in range(len(pretty_response["data"])):
        if pretty_response["data"][i]["type"]["id"] == 0 and pretty_response["data"][i]["status"]["id"] == 1:
            kkm.append(pretty_response["data"][i]["id"])
            docs.append(pretty_response["data"][i]["document_id"])

    print(f"KKM: {len(kkm)},  {kkm}")
    print(f"DOC: {len(docs)}, {docs}")

    temp = []

    for x in docs:
        if x not in temp:
            temp.append(x)
    docs = temp

    print(f"NEWDOC: {len(docs)}, {docs}")

    print(f'''
UPDATE documents SET bill_print_status = 1 WHERE id in ({', '.join(map(str, docs))});
UPDATE kkm_transactions SET status = 3 WHERE id in ({', '.join(map(str, kkm))});
''')

get_kkm_id(salon_id, date, enddate)
