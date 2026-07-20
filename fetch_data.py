import requests
import json
import os

API_URL = "https://theverticaltribe.com/peak-data/peaks.json"
OUTPUT_PATH =  "data/raw_peaks.json"

def fetch_and_save():

    response =  requests.get(API_URL)
    response.raise_for_status()
    data = {"data": response.json()["peaks"]}

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Data saved successfully!")

if __name__ == "__main__":
    fetch_and_save()
