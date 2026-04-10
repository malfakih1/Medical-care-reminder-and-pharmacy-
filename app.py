from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def create_tables():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            specialty TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            appointment_date TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    ''')
    conn.commit()
    conn.close()

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
    cursor.executemany("INSERT INTO doctors (name, specialty) VALUES (?, ?)", doctors)
    conn.commit()
    conn.close()

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
    cursor.executemany("INSERT INTO patients (name, age) VALUES (?, ?)", patients)
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return "Backend is working!"

# UPDATED: try/except added
@app.route('/doctors')
def get_doctors():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors")
        data = cursor.fetchall()
        conn.close()
        return jsonify([{"id": d[0], "name": d[1], "specialty": d[2]} for d in data])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# UPDATED: try/except added
@app.route('/patients')
def get_patients():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients")
        data = cursor.fetchall()
        conn.close()
        return jsonify([{"id": p[0], "name": p[1], "age": p[2]} for p in data])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# UPDATED: try/except added
@app.route('/appointments', methods=['GET'])
def get_appointments():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.id, p.name, d.name, a.appointment_date, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
        ''')
        data = cursor.fetchall()
        conn.close()
        return jsonify([{
            "id": row[0],
            "patient": row[1],
            "doctor": row[2],
            "date": row[3],
            "status": row[4]
        } for row in data])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# UPDATED: Full validation + try/except
@app.route('/appointments', methods=['POST'])
def book_appointment():
    try:
        body = request.get_json()

        # Validate required fields
        if not body or not all(k in body for k in ('patient_id', 'doctor_id', 'appointment_date')):
            return jsonify({"error": "patient_id, doctor_id, and appointment_date are required"}), 400

        patient_id = body['patient_id']
        doctor_id = body['doctor_id']
        appointment_date = body['appointment_date']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Validate doctor exists
        cursor.execute("SELECT id FROM doctors WHERE id = ?", (doctor_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Doctor not found"}), 404

        # Validate patient exists
        cursor.execute("SELECT id FROM patients WHERE id = ?", (patient_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Patient not found"}), 404

        cursor.execute(
            "INSERT INTO appointments (patient_id, doctor_id, appointment_date) VALUES (?, ?, ?)",
            (patient_id, doctor_id, appointment_date)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"message": "Appointment booked", "appointment_id": new_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

create_tables()
insert_doctors()
insert_patients()

app.run(debug=True)
