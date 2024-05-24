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


#ROUTES "LISTE NAISSANCE" -------------------------------------------------------------------------------------------------------------
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
    

#ROUTES "PRONOS" -------------------------------------------------------------------------------------------------------------
@views.route('/menu_2', methods=['GET', 'POST'])
@login_required
def menu_2():
    user = current_user
    
    # Si le user est déjà dans un projet et que je n'ai rien dans la session (parce que je viens de me connecter), je récupère le premier projet dans lequel le user est afin d'ouvrir une session et ne pas avoir à choisir un projet à chaque fois que je me connecte.
    #Si une session est déjà ouverte, je skip cette étape
    if 'selected_project' not in session:
        user_in_project = Project.objects(users__contains=user.id)
        if user_in_project:
            first_project = user_in_project.first() 
            first_project_id = first_project.id
            
            # Ajouter les données du premier projet trouvé dans la session
            session['selected_project'] = {
                'id': str(first_project_id),
                'name': first_project.name
            }
    
    try:
        current_project_id = session['selected_project']['id'] #J'ai l'id du projet actuellement sauvegardé dans la session
        current_project = Project.objects(id=current_project_id).first() #J'ai l'objet Project actuellement sauvegardé dans la session
        pronostics_for_current_project = current_project.pronostic #J'ai la liste des pronostics pour le projet actuellement sauvegardé dans la session
        
        if pronostics_for_current_project : #J'ai au moins 1 pronostic pour le projet sélectionné

            if user.pronostic : #Si le user actuel a déjà un pronostic, peut-importe sur quel projet

                for pronostic in user.pronostic:

                    if pronostic in pronostics_for_current_project: #Si le pronostic du user actuel est déjà lié au projet actuellement sauvegardé dans la session
                        pronostic_utilisateur = Pronostic.objects(id=pronostic).first() #J'ai l'objet Pronostic actuellement sauvegardé dans la session
                        
                        #Je récupère les datas pour les envoyer dans le html et afficher les données déjà saisies
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
                            return render_template('menu_2.html', user=current_user, **result) #** permet de passer les données du dictionnaire result en argument de la fonction render_template
            

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


#ROUTES "PHOTOS" -------------------------------------------------------------------------------------------------------------
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


#ROUTES "MON COMPTE" -------------------------------------------------------------------------------------------------------------
@views.route('/my_account')
@login_required
def my_account():

    admin_id = current_user.id #J'ai l'id du user actuellement connecté
    project = Project.objects(admin=admin_id).first() #J'ai l'objet project pour lequel le user actuel est l'admin
    
    user = current_user
    user_in_project = Project.objects(users__contains=user.id) 
    count_projects = user_in_project.count()
    
  
    
    if project : #Si le user actuel est l'admin d'un projet
        project_id = project.id
        project_name = project.name
        
        user_is_admin = True
        return render_template('my_account.html', user=current_user, project_id=project_id, project_name=project_name, user_is_admin=user_is_admin, count_projects=count_projects)

    else: #Si le user actuel n'est pas l'admin d'un projet
        user_is_admin = False
        
        return render_template('my_account.html', user=current_user, user_is_admin=user_is_admin, count_projects=count_projects)
   
@views.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        
        admin_id = current_user.id
        
        new_project = Project(
            name=project_name,
            admin=admin_id,
            users=[admin_id]
        )
        new_project.save()
        new_project_id = new_project.id
        new_project_name = new_project.name
        
        #Je viens de créer un nouveau projet, on bascule la session vers celui-ci
        session['selected_project'] = {
                'id': str(new_project_id),
                'name': new_project_name
            }
        
        flash(f'Projet "{new_project.name}" créé avec succès !', category='success')
        return redirect(url_for('views.home_page'))
        
    return render_template('create_project.html', user=current_user)

@views.route('/my_account', methods=['GET', 'POST'])
@login_required
def join_project():
    if request.method == 'POST':
        project_to_join_link = request.form.get('project_to_join')
        
        try: #je gère les erreurs notamment si je n'ai pas de "=" dans le lien
            project_to_join_id = project_to_join_link.split('=')[1].strip()[:24] #je récupère les 24 premiers caractères après le "="
            
            project_exist = Project.objects(id__contains=project_to_join_id) #Je vérifie si l'id fourni fait partie des id projets existants
            
            if project_exist :
                project_to_join = Project.objects(id=project_to_join_id).first()
                project_to_join_name = Project.objects(id=project_to_join_id).first().name
            
                if current_user.id in project_to_join.users:
                    flash(f'Vous avez déjà rejoint le projet "{project_to_join_name}"', category='error')
                    return redirect(url_for('views.my_account'))
                
                else:
                    project_to_join.users.append(current_user.id)
                    project_to_join.save()
                    
                    project_to_join_id = project_to_join.id
                    project_to_join_name = project_to_join.name
                    
                    session['selected_project'] = {'id': project_to_join_id, 'name': project_to_join_name}

                    flash(f'Vous avez rejoint le projet "{project_to_join_name}"', category='success')
                    return redirect(url_for('views.home_page'))

            else:
                flash('Le projet que vous souhaitez rejoindre n\'existe pas', category='error')
                return redirect(url_for('views.my_account'))
            
        except (IndexError):
            flash('Le projet que vous souhaitez rejoindre n\'existe pas', category='error')
            return redirect(url_for('views.my_account'))
        
    else:
        return redirect(url_for('views.home_page'))

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

@views.route('/delete_project', methods=['POST'])
@login_required
def delete_project():
    # Récupérer le projet actuel et le supprimer de la base de données

    admin_id = current_user.id #J'ai l'id de ce user
    
    project = Project.objects(admin=admin_id).first() #J'ai l'objet project que je souhaite supprimer pour lequel le user actuel est l'admin
    
    project.delete() #Je supprime le projet de la collection des projets
    
    session.clear()
    
    #Je vais basculer la session sur la première que je trouve pour le user actuel

    user_in_project = Project.objects(users__contains=admin_id)
    if user_in_project:
        first_project = user_in_project.first() 
        first_project_id = first_project.id
        
        # Ajouter les données du premier projet trouvé dans la session
        session['selected_project'] = {
            'id': str(first_project_id),
            'name': first_project.name
            }
    else:
        flash("Veuillez créer ou rejoindre un projet avant d'accéder aux pronostics", category='error')
        return redirect(url_for('views.my_account', user=current_user))
    
    flash('Projet supprimé avec succès !', category='success')
    return redirect(url_for('views.home_page'))