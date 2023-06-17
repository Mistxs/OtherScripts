import pprint

import requests
import json
import datetime
from config import u_token


salon_id = 309926
chain_id = 290446

startdate = '2023-03-07'
enddate = '2023-03-24'
pretty_output = [{}]
data_list = [{}]
new_data_list = []
now = datetime.date.today()
services = {}
headers = {
    'Accept': 'application/vnd.yclients.v2+json',
    'Content-Type': 'application/json',
    'Authorization': u_token,
}

# собираем данные по услугам / категориям, чтобы потом искать их в записях
def getservices():
    global services
    url = f"https://api.yclients.com/api/v1/company/{salon_id}/services"
    payload = ""
    response = requests.request("GET", url, headers=headers, data=payload)
    response_pretty = response.json()
    for i in range(len(response_pretty["data"])):
        services[f'{response_pretty["data"][i]["id"]}'] = response_pretty["data"][i]["category_id"]
        # services["services"] = response_pretty["data"][i]["id"]
    print(f"Услуги: {services}")
    return response_pretty

def findallrec():

    url = f"https://api.yclients.com/api/v1/records/{salon_id}?start_date={startdate}&end_date={enddate}&include_finance_transactions=1&page=1&count=1000"
    payload = ""
    response = requests.request("GET", url, headers=headers, data=payload)
    response_pretty = response.json()
    return response_pretty

def parserdata(data):
    visit_ids = []
    clients = []
    phones = []
    for i in range(len(data)):
        # print(i, data[i]["client"])
        if data[i]["client"] != None:
            if len(data[i]["client"]["phone"]) != 0:
                clients.append(data[i]["client"]["id"])
                visit_ids.append(data[i]["visit_id"])
                phones.append(data[i]["client"]["phone"])
    print(visit_ids)
    print(clients)
    print(phones)
    print(len(visit_ids))
    return visit_ids

def checkcart(clients):
    url = f"https://api.yclients.com/api/v1/loyalty/cards/{clients}/{chain_id}/{salon_id}"
    global pretty_output
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json()
    if len(response_json['data']) == 0:
        return False
    else:
        return response_json["data"][0]["id"]

def findalltrans():

    url = f"https://api.yclients.com/api/v1/chain/{chain_id}/loyalty/transactions"

    payload = json.dumps({
        "created_after": f"{startdate}",
        "created_before": f"{enddate}",
        "types": [2],
        "count": 1000
    })
    response = requests.request("GET", url, headers=headers, data=payload)
    pr_response = response.json()
    return pr_response

def parserloyal(data):
    visit_ids = []
    for i in range(len(data)):
        visit_ids.append(data[i]["visit_id"])
    # print(visit_ids)
    return visit_ids

def parservisits(data): # выбираю данные по тем визитам которые не обнаружились в транзакциях лояльности в сети, чтобы дальше работать  с этим списком
    for i in range(len(data)):
        if data[i]["visit_id"] in visits:
            # print(data[i]["client"])
            services = []
            data_list[i]["client"] = data[i]["client"]["name"]
            data_list[i]["phone"] = data[i]["client"]["phone"]
            data_list[i]["doc_id"] = data[i]["documents"][0]["id"]
            for j in range(len(data[i]["services"])):
                services.append(data[i]["services"][j]["id"])
            data_list[i]["services"] = services
            data_list[i]["date"] = data[i]["date"]
            data_list[i]["paidstat"] = data[i]["paid_full"]
            data_list[i]["url"] = f"https://yclients.com/timetable/{salon_id}#main_date={now}&open_modal_by_record_id={data[i]['id']}"
        data_list.append({})

def calcpayment(docid,counter,paid):
    url = f"https://api.yclients.com/api/v1/company/{salon_id}/sale/{docid}"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    pr_response = response.json()
    paydata = pr_response["data"]["state"]["payment_transactions"]
    print(f'принт новый: {paydata}')
    summ = 0
    allsumm = 0
    for i in range(len(paydata)):
        if paydata[i]["sale_item_type"] == "service":
            summ += paydata[i]["amount"]
        allsumm += paydata[i]["amount"]
    print(f'Сумма оплаты за услуги: {summ}')
    print(f'Общая сумма: {allsumm}')
    print(counter)
    pretty_output[counter]["summ"] = summ
    # считаем кэшбек
    if paid <= 50000:
        pretty_output[counter]["cashback"] = summ*0.05
    if paid >50000 and paid<=100000:
        pretty_output[counter]["cashback"] = summ * 0.07
    if paid >100000:
        pretty_output[counter]["cashback"] = summ * 0.1
    return pr_response

def clientpaid(clid):
    url = f"https://api.yclients.com/api/v1/loyalty/client_cards/{clid}"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload).json()
    return response["data"][0]["paid_amount"]

def parsernew(data): #еще раз иду по этим визитам и проверяю, есть ли карта у клиента
    doc_id = []
    clphone = []
    # pprint.pprint(data[1])
    for i in range(len(data)):
        print(i)
        if data[i]["visit_id"] in visits:
            # print(data[i]["client"])
            pretty_output[i]["client"] = data[i]["client"]["name"]
            pretty_output[i]["clid"] = data[i]["client"]["id"]
            pretty_output[i]["phone"] = data[i]["client"]["phone"]
            pretty_output[i]["doc_id"] = data[i]["documents"][0]["id"]
            pretty_output[i]["url"] = f"https://yclients.com/timetable/{salon_id}#main_date=2023-03-02&open_modal_by_record_id={data[i]['id']}"
            if checkcart(data[i]["client"]["phone"]):
                print(f'Карта есть, думаем че дальше, клиент {data[i]["client"]["phone"]}')
                pretty_output[i]["status"] = "Карта есть, считаем сумму кэшбека"
                pretty_output[i]["card_id"] = checkcart(data[i]["client"]["phone"])
                pretty_output[i]["spent"] = clientpaid(data[i]["client"]["id"]) # смотрим на потраченную клиентом сумму
                calcpayment(data[i]["documents"][0]["id"], i, pretty_output[i]["spent"]) # вызов функции (важно)
                doc_id.append(data[i]["documents"][0]["id"])
                clphone.append(data[i]["client"]["phone"])
            elif checkcart(data[i]["client"]["phone"]) == False:
                print("Карты у клиента нет")
                pretty_output[i]["status"] = "Карты нет"
            # print(pretty_output)
        pretty_output.append({})
    return doc_id, clphone


getservices()
dataset = findallrec()
print(len(dataset["data"]))
transaction_data = findalltrans()

visits = parserdata(dataset["data"])
print(f"Получено визитов: {len(visits)}")

loyalty_visits = parserloyal(transaction_data["data"])
print(f"Получено визитов из лояльности: {len(loyalty_visits)}")

visits = [x for x in visits if x not in loyalty_visits]
print(f"Визиты ({len(visits)})шт, в которых нет по какой то причине начисления кэшбека: \n {visits}")

parservisits(dataset["data"])
data_list = [lst for lst in data_list if lst]


# for i in range(len(data_list)):
#     checkcart(data_list[i]["phone"], i)
#     pretty_output.append({})
#
# print(pretty_output)

doc_set, ph_set = parsernew(dataset["data"])
print(doc_set)
print(len(doc_set))


print(pretty_output)

pr_2 = [lst for lst in pretty_output if lst]
final = json.dumps(pr_2, ensure_ascii=False)
f = open('newlog.txt', 'a')
f.write("\n")
f.write(final)
f.close()