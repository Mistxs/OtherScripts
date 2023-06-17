# В кое то веке соберу одно красивое приложение. Необходимо для переначисления кэшбека из-за бага, где в статусе визита
# лояльность не считалась. Алгоритм - задается период поиска, и указывается филиал. Далее программа находит все визиты
# за период, а также все транзакции лояльности за этот же период.
# Далее исключаем из первого поиска визитов, те, в которых были транзакции лояльности, и по списку, который получаем
# переставляем статусы (attendance) на подтвердил (2) и затем пришел (1)

import json
import requests
import pandas as pd
from tqdm import tqdm

from config import headers

# Входные данные
token = "u8xzkdpkgfc73uektn64, 535f6d732fd25df55c57e5ce35f3da99"


# salon_id = input("Введите ID филиала ", )
# chain_id = input("Введите ID сети ", )
# startdate = input("Введите дату начала периода в формате YYYY-MM-DD ", )
# enddate = input("Введите дату окончания периода в формате YYYY-MM-DD ", )

salon_id = 116064
chain_id = 95783
startdate = '2023-03-02'
enddate = '2023-03-25'
logs = [{}]

# Поиск всех записей за период
def findallrec():
    url = f"https://api.yclients.com/api/v1/records/{salon_id}?start_date={startdate}&end_date={enddate}&include_finance_transactions=1&page=1&count=1000"
    payload = ""
    response = requests.request("GET", url, headers=headers, data=payload)
    response_pretty = response.json()
    if response_pretty["meta"]["total_count"] > 1000:
        return "Error"
    return response_pretty["data"]

# Поиск всех транзакций с типом [2] - Начисление по программе лояльности
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
    if pr_response["meta"]["count"] == 1000:
        return "Error"
    return pr_response["data"]

#Поиск визитов
def parserdata(data, key):
    visit_ids = []
    for i in range(len(data)):
        if key == 1: # ключ нужен для того, чтобы понимать, что просматриваем - записи, или транзакции лояльности
            if data[i]["client"] != None and data[i]["paid_full"] == 1:
                if len(data[i]["client"]["phone"]) != 0:
                    visit_ids.append(data[i]["visit_id"])
        if key == 2:
            visit_ids.append(data[i]["visit_id"])
    return visit_ids



#Читаем данные по визиту
def read_visit(visit_id):
    url = f"https://api.yclients.com/api/v1/visits/{visit_id}"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    request_data = response.json()
    visit_data = request_data["data"]
    return visit_data["records"][0]["id"]

def read_record(rec_id):
    url = f"https://api.yclients.com/api/v1/record/{salon_id}/{rec_id}"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()["data"]

def put_record(rec_id, data,i):

    #пишем все в список чтобы потом проверить работу
    logs[i]["Step"] = i
    logs[i]["Record num"] = rec_id
    logs[i]["Visit num"] = data["visit_id"]

    url = f"https://api.yclients.com/api/v1/record/{salon_id}/{rec_id}"
    # print(f"Step: {i}, Record num: {rec_id}")
    true_attendance = data["attendance"]
    data["attendance"] = 2
    data["save_if_busy"] = True
    payload = json.dumps(data)
    response = requests.request("PUT", url, headers=headers, data=payload)
    logs[i]["Success"] = response.json()["success"]
    logs[i]["Attendance 2 result"] = response.text

    # print(response.text)

    data["attendance"] = 1
    payload = json.dumps(data)
    response = requests.request("PUT", url, headers=headers, data=payload)
    logs[i]["Attendance 1 result"] = response.text
    # print(response.text)

    data["attendance"] = true_attendance
    payload = json.dumps(data)
    response = requests.request("PUT", url, headers=headers, data=payload)
    logs[i]["Attendance true result"] = response.text
    # print(response.text)

def check_result(rec_id, vis_id, k):
    url = f"https://api.yclients.com/api/v1/visit/details/{salon_id}/{rec_id}/{vis_id}"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload).json()
    # pprint.pprint(response["data"])
    if response["data"]["loyalty_transactions"]:
        for i in range(len(response["data"]["loyalty_transactions"])):
            if response["data"]["loyalty_transactions"][i]["type_id"] == 2:
                amount = response["data"]["loyalty_transactions"][i]["amount"]
                date = response["data"]["loyalty_transactions"][i]["created_date"]
                trid = response["data"]["loyalty_transactions"][i]["id"]
                logs[k]["Result"] = f"Баллы начислены. Сумма {amount}, дата начисления: {date}, id транзакции лояльности: {trid}"

def save_db():
        f = open('logs.json', 'a')
        out = json.dumps(logs, ensure_ascii=False)
        df = pd.json_normalize(logs)
        df.to_excel('data.xlsx', index=False)
        f.write(", \n ")
        f.write(f'{out}')
        f.write("\n")
        f.close()

#Запуск программы
def start():
    input("ПРОВЕРЬ НАСТРОЙКИ УВЕДОМЛЕНИЙ КАРТ!!!!", )
    dataset = findallrec() # сохраняем данные по всем записям
    transaction_data = findalltrans()  # сохраняем данные по всем транзакциям лояльности
    if dataset == "Error" or transaction_data == "Error":
        print("Пожалуйста, укажите меньший период поиска, записей больше 1000")
        global startdate
        global enddate
        startdate = input("Введите дату начала периода в формате YYYY-MM-DD ", )
        enddate = input("Введите дату окончания периода в формате YYYY-MM-DD ", )
        start()
    else:
        visits = parserdata(dataset, 1) # отбираем визиты из полученных в dataset записях
        print(f"Получено визитов: {len(visits)}")

        loyalty_visits = parserdata(transaction_data, 2) # отбираем визиты из лояльности
        print(f"Получено визитов из лояльности: {len(loyalty_visits)}")

        visits = [x for x in visits if x not in loyalty_visits] # на выходе получили визиты, которые нужно обновить
        print(f"Визиты ({len(visits)})шт, в которых нет по какой то причине начисления кэшбека: \n {visits}")
        rec = []

    # Проходим по каждому визиту и запускаем функцию чтения / изменения данных
        for i in tqdm(range(len(visits))):
            v_rec = read_visit(visits[i])  # забираем данные визита
            rec.append(v_rec)
            data = read_record(v_rec)
            put_record(v_rec, data, i)
            logs[i]["link"] = f"https://yclients.com/timetable/{salon_id}#main_date=2023-03-31&open_modal_by_record_id={v_rec}&mode=1"
            # check_result(v_rec,visits[i],i)
            logs.append({})
        save_db()
        print(f"Записи этих визитов: \n {rec}")

        for j in range(len(rec)):
            print(f"https://yclients.com/timetable/{salon_id}#main_date=2023-03-31&open_modal_by_record_id={rec[j]}&mode=1")
        input("Вы великолепны. Файл с результатами создан в этой же директории (data.xlsx)", )

        # тестовые демоданные (запускать либо цикл выше, либо с этими параметрами)
        # v_rec = read_visit(490496256)  # забираем данные визита
        # data = read_record(v_rec)
        # put_record(v_rec,data,0)

start()


