from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import sqlite3
from datetime import datetime, timedelta
import requests
import os
import json
import markdown2 # For rendering markdown in dashboard

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # Replace with a strong secret key

# Database setup
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Create schema.sql if it doesn't exist (for initial setup)
if not os.path.exists(DATABASE):
    with open('schema.sql', 'w') as f:
        f.write("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")
    init_db()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html', now=datetime.utcnow())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']

        if password != password2:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            db.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered. Please use a different email or log in.', 'danger')
            return render_template('register.html')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()

        if user:
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html', now=datetime.utcnow())

@app.route('/contact')
def contact():
    user_name = session.get('user_name', '')
    user_email = session.get('user_email', '')
    return render_template('contact.html', user_name=user_name, user_email=user_email, now=datetime.utcnow())

@app.route('/dashboard', methods=['POST'])
def dashboard():
    if not session.get('logged_in'):
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    source = request.form['source']
    destination = request.form['destination']
    travel_date_str = request.form['date']
    return_date_str = request.form['return']

    # Convert date strings to datetime objects
    travel_date = datetime.strptime(travel_date_str, '%Y-%m-%d')
    return_date = datetime.strptime(return_date_str, '%Y-%m-%d')

    # Calculate number of days
    num_days = (return_date - travel_date).days + 1

    # --- Weather API Integration (Example using Visual Crossing Weather API) ---
    # Replace with your actual API key and desired location parameters
    WEATHER_API_KEY = 'BK9DN9PP2NZPGJNTCTLSGDUUW' # Get your key from https://www.visualcrossing.com/
    weather_data = {}
    try:
        # Fetch weather for the destination
        weather_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{destination}/{travel_date_str}/{return_date_str}?unitGroup=metric&key={WEATHER_API_KEY}&contentType=json"
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status() # Raise an exception for HTTP errors
        weather_data = weather_response.json()
    except requests.exceptions.RequestException as e:
        flash(f"Error fetching weather data: {e}", 'danger')
        # Provide a default or empty weather_data to avoid template errors
        weather_data = {'resolvedAddress': destination, 'days': []}
    except json.JSONDecodeError:
        flash("Error decoding weather data. Invalid JSON response.", 'danger')
        weather_data = {'resolvedAddress': destination, 'days': []}

    # --- Itinerary Generation (Placeholder - Integrate with Bard/LLM here) ---
    # This is a simplified placeholder. In a real application, you'd send
    # source, destination, dates, and potentially weather info to a Bard/LLM API
    # to generate a detailed itinerary.
    # For now, we'll construct a basic markdown string.

    itinerary_plan = f"""
# Your Travel Itinerary to {destination}

## Dates: {travel_date_str} to {return_date_str} ({num_days} days)
**From:** {source}

---

### Day 1: Arrival in {destination} ({travel_date.strftime('%Y-%m-%d')})
*   Arrive at {destination} airport/station.
*   Check into your accommodation.
*   Explore local area, perhaps a nearby market or park.
*   Dinner at a highly-rated local restaurant.

### Day 2: Exploring {destination} ({ (travel_date + timedelta(days=1)).strftime('%Y-%m-%d') })
*   Morning: Visit a prominent landmark (e.g., a historical site, museum).
*   Lunch: Try local cuisine.
*   Afternoon: Engage in an activity (e.g., boat tour, hiking, shopping).
*   Evening: Enjoy a cultural show or a relaxed evening.

"""
    # Add more days dynamically based on num_days
    for i in range(2, num_days):
        current_day = travel_date + timedelta(days=i)
        itinerary_plan += f"""
### Day {i+1}: Adventure in {destination} ({current_day.strftime('%Y-%m-%d')})
*   Morning: Discover a new attraction or revisit a favorite spot.
*   Lunch: Picnic or cafe.
*   Afternoon: Relax or pursue a hobby.
*   Evening: Farewell dinner or a quiet night in.
"""

    itinerary_plan += f"""
### Day {num_days}: Departure from {destination} ({return_date.strftime('%Y-%m-%d')})
*   Morning: Last-minute souvenir shopping or a final breakfast.
*   Check out from accommodation.
*   Depart from {destination}.

---

## Important Notes:
*   **Accommodation:** Book in advance, especially during peak season.
*   **Transportation:** Consider local public transport, taxis, or rental cars.
*   **Food:** Explore local eateries and street food.
*   **Emergency:** Keep local emergency numbers handy.
*   **Flexibility:** This is a suggested itinerary; feel free to adjust it to your preferences!
"""
    # Convert markdown to HTML
    itinerary_html = markdown2.markdown(itinerary_plan)

    return render_template('dashboard.html',
                           weather_data=weather_data,
                           plan=itinerary_html,
                           now=datetime.utcnow())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
