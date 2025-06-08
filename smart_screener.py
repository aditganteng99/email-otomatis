
import yfinance as yf
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os

# Konfigurasi email
EMAIL_PENGIRIM = "m.aldek.saputra08@gmail.com"
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_PENERIMA = "m.aldek.saputra08@gmail.com"

# Ambil daftar saham IDX secara otomatis (contoh fallback jika real list gagal)
def get_saham_list():
    try:
        df = pd.read_html("https://www.idx.co.id/Portals/0/StaticData/ListedCompanies/idx_lq45.xls")[0]
        return df["Kode Saham"].dropna().astype(str).apply(lambda x: x + ".JK").tolist()
    except:
        return ["ANTM.JK", "BBCA.JK", "TLKM.JK", "ADRO.JK", "MDKA.JK"]

saham_list = get_saham_list()
modal = 10_000_000
hasil = []

for kode in saham_list:
    try:
        df = yf.Ticker(kode).history(period="7d", interval="1d")
        df_intraday = yf.Ticker(kode).history(period="1d", interval="5m")
        if df.empty or df_intraday.empty: continue

        close = df["Close"]
        open_now = df_intraday["Open"].iloc[-1]
        close_now = df_intraday["Close"].iloc[-1]
        volume_now = df["Volume"].iloc[-1]
        avg_volume = df["Volume"].rolling(5).mean().iloc[-1]

        ma5 = close.rolling(5).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]

        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean().iloc[-1]
        avg_loss = loss.rolling(14).mean().iloc[-1]
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs)) if rs != 0 else 100

        if close_now > open_now and ma5 > ma20 and rsi < 60 and volume_now > avg_volume:
            lot = max(int(modal // (close_now * 100)), 1)
            tp = close_now * 1.03
            sl = close_now * 0.98
            est_profit = int((tp - close_now) * lot * 100)
            hasil.append(f"{kode.replace('.JK','')} | Harga: {round(close_now)} | Lot: {lot} | TP: {round(tp)} | SL: {round(sl)} | RSI: {int(rsi)} | Est. Profit: Rp {est_profit:,}")
    except:
        continue

# Format email
tanggal = datetime.now().strftime("%d-%m-%Y %H:%M")
subject = f"[Smart Screener IDX] - {tanggal}"
body = "Saham dengan sinyal kombinasi teknikal:\n\n" + ("\n".join(hasil) if hasil else "Tidak ada sinyal pasti naik hari ini.")

# Kirim email
msg = MIMEMultipart()
msg["From"] = EMAIL_PENGIRIM
msg["To"] = EMAIL_PENERIMA
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_PENGIRIM, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
    print("Email berhasil dikirim.")
except Exception as e:
    print(f"Gagal kirim email: {e}")
