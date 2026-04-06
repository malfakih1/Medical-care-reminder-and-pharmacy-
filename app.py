from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

# =========================
# إنشاء الجداول
# =========================
def create_tables():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # جدول الدكاترة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            specialty TEXT
        )
    ''')

    # جدول المرضى
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER
        )
    ''')

    conn.commit()
    conn.close()


# =========================
# إدخال بيانات الدكاترة
# =========================
def insert_doctors():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM doctors")

    doctors = [
        ("Dr. Ahmed Mohamed", "General Medicine"),
        ("Dr. Sara Ali", "Cardiology"),
        ("Dr. Khalid Ibrahim", "Pediatrics"),
        ("Dr. Mona Hassan", "Dermatology"),
        ("Dr. Omar Yousuf", "Eye Care"),
        ("Dr. Fatima Omar", "General Medicine")
    ]

    cursor.executemany(
        "INSERT INTO doctors (name, specialty) VALUES (?, ?)", doctors
    )

    conn.commit()
    conn.close()


# =========================
# إدخال بيانات المرضى
# =========================
def insert_patients():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM patients")

    patients = [
        ("Ali Ahmed", 25),
        ("Sara Mohamed", 30),
        ("Omar Khalid", 40),
        ("Fatima Hassan", 22)
    ]

    cursor.executemany(
        "INSERT INTO patients (name, age) VALUES (?, ?)", patients
    )

    conn.commit()
    conn.close()


# =========================
# الصفحة الرئيسية
# =========================
@app.route('/')
def home():
    return "Backend is working!"


# =========================
# API الدكاترة
# =========================
@app.route('/doctors')
def get_doctors():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM doctors")
    data = cursor.fetchall()

    doctors_list = []
    for d in data:
        doctors_list.append({
            "id": d[0],
            "name": d[1],
            "specialty": d[2]
        })

    conn.close()
    return jsonify(doctors_list)


# =========================
# API المرضى
# =========================
@app.route('/patients')
def get_patients():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    data = cursor.fetchall()

    patients_list = []
    for p in data:
        patients_list.append({
            "id": p[0],
            "name": p[1],
            "age": p[2]
        })

    conn.close()
    return jsonify(patients_list)


# =========================
# تشغيل أولي
# =========================
create_tables()
insert_doctors()
insert_patients()


# =========================
# تشغيل السيرفر (بدون مشاكل)
# =========================
app.run(debug=True)