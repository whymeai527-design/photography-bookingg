📸 PANDUAN DEPLOY FLASK DI RENDER.COM (Bahasa Melayu)

Langkah-langkah untuk deploy projek Flask anda di Render.com:

1️⃣ Struktur Folder (pastikan sama macam ini)
-------------------------------------------------
photography_booking/
│
├── app.py
├── requirements.txt
├── render.yaml
├── templates/
└── static/

2️⃣ Upload ke GitHub
-------------------------------------------------
1. Log masuk ke GitHub
2. Buat repo baharu (contoh: photography_booking)
3. Upload semua fail projek anda ke repo itu

3️⃣ Deploy di Render.com
-------------------------------------------------
1. Log masuk ke https://render.com
2. Klik "New" → "Web Service"
3. Sambung akaun GitHub anda dan pilih repo projek ini
4. Isi maklumat berikut:
   • Build Command: pip install -r requirements.txt
   • Start Command: gunicorn app:app
5. Klik “Deploy Web Service”

4️⃣ Selepas deploy berjaya:
-------------------------------------------------
Anda akan dapat URL seperti ini:
   🌐 https://photography-booking.onrender.com

5️⃣ Muat naik database manual (jika perlu)
-------------------------------------------------
Jika menggunakan SQLite (bookings.db):
- Upload fail 'bookings.db' secara manual menggunakan Render Shell atau FTP.

Selesai! 🚀
