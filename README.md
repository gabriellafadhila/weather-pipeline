# Weather Pipeline - Malang
Gabriella Fadhilatus Awanda | Cetta Data Engineer Technical Test

Pipeline ini ngambil data cuaca Malang dari weatherstack.com dan nyimpen hasilnya ke Google Spreadsheet secara otomatis 2x sehari (00:38 dan 12:38).

Dashboard: https://weather-pipeline-malang.streamlit.app/

---

## Struktur File
```
case2_weather/
├── weather_pipeline.py   # script utama pipeline
├── run_once.py           # versi pipeline untuk GitHub Actions
├── config.py             # konfigurasi API key & spreadsheet
├── requirements.txt      # dependencies
└── README.md
```

---

## Konfigurasi

### 1. Weatherstack API Key
Daftar di weatherstack.com, copy API key dari dashboard, lalu isi di `config.py`:
```python
WEATHERSTACK_API_KEY = "api_key_kamu"
```

### 2. Google Service Account
- Buat project di console.cloud.google.com
- Enable Google Sheets API dan Google Drive API
- Buat Service Account, download file JSON, rename jadi `credentials.json`
- Simpan di folder yang sama dengan script

### 3. Google Spreadsheet
- Buat spreadsheet baru di Google Sheets
- Share ke email `client_email` yang ada di `credentials.json` (role: Editor)
- Copy Spreadsheet ID dari URL, isi di `config.py`:
```python
SPREADSHEET_ID = "spreadsheet_id_kamu"
```

---

## Cara Menjalankan

Install dependencies dulu:
```bash
pip install requests gspread google-auth schedule
```

Jalankan pipeline:
```bash
python weather_pipeline.py
```

Pipeline akan langsung fetch data sekali saat pertama dijalankan, lalu otomatis jalan lagi tiap 00:38 dan 12:38. Biarkan terminal tetap terbuka.

---

## Penjadwalan Otomatis (GitHub Actions)

Pipeline dijadwalkan via GitHub Actions sehingga berjalan otomatis tanpa perlu laptop menyala. Konfigurasi ada di `.github/workflows/weather_schedule.yml`.

Tambahkan 3 secrets di GitHub repo (Settings → Secrets → Actions):
- `WEATHERSTACK_API_KEY` → API key dari weatherstack.com
- `SPREADSHEET_ID` → ID Google Spreadsheet
- `GCP_CREDENTIALS` → seluruh isi file `credentials.json`

---

## Penjadwalan Manual

**Windows (Task Scheduler)**
1. Buka Task Scheduler, klik "Create Basic Task"
2. Set trigger: Daily jam 00:38
3. Action: jalankan `python`, argument: path ke `weather_pipeline.py`
4. Ulangi untuk jam 12:38

**Mac/Linux (Cron)**
```bash
crontab -e
```
Tambahkan:
```
38 0  * * * python /path/to/weather_pipeline.py
38 12 * * * python /path/to/weather_pipeline.py
```

---

## Catatan
- Jangan upload `credentials.json` ke GitHub atau tempat publik
- API key di `config.py` juga bersifat rahasia