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

# Daftar saham IDX yang dianalisis
saham_list = ["ANTM.JK", "BBCA.JK", "TLKM.JK", "ADRO.JK", "MDKA.JK"]
modal = 10_000_000
hasil = []

# Ambil data dan analisis sinyal pasti naik
for kode in saham_list:
    try:
        df = yf.Ticker(kode).history(period="1d", interval="5m")
        if df.empty:
            continue
        harga = df["Close"].iloc[-1]
        ma5 = df["Close"].rolling(5).mean().iloc[-1]
        lot = max(int(modal // (harga * 100)), 1)
        tp = harga * 1.03
        sl = harga * 0.98
        profit = (tp - harga) * lot * 100
        sinyal = "📈 PASTI NAIK" if harga > ma5 else "-"
        if sinyal == "📈 PASTI NAIK":
            hasil.append(f"{kode.replace('.JK','')} | Harga: {round(harga)} | Lot: {lot} | TP: {round(tp)} | SL: {round(sl)} | Est. Profit: Rp {int(profit):,}")
    except Exception as e:
        continue

# Format isi email
tanggal = datetime.now().strftime("%d-%m-%Y %H:%M")
subject = f"Sinyal Saham PASTI NAIK - {tanggal}"
if hasil:
    body = "Saham dengan sinyal PASTI NAIK hari ini:\n\n" + "\n".join(hasil)
else:
    body = "Tidak ada sinyal pasti naik hari ini."

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
