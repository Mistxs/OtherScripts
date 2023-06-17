import requests
import json
import datetime
now = datetime.datetime.now()
import random
from config import headers

salon_id = 100646


url = f"https://api.yclients.com/api/v1/storage_operations/operation/{salon_id}"

payload = json.dumps({
  "type_id": 1,
  "master_id": 1925162,
  "client": {
    "id": 177103335
  },
  "storage_id": 1119155,
  "date": str(now),
  "goods_transactions": [
    {
      "type_id": 1,
      "good_id": 14714750,
      "amount": 1,
      "cost_per_unit": 22950,
      "cost": 22950,
      "good_special_number": str(random.randint(700000,700500)),
      "good": {
        "good_id": 14714750,
        "id": 14714750,
        "cost": 22950,
        "loyalty_abonement_type_id": 215877,
        "loyalty_certificate_type_id": 0,
        "loyalty_allow_empty_code": 0
      }
    }
  ]
})

response = requests.request("POST", url, headers=headers, data=payload).json()

#получаем номер документа и сумму к оплате из данного запроса для последующего запроса на создание продажи
document = response["data"]["document_id"]
amount = response["data"]["goods_transactions"][0]["cost"]



#создаем второй запрос на продажу
url2 = f"https://api.yclients.com/api/v1/company/{salon_id}/sale/{document}/payment"

payload = json.dumps({
  "payment": {
    "method": {
      "slug": "account",
      "account_id": 1075226 #указываем кассу
    },
    "amount": amount #забрали сумму из прошлого запроса
  }
})


response = requests.request("POST", url2, headers=headers, data=payload).json()
