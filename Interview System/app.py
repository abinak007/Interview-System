from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import openai
import sqlite3
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Used for session management

# Database Connection Function
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------- ROUTES ---------- #

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ---------- AUTHENTICATION ---------- #

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            flash('Username and password cannot be empty.', 'danger')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash('Signup successful! You can now login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another.', 'danger')
        finally:
            conn.close()

    return render_template('signup.html')

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_type = request.form["user_type"]
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        if user_type == "admin":
            cursor.execute("SELECT * FROM admin WHERE username = ?", (username,))
            admin = cursor.fetchone()
            if admin and check_password_hash(admin["password"], password):
                session["user_type"] = "admin"
                session["username"] = username
                conn.close()
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Invalid Admin Credentials. Please try again.", "danger")

        elif user_type == "user":
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user["password"], password):
                session["user_type"] = "user"
                session["username"] = username
                session["user_id"] = user["id"]
                conn.close()
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid User Credentials. Please try again.", "danger")

        conn.close()
    return render_template("login.html")

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# ---------- DASHBOARDS ---------- #

# User Dashboard
@app.route("/dashboard")
def dashboard():
    if "user_type" in session and session["user_type"] == "user":
        return render_template("dashboard.html")
    flash("You must be logged in to access the dashboard.", "danger")
    return redirect(url_for("login"))

# Admin Dashboard
@app.route("/admin_dashboard")
def admin_dashboard():
    if "user_type" in session and session["user_type"] == "admin":
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM interview_session")
        interview_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM response")
        response_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emotions")
        emotion_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM feedback")
        feedback_count = cursor.fetchone()[0]

        conn.close()

        return render_template("admin_dashboard.html", user_count=user_count, interview_count=interview_count, response_count=response_count, emotion_count=emotion_count, feedback_count=feedback_count)

    flash("You must be logged in as an admin to access this page.", "danger")
    return redirect(url_for("login"))

# ---------- INTERVIEW SYSTEM ---------- #

# Start Interview Route
@app.route("/start_interview")
def start_interview():
    if "username" in session:
        return redirect(url_for('interview'))

    flash("You must be logged in to start the interview.", "danger")
    return redirect(url_for('login'))

@app.route('/interview')
def interview():
    return render_template('interview.html')

@app.route('/interview_failed')
def interview_failed():
    flash("You have failed the interview. Try again.", "danger")
    return redirect(url_for('dashboard'))

# Results Route
@app.route('/results')
def results():
    if "user_id" in session:
        user_id = session["user_id"]
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch user score
        cursor.execute("SELECT score FROM response ORDER BY RANDOM() LIMIT 1")
        score = cursor.fetchone()["score"]

        # Fetch confidence level and expression analysis
        cursor.execute("SELECT confidence_level, expression_analysis FROM emotions ORDER BY RANDOM() LIMIT 1")
        emotion_data = cursor.fetchone()

        confidence_level = emotion_data["confidence_level"] if emotion_data else "N/A"
        expression_analysis = emotion_data["expression_analysis"] if emotion_data else "N/A"

        conn.close()

        return render_template("results.html", score=score, confidence_level=confidence_level, expression_analysis=expression_analysis)

    flash("You must be logged in to view results.", "danger")
    return redirect(url_for("login"))
# ---------- View delete user ---------- #
@app.route('/view_users')
def view_users():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('view_users.html', users=users)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_users'))

# ---------- Feedback ---------- #
@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    experience = request.form['experience']
    suggestion = request.form.get('suggestion', '')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedback (experience, suggestion) VALUES (?, ?)",
                   (experience, suggestion))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

# ---------- View Feedback ---------- #
@app.route('/view_feedback')
def view_feedback():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, experience, suggestion FROM feedback")
    feedback = cursor.fetchall()
    conn.close()
    return render_template('view_feedback.html', feedback=feedback)

# ---------- RUN SERVER ---------- #
if __name__ == '__main__':
    app.run(debug=True)



