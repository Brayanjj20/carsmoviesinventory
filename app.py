from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'

API_URL = "https://carsmoviesinventoryproject-production.up.railway.app/api/v1/carsmovies?page=0&size=5&sort=carMovieYear,desc"
API_POST_URL = "https://carsmoviesinventoryproject-production.up.railway.app/api/v1/carsmovies"

@app.route('/')
def dashboard():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        # Adjust based on actual API response structure
        if isinstance(data, dict) and "Movies" in data:
            cars_movies = data["Movies"]
        else:
            cars_movies = []
    except requests.RequestException as e:
        cars_movies = []
    # Filter relevant fields
    filtered_data = [
        {
            "id": item.get("id", ""),
            "carMovieName": item.get("carMovieName", ""),
            "carMovieYear": item.get("carMovieYear", ""),
            "duration": item.get("duration", "")
        }
        for item in cars_movies
    ]
    return render_template('dashboard.html', cars_movies=filtered_data)

@app.route('/create_movie', methods=['GET'])
def create_movie():
    return render_template('create_movie.html')

@app.route('/submit_movie', methods=['POST'])
def submit_movie():
    try:
        car_movie_year = request.form.get('carMovieYear')
        if car_movie_year is None or car_movie_year.strip() == '':
            car_movie_year = None
    except ValueError:
        flash('Invalid Car Movie Year.', 'danger')
        return redirect(url_for('create_movie'))

    try:
        duration = int(request.form.get('duration')) if request.form.get('duration') else None
    except ValueError:
        flash('Invalid Duration: must be an integer.', 'danger')
        return redirect(url_for('create_movie'))

    movie_data = {
        "carMovieName": request.form.get('carMovieName'),
        "carMovieYear": car_movie_year,
        "duration": duration
    }
    try:
        response = requests.post(API_POST_URL, json=movie_data)
        response.raise_for_status()
        flash('Movie created successfully!', 'success')
        return redirect(url_for('dashboard'))
    except requests.RequestException as e:
        if e.response is not None:
            try:
                error_message = e.response.json().get('message', e.response.text)
            except Exception:
                error_message = e.response.text
            flash(f'Error creating movie: {error_message}', 'danger')
        else:
            flash(f'Error creating movie: {e}', 'danger')
        return redirect(url_for('create_movie'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)

if __name__ == '__main__':
    app.run(debug=True)
