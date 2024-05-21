from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .models import Info

views = Blueprint("views", __name__)

@views.route('/')
@views.route('/home_page')
def home_page():
    return render_template('home.html')

@views.route('/menu_1')
@login_required
def menu_1():
    return render_template('menu_1.html', user=current_user)

@views.route('/menu_2', methods=['GET', 'POST'])
@login_required
def menu_2():
    user = current_user
    
    if request.method == 'POST':
        sexe = request.form.get('sexe')
        nom = request.form.get('nom')
        poids = request.form.get('poids')
        taille = request.form.get('taille')
        date = request.form.get('date')

        info_utilisateur = Info.objects(user=user.id).first()
        
        if info_utilisateur is None:
            nouveau_guess = Info(
                user=user,
                sexe=sexe,
                nom=nom,
                poids=poids,
                taille=taille,
                date=date
            )
            nouveau_guess.save()

        else:
            if sexe:
                info_utilisateur.sexe = sexe
            if nom:
                info_utilisateur.nom = nom
            if poids:
                info_utilisateur.poids = poids
            if taille: 
                info_utilisateur.taille = taille
            if date:
                info_utilisateur.date = date
                
            # Enregistrer les modifications
            info_utilisateur.save()            

        flash('Guess sauvegardée avec succès !')

        return redirect(url_for('views.menu_2'))
    return render_template('menu_2.html', user=current_user)

@views.route('/menu_3')
@login_required
def menu_3():
    return render_template('menu_3.html', user=current_user)

@views.route('/admin_section')
@login_required
def admin_section():
    return render_template('admin_section.html', user=current_user)