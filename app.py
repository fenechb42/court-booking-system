
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import json, os, uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecret')

BOOKINGS_FILE = 'bookings.json'
USERS_FILE = 'users.json'

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE) as f:
            return json.load(f)
    return {}

def save_bookings(bookings):
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(bookings, f)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        users = load_users()
        if email not in users:
            users[email] = {'name': email.split('@')[0], 'admin': False}
            save_users(users)
        session['user'] = email
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    date_str = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    selected_date = datetime.strptime(date_str, '%Y-%m-%d')
    bookings = load_bookings()
    users = load_users()
    user_email = session['user']
    user = users[user_email]
    day_bookings = bookings.get(date_str, {})

    if request.method == 'POST':
        action = request.form.get('action')
        court = int(request.form['court'])
        hour = int(request.form['hour'])
        key = f"court_{court}_hour_{hour}"

        if action == 'book':
            if key not in day_bookings:
                day_bookings[key] = {'user': user_email, 'name': user['name']}
        elif action == 'cancel':
            if key in day_bookings and (day_bookings[key]['user'] == user_email or user.get('admin')):
                del day_bookings[key]

        bookings[date_str] = day_bookings
        save_bookings(bookings)
        return redirect(url_for('index', date=date_str))

    hours = list(range(7, 22))
    courts = {i: 'Clay' if i <= 4 else 'Hard' for i in range(1, 9)}
    return render_template('index.html', date_str=date_str, hours=hours, courts=courts, bookings=day_bookings, user=user, user_email=user_email, next_7_days=[(selected_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
