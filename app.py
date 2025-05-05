from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

courts = {
    1: 'Clay', 2: 'Clay', 3: 'Clay', 4: 'Clay',
    5: 'Hard', 6: 'Hard', 7: 'Hard', 8: 'Hard'
}

BOOKINGS_FILE = 'bookings.json'

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_bookings(data):
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(data, f)

def is_blocked(day, court, hour):
    blocks = {
        'Sunday': {(1, h) for h in range(8, 13)} | {(3, h) for h in range(8, 13)},
        'Monday': {(7, h) for h in range(8, 13)} | {(5, h) for h in range(16, 19)} | {(7, h) for h in range(16, 22)},
        'Tuesday': {(7, h) for h in range(9, 11)} | {(7, h) for h in range(16, 21)} | {(5, h) for h in range(16, 19)},
        'Wednesday': {(7, h) for h in range(9, 12)} | {(7, h) for h in range(16, 21)} | {(5, h) for h in range(16, 19)},
        'Thursday': {(7, h) for h in range(9, 13)} | {(7, h) for h in range(16, 20)} | {(5, h) for h in range(16, 19)},
        'Friday': {(7, h) for h in range(9, 13)} | {(7, h) for h in range(16, 20)},
        'Saturday': {(7, h) for h in range(8, 13)}
    }
    day_name = day.strftime('%A')
    return (court, hour) in blocks.get(day_name, set())

@app.route('/', methods=['GET', 'POST'])
def index():
    date_str = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    selected_date = datetime.strptime(date_str, '%Y-%m-%d')
    bookings = load_bookings()
    day_bookings = bookings.get(date_str, {})

    if request.method == 'POST':
        if 'cancel' in request.form:
            court = int(request.form['court'])
            hour = int(request.form['hour'])
            key = f"court_{court}_hour_{hour}"
            if key in day_bookings:
                del day_bookings[key]
                bookings[date_str] = day_bookings
                save_bookings(bookings)
        else:
            name = request.form['name']
            court = int(request.form['court'])
            hour = int(request.form['hour'])
            key = f"court_{court}_hour_{hour}"
            if key not in day_bookings and not is_blocked(selected_date, court, hour):
                day_bookings[key] = name
                bookings[date_str] = day_bookings
                save_bookings(bookings)
        return redirect(url_for('index', date=date_str))

    hours = list(range(7, 22))
    next_7_days = [(selected_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

    return render_template(
        'index.html',
        date_str=date_str,
        hours=hours,
        courts=courts,
        bookings=day_bookings,
        next_7_days=next_7_days,
        is_blocked=lambda d, c, h: is_blocked(datetime.strptime(d, '%Y-%m-%d'), c, h)
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
