from flask import render_template, Blueprint, session, redirect, url_for, request, flash
from flask_login import current_user, login_required, login_user, logout_user
from hashlib import sha256
from werkzeug.security import check_password_hash, generate_password_hash


from .models import User

auth = Blueprint("auth", __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('home.html', user=current_user)
    else:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.objects(username=username).first()        

            if user :
                if check_password_hash(user.password, password):
                #if sha256(password.encode("utf-8")).hexdigest()==user['password']:
                    login_user(user, remember=True)
                    #session['username'] = username
                    return redirect(url_for('views.home_page'))
                else:
                    flash('Mauvais mot de passe !', category='error')

            else:
                return render_template('login.html', error="Nom d'utilisateur incorrect")
        return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.objects(username=username).first()
                
        if user:
            return render_template('register.html', error='Cet utilisateur existe déjà')
        
        if len(username) < 4:
            return render_template('register.html', error='Le nom d\'utilisateur doit contenir au moins 4 caractères')
        
        if len(password) < 4:
            return render_template('register.html', error='Le mot de passe doit contenir au moins 4 caractères')
        
        if password == confirm_password:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            #hashed_password = sha256(password.encode("utf-8")).hexdigest()
            new_user = User(username=username, password=hashed_password, roles='guest')
            new_user.save()
            return redirect(url_for('auth.login'))
        else:
            return render_template('register.html', error='Les mots de passe ne correspondent pas')
    return render_template('register.html')

@auth.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        user = User.objects(username=username).first()
                
        if user:
            return render_template('register.html', error='Cet utilisateur existe déjà')
        
        if len(username) < 4:
            return render_template('register.html', error='Le nom d\'utilisateur doit contenir au moins 4 caractères')
        
        if len(password) < 4:
            return render_template('register.html', error='Le mot de passe doit contenir au moins 4 caractères')
        
        if password == confirm_password:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            #hashed_password = sha256(password.encode("utf-8")).hexdigest()
            new_user = User(username=username, password=hashed_password, roles='admin')
            new_user.save()
            return redirect(url_for('auth.login'))
        else:
            return render_template('register_admin.html', error='Les mots de passe ne correspondent pas')
    return render_template('register_admin.html')

@auth.route('/logout')
# @login_required
def logout():
    logout_user()
    flash('Déconnecté avec succès !', category='success')
    return redirect(url_for('auth.login'))