from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.forms import LoginForm
from app.models import User
from app.main import main

# -------------------------------------------------------------------
# PÁGINA DE INICIO PÚBLICA
# -------------------------------------------------------------------
@main.route('/')
def inicio():
    if current_user.is_authenticated:
        # Redirige según el rol
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('cliente.home'))
    return render_template('main/inicio.html')


# -------------------------------------------------------------------
# LOGIN
# -------------------------------------------------------------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Inicio de sesión exitoso.')

            # Redirige según el rol
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('cliente.home'))
        else:
            flash('Usuario o contraseña incorrectos.')
    return render_template('main/login.html', form=form)

# -------------------------------------------------------------------
# LOGOUT
# -------------------------------------------------------------------
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.')
    return redirect(url_for('main.login'))
