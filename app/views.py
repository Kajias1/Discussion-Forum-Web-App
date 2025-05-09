from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from enum import Enum

import bleach
import re
import os

from app import db
from forms import RegistrationForm, LoginForm, PostCreationForm, AnswerCreationForm, ProfileEditForm
from models import User, Post, Answer

main = Blueprint('main', __name__)

@main.route('/')
def index():
    user = current_user
    posts = Post.query.all()

    return render_template('index.html', user=user, posts=posts)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('Username or email already exists. Please choose another.', 'danger')
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Something went wrong while creating your account. Please try again.', 'danger')
            return render_template('register.html', form=form)

        login_user(new_user)
        flash('You account has been created!', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index')) 

@main.route('/create_post', methods=["GET", "POST"])
def create_post():
    user = current_user
    if not user.is_authenticated:
        return redirect(url_for('main.login')) 

    form = PostCreationForm()

    if request.method == "POST":
        form.content.data = request.form.get("content")

        allowed_tags = ['b', 'i', 'u', 'a', 'code', 'pre', 'ul', 'ol', 'li', 'blockquote', 'strong', 'em']
        form.content.data = bleach.clean(form.content.data, tags=allowed_tags, strip=True)

        if not form.title.data.strip():
            flash("Title cannot be empty", "danger")
            return render_template('create_post.html', form=form)

        if not form.content.data.strip() or form.content.data == "<p><br></p>" or form.content.data == "<div><br></div>":
            flash("Content cannot be empty", "danger")
            return render_template('create_post.html', form=form)

    if form.validate_on_submit():
        new_post = Post(
            author_id=user.get_id(),
            title=form.title.data,
            content=form.content.data
        )
        
        db.session.add(new_post)
        db.session.commit()

        flash('Post has been created!', 'success')
        return redirect(url_for('main.index')) 

    return render_template('create_post.html', form=form, user=user)

@main.route('/post/<int:post_id>', methods=["GET", "POST"])
def post_view(post_id: int):
    user = current_user
    post = Post.query.get_or_404(post_id)

    if user.is_authenticated and user not in post.views:
        post.views.append(user)
        db.session.commit()

    answerForm = AnswerCreationForm()
    if answerForm.validate_on_submit():
        if not user.is_authenticated:
            flash('You have to sign in before leaving answers', 'info')
            return redirect(url_for('main.post_view', post_id=post_id))

        new_answer = Answer(
            author_id=user.get_id(),
            post_id=post_id,
            content=answerForm.content.data
        )
        db.session.add(new_answer)
        db.session.commit()
        flash('Question answered', 'info')
        return redirect(url_for('main.post_view', post_id=post_id))

    return render_template('post_view.html', post=post, answerForm=answerForm, user=user)

class ProfilePageState(Enum):
    VIEW = 'view'
    SETTINGS = 'settings'


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    user = current_user

    if not user.is_authenticated:
        return redirect(url_for('main.login')) 

    state = request.args.get('state', ProfilePageState.VIEW.value)
    form = ProfileEditForm()

    if state == ProfilePageState.SETTINGS.value:
        if form.validate_on_submit():
            user.username = form.username.data
            user.bio = form.bio.data

            # Profile picture upload handling
            if form.profile_picture.data:
                filename = secure_filename(form.profile_picture.data.filename)
                filepath = os.path.join(current_app.root_path, 'static/images/profile_images', filename)
                form.profile_picture.data.save(filepath)
                user.profile_photo = filename

            db.session.commit()
            flash('Profile updated', 'success')
            return redirect(url_for('main.profile_view', state=ProfilePageState.VIEW.value))

        form.username.data = user.username
        form.bio.data = user.bio

    return render_template('profile.html', user=user, state=state, form=form)

@main.route("/profile_view/<int:user_id>", methods=['GET'])
def profile_view(user_id: int):
    user = current_user
    view_user = User.query.get_or_404(user_id)

    if not view_user:
        flash('Such user does not exist', 'info')
        return redirect(url_for('main.index')) 

    return render_template('profile_view.html', user=user, view_user=view_user)
