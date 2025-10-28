import sqlite3

# Sambung ke database
conn = sqlite3.connect('bookings.db')
cursor = conn.cursor()

# Semak sama ada column 'note' dah wujud
cursor.execute("PRAGMA table_info(bookings)")
columns = [col[1] for col in cursor.fetchall()]

if 'note' not in columns:
    cursor.execute("ALTER TABLE bookings ADD COLUMN note TEXT")
    print("✅ Lajur 'note' berjaya ditambah.")
else:
    print("ℹ️ Lajur 'note' sudah wujud, tak perlu tambah lagi.")

conn.commit()
conn.close()
