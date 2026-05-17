from flask import Flask, render_template, request, redirect, url_for, session, g
import os
import sqlite3
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ✅ Load the trained model
MODEL_PATH = "pneumonia_model.h5"
model = load_model(MODEL_PATH)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Updated with timeout
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("database.db", check_same_thread=False, timeout=10)
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                age INTEGER,
                symptoms TEXT,
                contact TEXT,
                xray_image TEXT,
                diagnosis TEXT,
                confidence REAL,
                status TEXT DEFAULT 'Pending',
                recommendation TEXT DEFAULT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT DEFAULT '1234',
                role TEXT DEFAULT 'patient'
            )
        """)
        cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('DoctorJohn', '1234', 'doctor')")
        cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('HealthworkerMike', 'abcd', 'health_worker')")
        db.commit()

init_db()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT username, role FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            session['role'] = user[1]
            if session['role'] == "doctor":
                return redirect(url_for("doctor_dashboard"))
            elif session['role'] == "health_worker":
                return redirect(url_for("health_worker_dashboard"))
            else:
                return redirect(url_for("patient_dashboard"))
        return "Invalid Credentials. Try Again!"
    return render_template("login.html")

@app.route('/dashboard/doctor')
def doctor_dashboard():
    if 'username' in session and session['role'] == 'doctor':
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY id DESC")
        patients = cursor.fetchall()
        return render_template("doctor_dashboard.html", username=session['username'], patients=patients)
    return redirect(url_for('login'))

@app.route('/dashboard/health_worker')
def health_worker_dashboard():
    if 'username' in session and session['role'] == 'health_worker':
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY id DESC")
        patients = cursor.fetchall()
        return render_template("health_worker_dashboard.html", username=session['username'], patients=patients)
    return redirect(url_for('login'))

@app.route('/dashboard/patient')
def patient_dashboard():
    if 'username' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM patients WHERE name = ?", (session['username'],))
    patient_record = cursor.fetchone()
    return render_template("patient_dashboard.html", username=session['username'], patient_record=patient_record)

# ✅ Updated to use "with db:"
@app.route('/new_patient', methods=['GET', 'POST'])
def new_patient():
    if 'username' not in session or session['role'] != 'health_worker':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['fullname']
        age = request.form['age']
        symptoms = request.form['symptoms']
        contact = request.form['contact']
        file = request.files['xray']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            db = get_db()
            with db:
                cursor = db.cursor()
                cursor.execute("""
                    INSERT INTO patients (name, age, symptoms, contact, xray_image, diagnosis, confidence, status)
                    VALUES (?, ?, ?, ?, ?, 'Pending', 0.0, 'Pending')
                """, (name, age, symptoms, contact, filename))
                cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, '1234', 'patient')",
                               (name,))
            return redirect(url_for('diagnosis_result', filename=filename))
    return render_template("new_patient.html")

# ✅ Updated to use "with db:"
@app.route('/diagnosis_result/<filename>')
def diagnosis_result(filename):
    db = get_db()
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = image.load_img(filepath, target_size=(150, 150), color_mode="grayscale")
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    confidence = round(float(prediction[0][0]) * 100, 2)
    result_text = "Pneumonia Detected" if prediction[0][0] > 0.5 else "Normal"
    with db:
        cursor = db.cursor()
        cursor.execute("UPDATE patients SET diagnosis = ?, confidence = ? WHERE xray_image = ?",
                       (result_text, confidence, filename))
    return render_template("diagnosis_result.html", filename=filename, result_text=result_text, confidence=confidence)

# ✅ Updated to use "with db:"
@app.route('/recommendation/<int:patient_id>', methods=['GET', 'POST'])
def recommendation(patient_id):
    db = get_db()
    with db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()
        if request.method == 'POST':
            recommendation = request.form['recommendation']
            cursor.execute("UPDATE patients SET recommendation = ?, status = 'Reviewed' WHERE id = ?",
                           (recommendation, patient_id))
            return redirect(url_for('doctor_dashboard'))
    return render_template('recommendation.html', patient=patient)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5000)
