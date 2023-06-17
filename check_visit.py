import pprint
import requests
import json
from datetime import datetime
from config import headers

url = "https://api.yclients.com/api/v1/records"

with open('input.csv', 'r') as file:
    group_id = file.readline().strip()
    salon_id = file.readline().strip()
    delta_ch = int(file.readline().strip())
    # cli_array = [row.strip() for row in file]
    id_array = [row.strip() for row in file]


cli_url = f"https://api.yclients.com/api/v1/company/{salon_id}/clients/search"


# получаем один client id через API
def api_run(client_phone):
    payload = json.dumps({
        "filters": [
            {
                "type": "quick_search",
                "state": {
                    "value": f"{client_phone}"
                }
            }
        ]
    })


    response = requests.request("POST", f"{cli_url}", headers=headers, data=payload)
    request_data = response.json()
    if int(len((request_data["data"])) > 0):
        return request_data["data"][0]["id"]


# запускаем парсинг всех клиентов, и возвращаем массив с client_id, который потом отдадим в get_visit()
def get_cli_id(cli_array):
    cli_id = []
    for i in range(0, len(cli_array)):
        print(cli_array[i])
        ch_id = api_run(cli_array[i])
        print(ch_id)
        if ch_id is not None:
            cli_id.append(ch_id)
    return cli_id


def get_visit(salon_id, client_id):
    payload = json.dumps({
        "client_id": client_id
    })
    response = requests.request("GET", f"{url}/{salon_id}", headers=headers, data=payload)
    request_data = response.json()
    return request_data


# парсим то что получили в функции get_visit

def check_visit(data):
    total_rec = len(data['data'])  # длина массива, сколько всего записей, дальше пойдем циклом
    record_date = []
    for i in range(0, total_rec):
        if data['data'][i]["paid_full"] != 0:
            rec_id = data['data'][i]['date']
            record_date.append(rec_id)  # закидываем записи в массив record_date
    return record_date


# массив с датами есть, теперь надо проверить дельту. мог в той же функции сделать, но меня прикалывает все по разным функциям пихать

def calc_delta(array):
    print()
    dateFormatter = "%Y-%m-%d %H:%M:%S"
    err_count = []
    for i in range(0, len(array) - 1):
        first_date_count = int(datetime.strptime(array[i], dateFormatter).strftime("%j"))
        second_date_count = int(datetime.strptime(array[i + 1], dateFormatter).strftime("%j"))
        delta = first_date_count - second_date_count
        print(f"Step {i}: {array[i + 1]} - {array[i]} = {delta}")
        if delta > delta_ch:
            print("FAILED")
            err_count.append(i)
    return err_count


# Вернем значения visit id в которых есть ошибка


def visit_error(array_err, rec_data):
    total_rec = len(array_err)  # длина массива, сколько всего записей, дальше пойдем циклом
    visit_array = []
    for i in range(0, total_rec):
        visit_data = {}
        rec_id = rec_data['data'][array_err[i]]['visit_id']
        date_rec = datetime.strptime(rec_data['data'][array_err[i]]['date'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        date_bfr = datetime.strptime(rec_data['data'][array_err[i]+1]['date'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        visit_data["id"] = rec_id
        visit_data["date"] = date_rec
        visit_data["date_before"] = date_bfr
        visit_array.append(visit_data)
    return visit_array


def start_check_client(client_id):
    recdata = get_visit(salon_id, client_id)  # запускаем поиск записей, возращается массив всех записей
    pprint.pprint(recdata)

    get_date = check_visit(recdata)  # запускаем поиск дат из массива recdata, возвращается массив дат
    print("get_date: ", get_date)

    error_log = calc_delta(
        get_date)  # запускаем поиск разницы в датах, возвращается массив с ID визитов, где дельта больше нужного
    print("calc_delta(): ", error_log)

    ret_visit = visit_error(error_log, recdata)  # запускаем поиск ID ошибочных визитов
    print("visit_error(): ", ret_visit)

    pretty_return = {}
    print("Pretty return: ")
    if len(ret_visit) > 0:
        pretty_return["clid"] = client_id
        pretty_return["visit_error_meta"] = ret_visit
        pprint.pprint(pretty_return)
    return pretty_return


f = open('output.json', 'w')
f.write("")
f.close()


# id_array = get_cli_id(cli_array)

new_return = []
for i in range(0, len(id_array)):
    data = start_check_client(id_array[i])
    if len(data) > 0:
        new_return.append(data)

print(new_return)

with open('output.json', 'a') as outfile:
    json.dump(new_return, outfile)
f = open('output.json', 'a')
f.write('\n')
f.close()