# app.py

from flask import Flask, render_template, request, redirect, url_for, session, jsonify 
import sqlite3
import hashlib
import math
import os
from datetime import datetime
from flask_mail import Mail, Message  # <-- Import Mail and Message
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='../frontend', static_folder='../static') # <-- Point to static folder
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change_this_in_production')

# --- Flask-Mail Configuration ---
# IMPORTANT: Use environment variables for sensitive data.
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') # Your email (e.g., your-email@gmail.com)
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') # Your email app-password
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app) # <-- Initialize Mail

DATABASE = 'blood_donation.db'


# ✅ Database helper functions
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ✅ Initialize DB automatically with schema
def init_db():
    conn = get_db()
    schema = """
    -- Blood Donation Management System Database Schema

    CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        contact TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        age INTEGER NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        last_donation_month TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS receivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        contact TEXT NOT NULL,
        hospital_name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS hospitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        contact TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES receivers(id) ON DELETE CASCADE,
        UNIQUE(donor_id, receiver_id)
    );

    CREATE INDEX IF NOT EXISTS idx_donors_email ON donors(email);
    CREATE INDEX IF NOT EXISTS idx_receivers_email ON receivers(email);
    CREATE INDEX IF NOT EXISTS idx_hospitals_email ON hospitals(email);
    CREATE INDEX IF NOT EXISTS idx_requests_donor ON requests(donor_id);
    CREATE INDEX IF NOT EXISTS idx_requests_receiver ON requests(receiver_id);
    CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);
    """
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


# ✅ Haversine distance formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ✅ Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ✅ Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup_donor', methods=['GET', 'POST'])
def signup_donor():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = hash_password(request.form['password'])
        contact = request.form['contact']
        blood_group = request.form['blood_group']
        age = request.form['age']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        last_donation_month = request.form.get('last_donation_month', '')

        conn = get_db()
        try:
            conn.execute('''INSERT INTO donors (name, email, password, contact, blood_group, age, latitude, longitude, last_donation_month)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (name, email, password, contact, blood_group, age, latitude, longitude, last_donation_month))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists!", 400
    return render_template('signup_donor.html', google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY', ''))


@app.route('/signup_receiver', methods=['GET', 'POST'])
def signup_receiver():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = hash_password(request.form['password'])
        contact = request.form['contact']
        hospital_name = request.form['hospital_name']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])

        conn = get_db()
        try:
            conn.execute('''INSERT INTO receivers (name, email, password, contact, hospital_name, latitude, longitude)
                             VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (name, email, password, contact, hospital_name, latitude, longitude))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists!", 400
    return render_template('signup_receiver.html', google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY', ''))


@app.route('/signup_hospital', methods=['GET', 'POST'])
def signup_hospital():
    if request.method == 'POST':
        hospital_id = request.form['hospital_id']
        name = request.form['name']
        email = request.form['email']
        password = hash_password(request.form['password'])
        contact = request.form['contact']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])

        conn = get_db()
        try:
            conn.execute('''INSERT INTO hospitals (hospital_id, name, email, password, contact, latitude, longitude)
                             VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (hospital_id, name, email, password, contact, latitude, longitude))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Email or Hospital ID already exists!", 400
    return render_template('signup_hospital.html', google_maps_api_key=os.environ.get('GOOGLE_MAPS_API_KEY', ''))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        user_type = request.form['user_type']
        conn = get_db()

        user = None
        if user_type == 'donor':
            user = conn.execute('SELECT * FROM donors WHERE email = ? AND password = ?', (email, password)).fetchone()
        elif user_type == 'receiver':
            user = conn.execute('SELECT * FROM receivers WHERE email = ? AND password = ?', (email, password)).fetchone()
        elif user_type == 'hospital':
            user = conn.execute('SELECT * FROM hospitals WHERE email = ? AND password = ?', (email, password)).fetchone()

        if user:
            session['user_id'] = user['id']
            session['user_type'] = user_type
            session['user_name'] = user['name']
            conn.close()
            return redirect(url_for(f'dashboard_{user_type}'))
        conn.close()
        return "Invalid credentials!", 401
    return render_template('login.html')


@app.route('/dashboard_donor')
def dashboard_donor():
    if 'user_id' not in session or session['user_type'] != 'donor':
        return redirect(url_for('login'))

    conn = get_db()
    donor_id = session['user_id']
    donor = conn.execute('SELECT * FROM donors WHERE id = ?', (donor_id,)).fetchone()
    
    requests = conn.execute('''
        SELECT r.id, r.status, rec.name as receiver_name, rec.contact as receiver_contact,
               rec.email as receiver_email, rec.hospital_name, r.created_at
        FROM requests r
        JOIN receivers rec ON r.receiver_id = rec.id
        WHERE r.donor_id = ?
        ORDER BY r.created_at DESC
    ''', (donor_id,)).fetchall()
    
    conn.close()
    return render_template('dashboard_donor.html', donor=donor, requests=requests)


@app.route('/dashboard_receiver')
def dashboard_receiver():
    if 'user_id' not in session or session['user_type'] != 'receiver':
        return redirect(url_for('login'))

    conn = get_db()
    receiver_id = session['user_id']
    receiver_row = conn.execute('SELECT * FROM receivers WHERE id = ?', (receiver_id,)).fetchone()
    receiver_dict = dict(receiver_row) if receiver_row else None
    
    donors = conn.execute("""
        SELECT * FROM donors
        WHERE id NOT IN (
            SELECT donor_id FROM requests WHERE receiver_id = ?
        )
    """, (receiver_id,)).fetchall()

    donor_list = []
    if receiver_dict and donors:
        for donor in donors:
            donor_dict = dict(donor)
            distance = haversine(receiver_dict['latitude'], receiver_dict['longitude'], donor_dict['latitude'], donor_dict['longitude'])
            donor_dict['distance'] = round(distance, 2)
            donor_list.append(donor_dict)
            
        donor_list.sort(key=lambda x: x['distance'])
        
    sent_requests = conn.execute("""
        SELECT 
            r.status, 
            d.name as donor_name, 
            d.email as donor_email,
            d.contact as donor_contact, 
            d.blood_group as donor_blood_group
        FROM requests r
        JOIN donors d ON r.donor_id = d.id
        WHERE r.receiver_id = ?
        ORDER BY r.created_at DESC
    """, (receiver_id,)).fetchall()

    conn.close()
    
    return render_template(
        'dashboard_receiver.html', 
        receiver=receiver_dict, 
        donors=donor_list, 
        sent_requests=sent_requests
    )

@app.route('/dashboard_hospital')
def dashboard_hospital():
    if 'user_id' not in session or session['user_type'] != 'hospital':
        return redirect(url_for('login'))

    conn = get_db()
    hospital = conn.execute('SELECT * FROM hospitals WHERE id = ?', (session['user_id'],)).fetchone()
    donors = conn.execute('SELECT * FROM donors').fetchall()

    donor_list = []
    for donor in donors:
        distance = haversine(hospital['latitude'], hospital['longitude'], donor['latitude'], donor['longitude'])
        donor_list.append({
            'id': donor['id'],
            'name': donor['name'],
            'blood_group': donor['blood_group'],
            'age': donor['age'],
            'contact': donor['contact'],
            'distance': round(distance, 2)
        })
    donor_list.sort(key=lambda x: x['distance'])
    conn.close()
    return render_template('dashboard_hospital.html', hospital=hospital, donors=donor_list)


@app.route('/update_donor', methods=['POST'])
def update_donor():
    if 'user_id' not in session or session['user_type'] != 'donor':
        return redirect(url_for('login'))

    blood_group = request.form['blood_group']
    contact = request.form['contact']
    age = request.form['age']
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    last_donation_month = request.form['last_donation_month']

    conn = get_db()
    conn.execute('''UPDATE donors 
                      SET blood_group = ?, contact = ?, age = ?, latitude = ?, longitude = ?, last_donation_month = ?
                      WHERE id = ?''',
                 (blood_group, contact, age, latitude, longitude, last_donation_month, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard_donor'))

@app.route('/send_request', methods=['POST'])
def send_request():
    if 'user_id' not in session or session['user_type'] != 'receiver':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # This now expects a JSON payload, e.g., from a JavaScript fetch() call
    # --- THIS IS A BUGFIX from the original file ---
    # The original HTML file uses a standard FORM post, not JSON.
    # We must change this to read from request.form.
    
    donor_id = request.form.get('donor_id') # <-- FIX: Use request.form
    if not donor_id:
        return "Donor ID is required", 400
        
    receiver_id = session['user_id']
    
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO requests (donor_id, receiver_id) VALUES (?, ?)',
            (donor_id, receiver_id)
        )
        conn.commit()
        # --- FIX: Redirect back instead of sending JSON ---
        return redirect(url_for('dashboard_receiver'))
    except sqlite3.IntegrityError:
        # This error is triggered by the UNIQUE constraint in the database schema
        # You should add a flash message here to show the user
        return "You have already sent a request to this donor.", 409
    finally:
        conn.close()

# --- REPLACE the old accept_request function with this new one ---
@app.route('/accept_request/<int:request_id>')
def accept_request(request_id):
    if 'user_id' not in session or session['user_type'] != 'donor':
        return redirect(url_for('login'))
    
    conn = get_db()
    
    # First, get the request details BEFORE updating
    request_data = conn.execute('''
        SELECT 
            req.id, 
            rec.email AS receiver_email, 
            rec.name AS receiver_name,
            don.name AS donor_name
        FROM requests req
        JOIN receivers rec ON req.receiver_id = rec.id
        JOIN donors don ON req.donor_id = don.id
        WHERE req.id = ? AND req.donor_id = ?
    ''', (request_id, session['user_id'])).fetchone()

    if not request_data:
        conn.close()
        return "Error: Request not found or you are not authorized.", 404

    # Now, update the request status
    conn.execute('UPDATE requests SET status = ? WHERE id = ?',
                 ('accepted', request_id))
    conn.commit()
    conn.close()

    # --- Send the email ---
    if not os.environ.get('MAIL_USERNAME'):
        print("MAIL_USERNAME not set. Skipping email.")
        return redirect(url_for('dashboard_donor'))

    try:
        msg = Message(
            subject="Your Blood Request has been Accepted! - Arogya Deeksha",
            recipients=[request_data['receiver_email']],
            body=f"""
            Dear {request_data['receiver_name']},

            Great news! Your request for blood has been accepted by donor {request_data['donor_name']}.

            Please coordinate with them for the next steps.

            Thank you,
            Arogya Deeksha Team
            """
        )
        mail.send(msg)
    except Exception as e:
        # Log the error, but don't stop the user
        print(f"Error sending email: {e}")
        # You could add a flash message here: flash(f"Error sending email: {e}")

    return redirect(url_for('dashboard_donor'))


@app.route('/reject_request/<int:request_id>')
def reject_request(request_id):
    if 'user_id' not in session or session['user_type'] != 'donor':
        return redirect(url_for('login'))

    conn = get_db()
    conn.execute('UPDATE requests SET status = ? WHERE id = ? AND donor_id = ?',
                 ('rejected', request_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard_donor'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ✅ Start server
if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    else:
        print("✅ Database already exists.")
        
    if not os.environ.get('MAIL_USERNAME') or not os.environ.get('MAIL_PASSWORD'):
        print("WARNING: MAIL_USERNAME or MAIL_PASSWORD environment variables not set.")
        print("Email notifications will fail. Set them before running in production.")

    port = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=True) # Added debug=True for development