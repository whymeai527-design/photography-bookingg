from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'rahsia_admin_123'

DB_NAME = 'bookings.db'
MAX_BOOKING_PER_DAY = 3

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# ===============================
# DATABASE SETUP
# ===============================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    # Jadual bookings
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            phone TEXT NOT NULL,
            tarikh TEXT NOT NULL,
            pakej TEXT NOT NULL,
            note TEXT
        )
    """)

    # Jadual packages
    conn.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT UNIQUE NOT NULL,
            harga REAL NOT NULL
        )
    """)
    conn.commit()

    # Masukkan data default jika kosong
    rows = conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0]
    if rows == 0:
        default_packages = [
            ("Wedding Nikah Sanding", 1500),
            ("Wedding Nikah Sanding Dan Bertandang", 2500),
            ("Wedding Nikah", 500),
            ("Wedding Sanding/Bertandang", 800),
            ("Wedding Bertunang", 500),
            ("Studio", 200),
            ("Outdoor", 250),
            ("Event 1 hour", 200),
            ("Graduation", 200)
        ]
        conn.executemany("INSERT INTO packages (nama, harga) VALUES (?, ?)", default_packages)
        conn.commit()
    conn.close()


init_db()

# ===============================
# HELPER FUNCTION
# ===============================
def get_packages():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM packages ORDER BY nama ASC").fetchall()
    conn.close()
    return data


# ===============================
# ROUTE: LAMAN UTAMA
# ===============================
@app.route('/')
def index():
    conn = get_db_connection()

    # Ambil tarikh yang telah penuh tempahan
    full_dates = [row['tarikh'] for row in conn.execute("SELECT tarikh FROM bookings").fetchall()]

    # Ambil senarai pakej
    packages = conn.execute("SELECT nama, harga FROM packages ORDER BY nama ASC").fetchall()
    conn.close()

    pakej_dict = {row['nama']: row['harga'] for row in packages}

    msg = session.pop('msg', None)
    error = session.pop('error', None)

    return render_template('index.html', full_dates=full_dates, pakej_dict=pakej_dict, msg=msg, error=error)


# ===============================
# ROUTE: SUBMIT TEMPAHAN
# ===============================
@app.route('/submit', methods=['POST'])
def submit():
    nama = request.form['nama']
    phone = request.form['phone']
    tarikh = request.form['tarikh']
    pakej = request.form['pakej']
    note = request.form.get('note')

    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM bookings WHERE tarikh=?", (tarikh,)).fetchone()[0]
    if count >= MAX_BOOKING_PER_DAY:
        conn.close()
        session['error'] = f"❌ Tarikh {tarikh} sudah penuh!"
        return redirect(url_for('index'))

    conn.execute("INSERT INTO bookings (nama, phone, tarikh, pakej, note) VALUES (?, ?, ?, ?, ?)",
                 (nama, phone, tarikh, pakej, note))
    conn.commit()
    conn.close()

    session['msg'] = f"✅ Tempahan berjaya dibuat untuk {tarikh} ({pakej})!"
    return redirect(url_for('index'))


# ===============================
# ROUTE: SENARAI TEMPAHAN
# ===============================
@app.route('/bookings')
def bookings():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM bookings ORDER BY tarikh ASC").fetchall()
    conn.close()
    return render_template('bookings.html', bookings=rows)


# ===============================
# ROUTE: EDIT TEMPAHAN
# ===============================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_booking(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    booking = conn.execute("SELECT * FROM bookings WHERE id=?", (id,)).fetchone()
    pakej_list = get_packages()

    if request.method == 'POST':
        nama = request.form['nama']
        phone = request.form['phone']
        pakej = request.form['pakej']
        tarikh = request.form['tarikh']
        note = request.form['note']
        conn.execute("UPDATE bookings SET nama=?, phone=?, pakej=?, tarikh=?, note=? WHERE id=?",
                     (nama, phone, pakej, tarikh, note, id))
        conn.commit()
        conn.close()
        flash("✅ Tempahan berjaya dikemaskini!", "success")
        return redirect(url_for('bookings'))

    conn.close()
    return render_template('edit_booking.html', booking=booking, pakej_list=pakej_list)


# ===============================
# ROUTE: PADAM TEMPAHAN
# ===============================
@app.route('/delete/<int:id>', methods=['POST'])
def delete_booking(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM bookings WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Tempahan dipadam!", "success")
    return redirect(url_for('bookings'))


# ===============================
# ROUTE: URUS PAKEJ
# ===============================
# --- Admin: Urus Pakej ---
@app.route('/admin/pakej', methods=['GET', 'POST'])
def urus_pakej():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        action = request.form.get('action')
        nama = request.form.get('nama')
        harga = request.form.get('harga')
        id_pakej = request.form.get('id')

        try:
            if action == 'add':
                conn.execute("INSERT INTO packages (nama, harga) VALUES (?, ?)", (nama, harga))
                flash("✅ Pakej baru ditambah!", "success")
            elif action == 'update':
                conn.execute("UPDATE packages SET nama=?, harga=? WHERE id=?", (nama, harga, id_pakej))
                flash("✏️ Pakej dikemaskini!", "success")
            elif action == 'delete':
                conn.execute("DELETE FROM packages WHERE id=?", (id_pakej,))
                flash("🗑️ Pakej dipadam!", "success")
            conn.commit()
        except sqlite3.IntegrityError:
            flash("❌ Nama pakej sudah wujud. Gunakan nama lain!", "error")

    pakej_all = conn.execute("SELECT * FROM packages ORDER BY nama ASC").fetchall()
    conn.close()

    # Pastikan guna nama pembolehubah yang sepadan dengan HTML
    return render_template('manage_packages.html', pakej_all=pakej_all)



# ===============================
# ROUTE: LOGIN ADMIN
# ===============================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash("✅ Login berjaya!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("❌ Salah username atau password.", "error")
    return render_template('login.html')


# ===============================
# ROUTE: DASHBOARD ADMIN
# ===============================
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    total_bookings = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    total_packages = conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0]
    conn.close()

    return render_template('admin_dashboard.html',
                           total_bookings=total_bookings,
                           total_packages=total_packages)


# ===============================
# ROUTE: LOGOUT
# ===============================
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("✅ Anda telah log keluar.", "success")
    return redirect(url_for('login'))


# ===============================
# ROUTE: KALENDAR
# ===============================
@app.route('/calendar')
def calendar():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    rows = conn.execute('SELECT tarikh, COUNT(*) as jumlah FROM bookings GROUP BY tarikh').fetchall()
    conn.close()
    data = []
    for row in rows:
        status = "Penuh ❌" if row['jumlah'] >= MAX_BOOKING_PER_DAY else "Kosong ✅"
        data.append({"tarikh": row['tarikh'], "jumlah": row['jumlah'], "status": status})
    return render_template('calendar.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
