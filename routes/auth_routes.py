import uuid
import logging
import time
from flask import Blueprint, request, session, redirect, url_for, flash, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from services.user_store import users, password_reset_tokens

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            email = email.lower()
        password = request.form.get('password')
        user = users.get(email)

        if user and check_password_hash(user['password'], password):
            session['user_id'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth_bp.login'))
    return render_template('login.html')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    if email:
        email = email.lower()
    password = request.form.get('password')

    if not email:
        flash('Email is required', 'error')
        return redirect(url_for('auth_bp.login'))

    if not password:
        flash('Password is required', 'error')
        return redirect(url_for('auth_bp.login'))

    if email in users:
        flash('Email already in use', 'error')
        return redirect(url_for('auth_bp.login'))

    users[email] = {
        'name': name,
        'password': generate_password_hash(password)
    }
    session['user_id'] = email
    return redirect(url_for('dashboard'))

@auth_bp.route('/guest-login')
def guest_login():
    guest_id = f"guest_{uuid.uuid4()}"
    session['user_id'] = guest_id
    logger.info(f"Guest login: {guest_id}")
    return redirect(url_for('dashboard'))

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    if email:
        email = email.lower()

    if email in users:
        token = str(uuid.uuid4())
        # Store email and expiration (1 hour)
        password_reset_tokens[token] = {
            "email": email,
            "expires": time.time() + 3600
        }

        # Cleanup expired tokens
        current_time = time.time()
        for t in list(password_reset_tokens.keys()):
            data = password_reset_tokens.get(t)
            if data:
                if isinstance(data, dict) and data.get("expires", 0) < current_time:
                    password_reset_tokens.pop(t, None)
                elif not isinstance(data, dict): # Handle legacy or malformed
                     password_reset_tokens.pop(t, None)

        reset_link = url_for('auth_bp.reset_password', token=token, _external=True)
        logger.info(f"Password reset link for {email}: {reset_link}")
    return redirect(url_for('auth_bp.forgot_password_confirm'))

@auth_bp.route('/forgot-password-confirm')
def forgot_password_confirm():
    return render_template('forgot_password_confirm.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    token_data = password_reset_tokens.get(token)

    if not token_data or not isinstance(token_data, dict) or token_data.get("expires", 0) < time.time():
        flash('Invalid or expired password reset link.', 'error')
        # Clean up if expired
        if token_data:
             password_reset_tokens.pop(token, None)
        return redirect(url_for('auth_bp.login'))

    email = token_data['email']

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html')

        users[email]['password'] = generate_password_hash(password)
        password_reset_tokens.pop(token, None)
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('auth_bp.login'))

    return render_template('reset_password.html')
