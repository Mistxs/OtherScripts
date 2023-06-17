import requests
import json
from datetime import datetime

from config import headers

with open('output.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('input.csv', 'r') as file:
    group_id = file.readline().strip()

url = f"https://api.yclients.com/api/v1/chain/{group_id}/loyalty/transactions"


def get_transaction(visit_id, visit_date, date_before):
    payload = json.dumps({
        "created_after": date_before,
        "created_before": visit_date,
        "count": "1000",
        "visit_ids": [
            visit_id
        ]
    })
    response = requests.request("GET", f"{url}", headers=headers, data=payload)
    request_data = response.json()
    return request_data


def find_type_loyal(transaction): #ищу косячные списания, которых быть не должно (где type=3)
    return_dict = {}
    summ = 0
    for i in range(0, len(transaction["data"])):
        print(transaction["data"][i]["type_id"])
        if transaction["data"][i]["type_id"] == 3:
            print("ALARM: ", transaction["data"][i]["visit_id"], transaction["data"][i]["created_date"],
                  transaction["data"][i]["type_id"], transaction["data"][i]["amount"])
            summ += transaction["data"][i]["amount"]
            return_dict["visit_id"] = transaction["data"][i]["visit_id"]
            return_dict["type_id"] = transaction["data"][i]["type_id"]
            return_dict["summ"] = summ
            return_dict["card_id"] = transaction["data"][i]["card_id"]
            return_dict["data"] = datetime.strptime(transaction["data"][i]["created_date"],
                                                    "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d")
    print(return_dict)
    if len(return_dict) != 0:
        return return_dict


def find_lost_burning(visit_date, date_before, card_id):
    payload = json.dumps({
        "created_after": date_before,
        "created_before": visit_date,
        "count": "1000",
        "types": ["7"]
    })

    response = requests.request("GET", f"{url}", headers=headers, data=payload)
    request_data = response.json()
    checker = 1
    if len(request_data["data"]) == 0:
        checker = 1


    for i in range(0, len(request_data["data"])):
        if request_data["data"][i]["card_id"] == card_id:
            print("ALL RIGHT, step N: ", i)
            checker = 0
            break

    return checker





#  шайтан цикл для передачи output.json в метод поиска лояльности
final_return = []
card_id = 1
for i in range(0, len(data)):
    for j in range(0, len(data[i]["visit_error_meta"])):
        visit_id = data[i]["visit_error_meta"][j]["id"]
        visit_date = data[i]["visit_error_meta"][j]["date"]
        date_before = data[i]["visit_error_meta"][j]["date_before"]
        transaction_data = (get_transaction(visit_id, visit_date, date_before))  # выполняется функция поиска транзакций
        if transaction_data["data"][0]["card_id"]:
            card_id = transaction_data["data"][0]["card_id"]
        print()
        print()
        lost_burn = find_lost_burning(visit_date, date_before, card_id)
        if lost_burn:
            print("WRONG OPERATION! Visit:", visit_id, "clid:", data[i]["clid"], "card_id:", card_id, "visit_date:", visit_date,
                  "before_date:", date_before)

            # calc_summ (transaction_data)
        #
        # find_type3 = find_type_loyal(transaction_data)
        # if find_type3 is not None:
        #     final_return.append(find_type3)
        # print(lost_burn)

f = open('output_final.json', 'w')
f.write("")
f.close()

with open('output_final.json', 'a') as outfile:
    json.dump(final_return, outfile)
f = open('output_final.json', 'a')
f.write('\n')
f.close()
