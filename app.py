from flask import Flask, render_template, request, redirect, url_for, flash
import logging
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'

logging.basicConfig(level=logging.INFO)

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
    import logging
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
    # Validate required fields
    if not movie_data["carMovieName"]:
        flash('Car Movie Name is required.', 'danger')
        return redirect(url_for('create_movie'))
    logging.info(f"Submitting movie data: {movie_data}")
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


from flask import jsonify

from flask import jsonify, request

@app.route('/update_movie/<movie_id>', methods=['PUT'])
def update_movie(movie_id):
    try:
        data = request.get_json()
        car_movie_year = data.get('carMovieYear')
        if car_movie_year is None or (isinstance(car_movie_year, str) and car_movie_year.strip() == ''):
            car_movie_year = None
    except Exception:
        return jsonify({'error': 'Invalid Car Movie Year.'}), 400

    try:
        duration = data.get('duration')
        if duration is not None:
            duration = int(duration)
    except Exception:
        return jsonify({'error': 'Invalid Duration: must be an integer.'}), 400

    movie_data = {
        "carMovieName": data.get('carMovieName'),
        "carMovieYear": car_movie_year,
        "duration": duration
    }
    try:
        put_url = f"{API_POST_URL}/{movie_id}"
        headers = {'Content-Type': 'application/json'}
        response = requests.put(put_url, json=movie_data, headers=headers)
        response.raise_for_status()
        return jsonify({'message': 'Movie updated successfully!'}), 200
    except requests.RequestException as e:
        if e.response is not None:
            try:
                error_message = e.response.json().get('message', e.response.text)
            except Exception:
                error_message = e.response.text
            return jsonify({'error': error_message}), 400
        else:
            return jsonify({'error': str(e)}), 400

@app.route('/delete_movie/<movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    try:
        delete_url = f"{API_POST_URL}/{movie_id}"
        headers = {'Content-Type': 'application/json'}
        response = requests.delete(delete_url, headers=headers)
        response.raise_for_status()
        return jsonify({'message': 'Movie deleted successfully!'}), 200
    except requests.RequestException as e:
        if e.response is not None:
            try:
                error_message = e.response.json().get('message', e.response.text)
            except Exception:
                error_message = e.response.text
            return jsonify({'error': error_message}), 400
        else:
            return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
