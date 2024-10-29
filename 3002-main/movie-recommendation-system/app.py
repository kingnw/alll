from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from auth import auth_blueprint
from models import db, User, UserMovies
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Flask-Login
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# TMDB API Key
API_KEY = '9ba93d1cf5e3054788a377f636ea1033'

# Load user callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Register the auth blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

# TMDB API Functions
def get_top_rated_movies():
    url = f'https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&language=en-US&page=1'
    response = requests.get(url)
    return process_movie_results(response)

def get_new_released_movies():
    url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={API_KEY}&language=en-US&page=1'
    response = requests.get(url)
    return process_movie_results(response)

def get_trending_movies():
    url = f'https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}'
    response = requests.get(url)
    return process_movie_results(response)

def search_movie(movie_title):
    url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}'
    response = requests.get(url)
    return process_movie_results(response)

def get_movie_details(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    response = requests.get(url)
    if response.status_code == 200:
        movie = response.json()
        movie['poster'] = f"https://image.tmdb.org/t/p/w300{movie.get('poster_path', '')}" if movie.get('poster_path') else "https://via.placeholder.com/300x450?text=No+Image"
        return movie
    return None

def get_recommendations(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={API_KEY}'
    response = requests.get(url)
    return process_movie_results(response)

def process_movie_results(response):
    if response.status_code == 200:
        results = response.json().get('results', [])
        for movie in results:
            movie['rating'] = movie.get('vote_average', 'N/A')
            poster_path = movie.get('poster_path')
            movie['poster'] = f"https://image.tmdb.org/t/p/w200{poster_path}" if poster_path else "https://via.placeholder.com/200x300?text=No+Image"
        return results
    return []

# Routes for Watchlist and Favorites
@app.route('/<category>/add/<int:movie_id>', methods=['POST'])
@login_required
def add_movie(category, movie_id):
    if category not in ['watchlist', 'favorites']:
        return "Invalid category", 400
    
    existing_entry = UserMovies.query.filter_by(user_id=current_user.id, movie_id=movie_id, category=category).first()
    if not existing_entry:
        new_entry = UserMovies(user_id=current_user.id, movie_id=movie_id, category=category)
        db.session.add(new_entry)
        db.session.commit()
        flash(f"Movie added to {category}.", "success")
    else:
        flash("Movie is already in your list.", "info")

    return redirect(url_for(f'view_{category}'))

@app.route('/watchlist')
@login_required
def view_watchlist():
    watchlist_movies = UserMovies.query.filter_by(user_id=current_user.id, category='watchlist').all()
    movies = [get_movie_details(movie.movie_id) for movie in watchlist_movies]
    return render_template('watchlist.html', movies=movies, category="Watchlist")

@app.route('/favorites')
@login_required
def view_favorites():
    favorite_movies = UserMovies.query.filter_by(user_id=current_user.id, category='favorites').all()
    movies = [get_movie_details(movie.movie_id) for movie in favorite_movies]
    return render_template('favorites.html', movies=movies, category="Favorites")

# Other Routes

@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    movie = get_movie_details(movie_id)
    if movie:
        return render_template('movie_details.html', movie=movie)
    return "Movie not found", 404

@app.route('/top-rated')
def top_rated():
    top_rated_movies = get_top_rated_movies()
    return render_template('top_rated.html', top_rated_movies=top_rated_movies)

@app.route('/new-released')
def new_released():
    new_released_movies = get_new_released_movies()
    return render_template('new_released.html', new_released_movies=new_released_movies)

@app.route('/')
def index():
    trending_movies = get_trending_movies()
    return render_template('index.html', trending_movies=trending_movies)

@app.route('/recommend', methods=['POST'])
def recommend():
    movie_title = request.form['movie_title']
    search_results = search_movie(movie_title)
    if search_results:
        movie_id = search_results[0]['id']
        recommendations = get_recommendations(movie_id)
        return render_template('index.html', recommendations=recommendations)
    return render_template('index.html', recommendations=[])

# Initialize database tables if they do not exist
with app.app_context():
    db.create_all()

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5001)
