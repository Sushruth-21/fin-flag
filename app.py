import csv
from cs50 import SQL
from datetime import datetime
from engine import check_velocity, check_outlier
from flask import Flask, render_template, request, jsonify, session, redirect, flash, url_for
import io
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

# Api key
app.secret_key = os.getenv("FINFLAG_SECRET_KEY")

if not app.secret_key:
    raise ValueError("No secret key set for Flask application. Please set the FINFLAG_SECRET_KEY environment variable.")


# Retrieve the database
db = SQL("sqlite:///finflag.db")


# Index
@app.route('/')
def index():

    # Protect the route!
    if session.get("admin_id") is None:
        return redirect("/login")
    
    return render_template("index.html")


# Dashboard
@app.route('/dashboard')
def dashboard():

    # Protect the route!
    if session.get("admin_id") is None:
        return redirect("/login")
    
    return render_template("soc_feed.html")


# Process Transactions
@app.route('/process_transaction', methods=["POST"])
def process_transaction():
    user_id = int(request.form.get("user_id"))
        
    existing_user = db.execute("SELECT id FROM users WHERE id = ?", user_id)
    if not existing_user:
        db.execute("INSERT INTO users (id, username) VALUES (?, 'Guest')", user_id)
        
    amount = float(request.form.get("amount"))

    current_time = datetime.now()

    is_velocity_flagged = check_velocity(user_id, current_time)

    raw_db_history = db.execute("SELECT amount FROM transactions WHERE user_id = ?", user_id)

    clean_history_list = []

    for row in raw_db_history:
        clean_history_list.append(row["amount"])

    is_outlier_flagged = check_outlier(clean_history_list, amount)

    final_flag_status = 0

    # Flagging Anomalies
    if is_velocity_flagged or is_outlier_flagged:
        final_flag_status = 1
        if is_outlier_flagged:
            flag_reason = "Statistical Outlier"
        else:
            flag_reason = "Velocity Anomaly"
    else:
        flag_reason = "None"

    current_admin = session.get("admin_id")

    db.execute("INSERT INTO transactions(user_id, amount, timestamp, is_flagged, flag_type, admin_id) VALUES ( ?, ?, ?, ?, ?, ?)", user_id, amount, current_time, final_flag_status, flag_reason, current_admin)

    return "Processed! Flag Status: " + str(final_flag_status)


# Alerts
@app.route('/api/alerts')
def get_alerts():

    # Protect the route!
    if session.get("admin_id") is None:
        return jsonify({"error": "Unauthorized"}), 401

    current_admin = session.get("admin_id")
    max_filter = request.args.get('max_filter')
    min_filter = request.args.get('min_filter')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 25, type=int)

    offset = (page - 1) * limit

    if max_filter and min_filter:
        recent_alerts = db.execute("SELECT id, user_id, amount, flag_type, timestamp FROM transactions WHERE admin_id = ? AND is_flagged = 1 AND amount BETWEEN ? AND ? ORDER BY timestamp DESC LIMIT ? OFFSET ?", current_admin, float(min_filter), float(max_filter), limit, offset)
    else:
        recent_alerts = db.execute("SELECT id, user_id, amount, flag_type, timestamp FROM transactions WHERE admin_id = ? AND is_flagged = 1 ORDER BY timestamp DESC LIMIT ? OFFSET ?", current_admin, limit, offset)

    return jsonify([dict(row) for row in recent_alerts])


# File
@app.route('/csv', methods=['POST'])
def upload_csv():

    # Protect the route!
    if session.get("admin_id") is None:
        return redirect("/login")

    current_admin = session.get("admin_id")

    if 'file' not in request.files:
        return "No file uploaded", 400 

    uploaded_file = request.files['file']

    if uploaded_file.filename == "":
        return "Empty File", 400

    # bytes into strings using UTF-8
    text_stream = io.TextIOWrapper(uploaded_file.stream, encoding="utf-8")
    csv_reader = csv.DictReader(text_stream)

    processed_count = 0
    flagged_count = 0

    for row in csv_reader:
        user_id = int(row['user_id'])
        amount = float(row['amount'])

        # Extract the timestamp if it exists, otherwise return None
        csv_timestamp = row.get('timestamp')

        if csv_timestamp:
            # Convert the CSV string into a real Python datetime object
            current_time = datetime.strptime(csv_timestamp, '%Y-%m-%d %H:%M:%S')
        else:
            # Timestamp column is missing
            current_time = datetime.now()

        existing_user = db.execute("SELECT id FROM users WHERE ID = ?", user_id)

        if not existing_user:
            db.execute("INSERT INTO users (id, username) VALUES (?, ?)", user_id, f"Student_{user_id}")

        is_velocity_flagged = check_velocity(user_id, current_time)

        raw_db_history = db.execute("SELECT amount FROM transactions WHERE user_id = ?", user_id)

        clean_history_list = []

        for r in raw_db_history:
            clean_history_list.append(r["amount"])

        is_outlier_flagged = check_outlier(clean_history_list, amount)

        final_flag_status = 0

        # Flagging Anomalies
        if is_velocity_flagged or is_outlier_flagged:
            final_flag_status = 1
            flagged_count += 1
            if is_outlier_flagged:
                flag_reason = "Statistical Outlier"
            else:
                flag_reason = "Velocity Anomaly"
        else:
            flag_reason = "None"

        db.execute("INSERT INTO transactions(user_id, amount, timestamp, is_flagged, flag_type, admin_id) VALUES ( ?, ?, ?, ?, ?, ?)", user_id, amount, current_time, final_flag_status, flag_reason, current_admin)

        processed_count += 1

    flash(f"Processed {processed_count} rows. Found {flagged_count} anomalies!")
    return redirect(url_for('dashboard'))


# Register
@app.route('/register', methods=["GET", "POST"])
def register():
    # POST
    if request.method == "POST":
        username =  request.form.get("username")
        password = request.form.get("password")
        confirmation =  request.form.get("confirmation")

        if not username or not password or not confirmation:
            return "All fields required", 400

        if password != confirmation:
            return "Password do not match", 400

        check_username = db.execute("SELECT username FROM admins WHERE username = ?", username)

        if len(check_username) >= 1:
            return "Username already exists", 400

        hashed_password = generate_password_hash(password)

        db.execute("INSERT INTO admins(username, hash) VALUES ( ?, ?)", username, hashed_password)

        return redirect("/login")

    # GET
    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()

    # POST
    if request.method == "POST":
        username =  request.form.get("username")
        password = request.form.get("password")

        # Empty username or password
        if not username or not password:
                return "All fields required", 400

        rows = db.execute("SELECT * FROM admins WHERE username = ?",username)

        # Check Username and Password
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Invalid username and/or password", 400

        # Current Session ID
        session["admin_id"] = rows[0]["id"]

        # Index
        return redirect("/")

    # GET
    return render_template("login.html")


# Logout
@app.route('/logout')
def logout():

    # Clear cookies
    session.clear()

    return redirect("/")


# DELETE transactions
@app.route('/api/delete/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):

    if session.get("admin_id") is None:
        return jsonify({"error": "Unauthorized"}), 401

    current_admin = session.get("admin_id")

    db.execute("DELETE FROM transactions WHERE id = ? AND admin_id = ?", transaction_id, current_admin)

    return jsonify({"success": True, "message": "Transaction deleted"})