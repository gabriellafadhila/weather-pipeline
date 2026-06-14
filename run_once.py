# Gabriella Fadhilatus Awanda - Cetta Technical Test

import requests
import gspread
import os
import json
from datetime import datetime, timezone, timedelta
from google.oauth2.service_account import Credentials

WIB = timezone(timedelta(hours=7))

# ambil config dari environment variables (GitHub Secrets)
WEATHERSTACK_API_KEY = os.environ["WEATHERSTACK_API_KEY"]
SPREADSHEET_ID       = os.environ["SPREADSHEET_ID"]
GCP_CREDENTIALS      = os.environ["GCP_CREDENTIALS"]
CITY                 = "Malang"
SHEET_NAME           = "Weather Data"


def connect_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_info = json.loads(GCP_CREDENTIALS)
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)

    try:
        ws = sheet.worksheet(SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=SHEET_NAME, rows=1000, cols=15)

    return ws


def fetch_weather():
    url = "http://api.weatherstack.com/current"
    params = {
        "access_key": WEATHERSTACK_API_KEY,
        "query": CITY,
        "units": "m"
    }

    res = requests.get(url, params=params)
    data = res.json()

    if "error" in data:
        raise Exception(f"API error: {data['error']['info']}")

    cur = data["current"]
    loc = data["location"]

    return {
        "timestamp": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
        "city": loc["name"],
        "date": loc["localtime"].split(" ")[0],
        "local_time": loc["localtime"].split(" ")[1],
        "temperature_c": cur["temperature"],
        "feels_like_c": cur["feelslike"],
        "description": cur["weather_descriptions"][0],
        "humidity_pct": cur["humidity"],
        "wind_speed_kmh": cur["wind_speed"],
        "cloud_cover_pct": cur["cloudcover"],
        "pressure_mb": cur["pressure"],
        "uv_index": cur["uv_index"],
        "air_quality": cur.get("air_quality", {}).get("us-epa-index", "N/A")
    }


def save_to_sheets(ws, data):
    if ws.cell(1, 1).value is None:
        headers = [
            "Timestamp", "City", "Date", "Local Time",
            "Temperature (°C)", "Feels Like (°C)", "Description",
            "Humidity (%)", "Wind Speed (km/h)", "Cloud Cover (%)",
            "Pressure (hPa)", "UV Index", "Air Quality (US EPA)"
        ]
        ws.append_row(headers)

    row = [
        data["timestamp"], data["city"], data["date"], data["local_time"],
        data["temperature_c"], data["feels_like_c"], data["description"],
        data["humidity_pct"], data["wind_speed_kmh"], data["cloud_cover_pct"],
        data["pressure_mb"], data["uv_index"], data["air_quality"]
    ]
    ws.append_row(row)
    print(f"Data tersimpan: {data['timestamp']} | {data['temperature_c']}°C, {data['description']}")


if __name__ == "__main__":
    print(f"Pipeline jalan: {datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S')} WIB")
    try:
        ws = connect_sheets()
        data = fetch_weather()
        save_to_sheets(ws, data)
    except Exception as e:
        print(f"Error: {e}")
        raise