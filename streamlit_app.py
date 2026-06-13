import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime

# page config
st.set_page_config(
    page_title="Cuaca Malang",
    page_icon="🌤️",
    layout="centered"
)

# ── koneksi ke Google Sheets via Streamlit Secrets ──────────
@st.cache_resource
def connect_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    client = gspread.authorize(creds)
    return client

def load_data():
    client = connect_sheets()
    sheet = client.open_by_key(st.secrets["spreadsheet"]["id"])
    ws = sheet.worksheet("Weather Data")
    data = ws.get_all_records()
    df = pd.DataFrame(data)
    return df


# ── UI ───────────────────────────────────────────────────────
st.title("🌤️ Dashboard Cuaca Malang")
st.caption("Data diambil otomatis dari weatherstack.com · Update jam 00:38 & 12:38")

# tombol refresh
if st.button("🔄 Refresh Data"):
    st.cache_resource.clear()

# load data
with st.spinner("Mengambil data dari Google Sheets..."):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
        st.stop()

if df.empty:
    st.warning("Belum ada data di spreadsheet.")
    st.stop()

# ambil data terbaru
latest = df.iloc[-1]

# ── CURRENT WEATHER CARD ─────────────────────────────────────
st.subheader("📍 Kondisi Terkini")

col1, col2 = st.columns([1, 1])

with col1:
    st.metric("🌡️ Suhu", f"{latest['Temperature (°C)']}°C",
              f"Feels like {latest['Feels Like (°C)']}°C")
    st.metric("💧 Humidity", f"{latest['Humidity (%)']}%")
    st.metric("🌬️ Wind Speed", f"{latest['Wind Speed (km/h)']} km/h")

with col2:
    st.metric("☁️ Cloud Cover", f"{latest['Cloud Cover (%)']}%")
    st.metric("🔵 Pressure", f"{latest['Pressure (hPa)']} hPa")
    st.metric("☀️ UV Index", f"{latest['UV Index']}")

st.info(f"**{latest['Description']}** · {latest['City']} · {latest['Timestamp']}")

st.divider()

# ── RIWAYAT CHART ────────────────────────────────────────────
st.subheader("📈 Riwayat Cuaca")

# konversi timestamp
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df = df.sort_values("Timestamp")

tab1, tab2, tab3 = st.tabs(["🌡️ Suhu", "💧 Humidity", "🌬️ Wind Speed"])

with tab1:
    st.line_chart(df.set_index("Timestamp")["Temperature (°C)"])

with tab2:
    st.line_chart(df.set_index("Timestamp")["Humidity (%)"])

with tab3:
    st.line_chart(df.set_index("Timestamp")["Wind Speed (km/h)"])

st.divider()

# ── TABEL RIWAYAT ────────────────────────────────────────────
st.subheader("📋 Tabel Riwayat")

show_cols = ["Timestamp", "Temperature (°C)", "Feels Like (°C)",
             "Description", "Humidity (%)", "Wind Speed (km/h)",
             "Pressure (hPa)", "UV Index"]

st.dataframe(
    df[show_cols].sort_values("Timestamp", ascending=False).reset_index(drop=True),
    use_container_width=True
)

st.caption(f"Total data: {len(df)} record · Terakhir update: {latest['Timestamp']}")
