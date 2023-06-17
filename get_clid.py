import requests
import json
from config import headers

with open('input.csv', 'r') as file:
    salon_id = file.readline().strip()
    delta_ch = int(file.readline().strip())

with open('clients.csv', 'r') as file:
    cli_array = [row.strip() for row in file]

url = f"https://api.yclients.com/api/v1/company/{salon_id}/clients/search"


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
    response = requests.request("POST", f"{url}", headers=headers, data=payload)
    request_data = response.json()
    if int(len((request_data["data"])) > 0):
        return request_data["data"][0]["id"]


def get_cli_id(cli_array):
    cli_id = []
    for i in range(0, len(cli_array)):
        ch_id = api_run(cli_array[i])
        if ch_id is not None:
            cli_id.append(ch_id)
    return cli_id

print(get_cli_id(cli_array))
