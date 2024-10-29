from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the SQLAlchemy database instance
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Model for storing user details."""
    __tablename__ = 'users'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    # Username, unique for each user
    username = db.Column(db.String(150), unique=True, nullable=False)
    # Password hash for security
    password_hash = db.Column(db.String(200), nullable=False)

    def __init__(self, username, password):
        """Initializes a new user with a hashed password."""
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_user(username, password):
        """Creates a new user and adds to the database."""
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def get(username):
        """Fetch a user by username."""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_id(user_id):
        """Fetch a user by their user ID."""
        return User.query.get(user_id)

class UserMovies(db.Model):
    """Model for storing user's movies in watchlist or favorites."""
    __tablename__ = 'user_movies'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    # Foreign key referencing the user who added this movie
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # ID of the movie (from an external API or source)
    movie_id = db.Column(db.Integer, nullable=False)
    # Category to differentiate between watchlist and favorites
    category = db.Column(db.String(50), nullable=False)  # 'watchlist' or 'favorites'

    # Relationship to easily access user's movies
    user = db.relationship('User', backref=db.backref('user_movies', lazy=True))
