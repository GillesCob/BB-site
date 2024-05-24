from flask_login import UserMixin
from mongoengine import Document, StringField, ReferenceField, CASCADE, ListField


   
class User(Document, UserMixin):
    meta = {'collection': 'users_collection'}

    username = StringField(max_length=150, unique=True, required=True)
    password = StringField(max_length=150, required=True)
    roles = StringField(max_length=50, default='guest')
    pronostic = ListField()


class Project(Document):
    meta = {'collection': 'projects_collection'}
    
    name = StringField(max_length=150, unique=True)
    admin = ReferenceField('User', reverse_delete_rule=CASCADE)
    users = ListField()
    pronostic = ListField()


class Pronostic(Document):
    meta = {'collection': 'Pronostic_collection'}
    
    user = ReferenceField('User', reverse_delete_rule=CASCADE)
    project = ReferenceField('Project', reverse_delete_rule=CASCADE)
    sexe = StringField(max_length=150, required=True)
    nom = StringField(max_length=150, required=True)
    taille = StringField(max_length=150, required=True)
    poids = StringField(max_length=150, required=True)
    date = StringField(max_length=150, required=True)