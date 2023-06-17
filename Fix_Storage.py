import requests
from flask import Flask
from flask import request
from datetime import datetime
from datetime import timedelta
import json

from config import headers


salon_id = 543449

import time

app = Flask(__name__)
ids = []

@app.route('/get', methods=['POST'])
def process_json():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        request_data = request.json
        if request_data["resource"] == "goods_operations_sale" and request_data["status"] == "create":
            check_hook(request_data)
        return '200'
    else:
        return 'Content-Type not supported!'

def update(doc_id,data):
    url = f"https://yclients.com/api/v1/storage_operations/documents/{salon_id}/{doc_id}"
    payload = json.dumps(data)
    print(payload)
    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.text)

def check_hook(data):
    # print(data)
    # print(data["data"]["online"])
    date = datetime.strptime(data["data"]["create_date"], '%Y-%m-%dT%H:%M:%S%z')
    print(date)
    print(date.hour)
    # Проверка, если время больше или равно 23, то запустить функцию
    if date.hour == 0:
        print("Время больше или равно 23 часам.")
        print(data)
        print(data["data"]["create_date"])
        newdate = date - timedelta(hours=2)
        new_date_string = newdate.strftime('%Y-%m-%d %H:%M:%S')
        data["data"]["create_date"] = new_date_string
        print("NEW DATE")
        print(data["data"]["create_date"])

        update(data["data"]["document_id"], data["data"])



if __name__ == '__main__':
    app.run()
