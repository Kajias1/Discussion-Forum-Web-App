from flask_login import UserMixin
from datetime import datetime

from app import db, login_manager

# Relation table between users and posts
post_views = db.Table('post_views',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('viewed_at', db.DateTime, default=datetime.utcnow)
)

# User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    bio = db.Column(db.String(200))
    
    profile_photo = db.Column(db.String(255), nullable=True, default='default_avatar.png')

    def __init__(self, username, email, password=None, password_hash=None):
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
        elif password_hash:
            self.password_hash = password_hash

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

# Post model
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='posts', lazy=True)
    views = db.relationship('User', secondary=post_views, backref='viewed_posts')

    def __init__(self, author_id, title, content):
        self.author_id = author_id
        self.title = title
        self.content = content

    def __repr__(self):
        return f'<Post {self.title}>'

# Answer model
class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='answers', lazy=True)
    post = db.relationship('Post', backref='answers', lazy=True)

    def __init__(self, author_id, post_id, content):
        self.author_id = author_id
        self.post_id = post_id
        self.content = content

    def __repr__(self):
        return f'<Post {self.title}>'

# This function tells Flask-Login how to load a user from the database using the user ID stored in the session.
# It is called automatically during a request when the user needs to be reloaded.
# The @login_manager.user_loader decorator registers this function with Flask-Login.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

