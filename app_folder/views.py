from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import current_user, login_required, logout_user
from .models import Info, User, Project

views = Blueprint("views", __name__)

@views.route('/')
@views.route('/home_page',methods=['GET'])
def home_page():
    return render_template('home.html')


@views.route('/menu_1')
@login_required
def menu_1():
    admin_id = current_user.id #J'ai l'id du user actuellement connecté
    project = Project.objects(admin=admin_id).first() #J'ai l'objet project pour lequel le user actuel est l'admin
    
    if project : #Si le user actuel est l'admin d'un projet
        project_name = project.name
        
        user_is_admin = True
        return render_template('menu_1.html', user=current_user, project_name=project_name, user_is_admin=user_is_admin)

    else: #Si le user actuel n'est pas l'admin d'un projet
        user_is_admin = False
        return render_template('menu_1.html', user=current_user, user_is_admin=user_is_admin)
    

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
    admin_id = current_user.id #J'ai l'id du user actuellement connecté
    project = Project.objects(admin=admin_id).first() #J'ai l'objet project pour lequel le user actuel est l'admin
    
    if project : #Si le user actuel est l'admin d'un projet
        project_name = project.name
        
        user_is_admin = True
        return render_template('menu_3.html', user=current_user, project_name=project_name, user_is_admin=user_is_admin)

    else: #Si le user actuel n'est pas l'admin d'un projet
        user_is_admin = False
        return render_template('menu_3.html', user=current_user, user_is_admin=user_is_admin)

@views.route('/admin_section')
@login_required
def admin_section():
    return render_template('admin_section.html', user=current_user)

@views.route('/my_account')
@login_required
def my_account():

    admin_id = current_user.id #J'ai l'id du user actuellement connecté
    project = Project.objects(admin=admin_id).first() #J'ai l'objet project pour lequel le user actuel est l'admin
    
    if project : #Si le user actuel est l'admin d'un projet
        project_id = project.id
        project_name = project.name
        
        user_is_admin = True
        return render_template('my_account.html', user=current_user, project_id=project_id, project_name=project_name, user_is_admin=user_is_admin)

    else: #Si le user actuel n'est pas l'admin d'un projet
        user_is_admin = False
        return render_template('my_account.html', user=current_user, user_is_admin=user_is_admin)
        
    


@views.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        username = current_user.username
        
        admin = User.objects(username=username).first()
        admin_id = admin.id
        
        if username:
            new_project = Project(
                name=project_name,
                admin=admin_id
            )
            new_project.save()
            
            project_id = str(new_project.id)
            admin.update(push__project=project_id)
            
            return redirect(url_for('views.home_page'))
            
        else:
            print('Admin non trouvé')
        
    return render_template('create_project.html', user=current_user)


@views.route('/delete_project', methods=['POST'])
@login_required
def delete_project():
    # Récupérer le projet actuel et le supprimer de la base de données
    username = current_user.username
    admin = User.objects(username=username).first() #J'ai mon objet user qui est l'admin du projet que je souhaite supprimer
    admin_id = admin.id #J'ai l'id de ce user
    
    project = Project.objects(admin=admin_id).first() #J'ai l'objet project que je souhaite supprimer pour lequel le user actuel est l'admin
    project_id = project.id #J'ai l'id du projet à supprimer
    
    project_id_str = str(project_id)
    admin.project.remove(project_id_str) #Je supprime l'id du projet de la liste des projets de l'admin
    admin.save()

    
    # admin.update(pull__project=project_id) #Je supprime l'id du projet de la liste des projets de l'admin
    
    project.delete() #Je supprime le projet de la collection des projets
    flash('Projet supprimé avec succès !', category='success')
    return redirect(url_for('views.home_page'))