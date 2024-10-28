from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Sample data for watchlist and favorites
favorites = []
watchlist = []
history = []

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Movie details route
@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    movie = {
        'id': movie_id,
        'title': 'Sample Movie',
        'release_date': '2024-01-01',
        'vote_average': 8.5,
        'overview': 'This is a sample movie description.',
        'poster': 'https://via.placeholder.com/150'
    }
    return render_template('movie_details.html', movie=movie)

# Route for favorites page
@app.route('/favorites')
def favorites_page():
    return render_template('favorites.html', favorites=favorites)

# Route for watchlist page
@app.route('/watchlist')
def watchlist_page():
    return render_template('watchlist.html', watchlist=watchlist)

# API endpoint to add a movie to favorites
@app.route('/api/favorites/add/<int:movie_id>', methods=['POST'])
def add_to_favorites(movie_id):
    # Assuming you have a function `get_movie_by_id` to retrieve movie details
    movie = get_movie_by_id(movie_id)
    if movie not in favorites:
        favorites.append(movie)
        return jsonify({'status': 'success', 'message': 'Movie added to favorites!'}), 200
    return jsonify({'status': 'fail', 'message': 'Movie already in favorites.'}), 400

# API endpoint to add a movie to watchlist
@app.route('/api/watchlist/add/<int:movie_id>', methods=['POST'])
def add_to_watchlist(movie_id):
    movie = get_movie_by_id(movie_id)
    if movie not in watchlist:
        watchlist.append(movie)
        record_history(movie)  # Record viewing history
        return jsonify({'status': 'success', 'message': 'Movie added to watchlist!'}), 200
    return jsonify({'status': 'fail', 'message': 'Movie already in watchlist.'}), 400

# API endpoint to record viewing history
@app.route('/api/history/add/<int:movie_id>', methods=['POST'])
def add_to_history(movie_id):
    movie = get_movie_by_id(movie_id)
    if movie not in history:
        history.append(movie)
    return '', 204

# Function to get movie details by ID
def get_movie_by_id(movie_id):
    # Placeholder function to retrieve movie details
    # In a real app, you would fetch from your database or API
    return {
        'id': movie_id,
        'title': 'Sample Movie',
        'release_date': '2024-01-01',
        'vote_average': 8.5,
        'overview': 'This is a sample movie description.',
        'poster': 'https://via.placeholder.com/150'
    }

# Function to record movie in history
def record_history(movie):
    if movie not in history:
        history.append(movie)

# POST route to remove a movie from the watchlist
@app.route('/watchlist', methods=['POST'])
def remove_from_watchlist():
    movie_id = int(request.form['movie_id'])
    global watchlist
    watchlist = [movie for movie in watchlist if movie['id'] != movie_id]
    return redirect(url_for('watchlist_page'))

if __name__ == '__main__':
    app.run(debug=True)
