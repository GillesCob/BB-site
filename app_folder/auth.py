from flask import render_template, Blueprint, session, redirect, url_for, request, flash
from flask_login import current_user, login_required, login_user, logout_user
from hashlib import sha256
from werkzeug.security import check_password_hash, generate_password_hash


from .models import User, Project, Pronostic

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
                    login_user(user, remember=True)
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
            new_user = User(username=username, password=hashed_password)              
                    
            new_user.save()
            return redirect(url_for('auth.login'))
        else:
            return render_template('register.html', error='Les mots de passe ne correspondent pas')
    return render_template('register.html')


@auth.route('/my_account', methods=['GET', 'POST'])
@login_required
def join_project():
    if request.method == 'POST':
        project_to_join_link = request.form.get('project_to_join')
        project_to_join_id = project_to_join_link.split('=')[1]
        project_to_join_id = project_to_join_id.strip()
        
        project_to_join = Project.objects(id=project_to_join_id).first()
        project_to_join_name = Project.objects(id=project_to_join_id).first().name
        
        project_to_join.users.append(current_user.id)
        project_to_join.save()
        
        project_to_join_id = project_to_join.id
        project_to_join_name = project_to_join.name
        
        session['selected_project'] = {'id': project_to_join_id, 'name': project_to_join_name}

        flash(f'Vous avez rejoint le projet "{project_to_join_name}"', category='success')
        return redirect(url_for('views.home_page'))
    else:
        return redirect(url_for('views.home_page'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Déconnecté avec succès !', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/delete', methods=['POST'])
@login_required
def delete_account():
    
    # Récupérer l'utilisateur actuel et le supprimer de la base de données
    user = User.objects(id=current_user.id).first() #Je récupère le user à supprimer
    user_pronostics = Pronostic.objects(user=user) #Je récupère tous les Objets pronostics du user
    pronostic_ids = [pronostic.id for pronostic in user_pronostics] #Je récupère les ids des pronostics sous forme de liste
    for pronostic_id in pronostic_ids:
        Project.objects(pronostic=pronostic_id).update(pull__pronostic=pronostic_id) #Je supprime les pronostics du user dans les projets
    
    user.delete()
    
    #Suppression du user dans les projets
    user_in_project = Project.objects(users=current_user.id)
    user_in_project.update(pull__users=current_user.id)
    
    session.clear()
    flash('Compte supprimé avec succès !', category='success')
    return redirect(url_for('auth.login'))