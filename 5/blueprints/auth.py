from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, bcrypt, User
from ai import seed_demo_tasks

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        seed_demo_tasks(user.id)
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id']  = user.id
            session['username'] = user.username
            return redirect(url_for('tasks.dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    from functools import wraps
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    current = request.form['current_password']
    new_pw  = request.form['new_password']
    if user.check_password(current):
        user.set_password(new_pw)
        db.session.commit()
        flash('Password changed successfully.', 'success')
    else:
        flash('Current password is incorrect.', 'danger')
    return redirect(url_for('tasks.profile'))
