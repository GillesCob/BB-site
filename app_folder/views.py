from flask import render_template, Blueprint, redirect, url_for, flash, request, session
from flask_login import current_user, login_required, logout_user
from .models import Pronostic, User, Project

views = Blueprint("views", __name__)


#FONCTIONS -------------------------------------------------------------------------------------------------------------
# Fonction utilisée pour créer un nouveau pronostic dans la route menu_2
def new_pronostic(user, current_project_id, current_project, pronostics_for_current_project):
    if request.method == 'POST':
        sexe = request.form.get('sexe')
        nom = request.form.get('nom')
        poids = request.form.get('poids')
        taille = request.form.get('taille')
        date = request.form.get('date')
                
        new_pronostic = Pronostic(
            user=user,
            sexe=sexe,
            nom=nom,
            poids=poids,
            taille=taille,
            date=date,
            project = current_project_id
        )
        new_pronostic.save()
        
        pronostic_id = new_pronostic.id
        #J'ajoute l'id du nouveau pronostic dans la class User
        current_user.pronostic.append(pronostic_id)
        current_user.save()
        
        #J'ajoute l'id du nouveau pronostic dans la class Project
        current_project.pronostic.append(pronostic_id)
        current_project.save()
        
        pronostic_done = True
        for pronostic in user.pronostic:

            if pronostic in pronostics_for_current_project:
                pronostic_utilisateur = Pronostic.objects(id=pronostic).first()
                prono_sexe = pronostic_utilisateur.sexe
                prono_nom = pronostic_utilisateur.nom
                prono_poids = pronostic_utilisateur.poids
                prono_taille = pronostic_utilisateur.taille
                prono_date = pronostic_utilisateur.date
                            
                flash('Pronostic sauvegardé avec succès !')
                return {
                    'pronostic_done': pronostic_done,
                    'prono_sexe': prono_sexe,
                    'prono_nom': prono_nom,
                    'prono_poids': prono_poids,
                    'prono_taille': prono_taille,
                    'prono_date': prono_date
                }


#ROUTES -------------------------------------------------------------------------------------------------------------
@views.route('/')
@views.route('/home_page',methods=['GET'])
def home_page():
    return render_template('home.html')


@views.route('/menu_1')
@login_required
def menu_1():
    admin_id = current_user.id #Récupération de l'id du user actuellement connecté
    project = Project.objects(admin=admin_id).first() #Récupération de l'objet Project pour lequel le user actuel est l'admin
    
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
    try:
        current_project_id = session['selected_project']['id'] #J'ai l'id du projet actuellement sauvegardé dans la session
        current_project = Project.objects(id=current_project_id).first() #J'ai l'objet Project actuellement sauvegardé dans la session
        pronostics_for_current_project = current_project.pronostic #J'ai la liste des pronostics pour le projet actuellement sauvegardé dans la session
        
        if pronostics_for_current_project : #J'ai au moins 1 pronostic pour le projet sélectionné

            if user.pronostic : #Si le user actuel a déjà un pronostic, peut-importe sur quel projet

                for pronostic in user.pronostic:

                    if pronostic in pronostics_for_current_project: #Si le pronostic du user actuel est déjà lié au projet actuellement sauvegardé dans la session
                        pronostic_utilisateur = Pronostic.objects(id=pronostic).first()
                        prono_sexe = pronostic_utilisateur.sexe
                        prono_nom = pronostic_utilisateur.nom
                        prono_poids = pronostic_utilisateur.poids
                        prono_taille = pronostic_utilisateur.taille
                        prono_date = pronostic_utilisateur.date
                        pronostic_done=True
                        
                        return render_template('menu_2.html', user=current_user, pronostic_done=pronostic_done, prono_sexe=prono_sexe, prono_nom=prono_nom, prono_poids=prono_poids, prono_taille=prono_taille, prono_date=prono_date)

                    else : #Si le pronostic du user actuel n'est pas lié au projet actuellement sauvegardé dans la session, je créé un nouveau pronostic pour ce projet
                        result = new_pronostic(user, current_project_id, current_project, pronostics_for_current_project)
                        if result:
                            return render_template('menu_2.html', user=current_user, **result)
            

        else : #J'arrive ici pour faire pour la première fois un pronostic pour un projet
            result = new_pronostic(user, current_project_id, current_project, pronostics_for_current_project)
            if result:
                return render_template('menu_2.html', user=current_user, **result)
            
    except KeyError:
        flash("Veuillez créer ou rejoindre un projet avant d'accéder aux pronostics", category='error')
        return redirect(url_for('views.my_account', user=current_user))
    
    return render_template('menu_2.html', user=current_user)


@views.route('/update_pronostic', methods=['GET', 'POST'])
@login_required
def update_pronostic():
    user = current_user

    current_project_id = session['selected_project']['id'] #J'ai l'id du projet actuellement sauvegardé dans la session
    current_project = Project.objects(id=current_project_id).first() #J'ai l'objet Project actuellement sauvegardé dans la session
    pronostics_for_current_project = current_project.pronostic #J'ai la liste des pronostics pour le projet actuellement sauvegardé dans la session


    for pronostic in user.pronostic:
        if pronostic in pronostics_for_current_project:
            pronostic_utilisateur = Pronostic.objects(id=pronostic).first()
    
            prono_sexe = pronostic_utilisateur.sexe
            prono_nom = pronostic_utilisateur.nom
            prono_poids = pronostic_utilisateur.poids
            prono_taille = pronostic_utilisateur.taille
            prono_date = pronostic_utilisateur.date
                        
            if request.method == 'POST':
                sexe = request.form.get('sexe_new_proposition')
                nom = request.form.get('nom_new_proposition')
                poids = request.form.get('poids_new_proposition')
                taille = request.form.get('taille_new_proposition')
                date = request.form.get('date_new_proposition')
                
                if sexe:
                    pronostic_utilisateur.sexe = sexe
                if nom:
                    pronostic_utilisateur.nom = nom
                if poids:
                    pronostic_utilisateur.poids = poids
                if taille: 
                    pronostic_utilisateur.taille = taille
                if date:
                    pronostic_utilisateur.date = date
                    
                # Enregistrer les modifications
                pronostic_utilisateur.save()
                
                pronostic_done = True
                prono_sexe = pronostic_utilisateur.sexe
                prono_nom = pronostic_utilisateur.nom
                prono_poids = pronostic_utilisateur.poids
                prono_taille = pronostic_utilisateur.taille
                prono_date = pronostic_utilisateur.date
                
                flash('Pronostic mis à jour avec succès !')
                return render_template('menu_2.html', user=current_user, pronostic_done=pronostic_done, prono_sexe=prono_sexe, prono_nom=prono_nom, prono_poids=prono_poids, prono_taille=prono_taille, prono_date=prono_date)
    
    return render_template('update_pronostic.html', user=current_user, prono_sexe=prono_sexe, prono_nom=prono_nom, prono_poids=prono_poids, prono_taille=prono_taille, prono_date=prono_date)


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
   
   
@views.route('/select_project', methods=['GET', 'POST'])
@login_required
def select_project():
    projects = Project.objects(users__contains=current_user.id)
    projects_dict = {}  
    for project in projects:
        projects_dict[project.name] = str(project.id)
        
        if request.method == 'POST':
            project_id = request.form.get('project_id')
            project_name = Project.objects(id=project_id).first().name
            session['selected_project'] = {'id': project_id, 'name': project_name}
            flash(f'Projet sélectionné avec succès. : {project_name}')
            return redirect(url_for('views.my_account'))
            
    return render_template('select_project.html', user=current_user, projects_dict=projects_dict)


@views.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        
        admin_id = current_user.id
        
        new_project = Project(
            name=project_name,
            admin=admin_id
        )
        new_project.save()
        
        flash(f'Projet "{new_project.name}" créé avec succès !', category='success')
        return redirect(url_for('views.home_page'))
        
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