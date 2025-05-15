import requests
import time
import json
import os

def fetch_models_for_make(make_id):
    url = "https://www.carqueryapi.com/api/0.3/"
    params = {"cmd": "getModels", "make": make_id}
    headers = {
        "User-Agent": "Mozilla/5.0 ...",
        "Accept": "application/json"
    }
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    data = resp.json()
    if 'error' in data:
        print(f"[ERROR] {data['error']} (make_id={make_id})")
        return None
    return data.get('Models', [])

def main():
    # Сюди зберігай, що вже зібрав
    done_file = "fetched_makes.json"
    done = set()
    if os.path.exists(done_file):
        with open(done_file, "r") as f:
            done = set(json.load(f))

    # makes = ...  # список усіх make_id (отримуй окремо!)
    makes = ["honda", "bmw", "audi", ...]  # твій список

    for i, make_id in enumerate(makes):
        if make_id in done:
            continue
        models = fetch_models_for_make(make_id)
        if models is None:
            print(f"!!! Заблокували під час {make_id}, збережи прогрес і зміни IP/VPN!")
            break
        # Тут зберігай у свою базу!
        print(f"{make_id}: {len(models)} моделей")
        done.add(make_id)
        with open(done_file, "w") as f:
            json.dump(list(done), f)
        time.sleep(4)  # повільно!
        if i % 10 == 0:
            print("Пауза 1 хвилина для уникнення бана...")
            time.sleep(60)

if __name__ == "__main__":
    main()