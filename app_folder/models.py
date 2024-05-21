from flask_login import UserMixin
from mongoengine import Document, StringField, ReferenceField, CASCADE

class Admin(Document, UserMixin):
    meta = {'collection': 'admins_collection'}

    username = StringField(max_length=150, unique=True, required=True)
    password = StringField(max_length=150, required=True)
    roles = StringField(max_length=50, default='admin')
    project_name = StringField(max_length=150, default='My Project')


class User(Document, UserMixin):
    meta = {'collection': 'users_collection'}

    username = StringField(max_length=150, unique=True, required=True)
    password = StringField(max_length=150, required=True)
    roles = StringField(max_length=50, default='guest')
    info = ReferenceField('Info')
    project_name = StringField(max_length=150, default='My Project')

class Info(Document):
    meta = {'collection': 'Info'}
    
    admin = ReferenceField('Admin', reverse_delete_rule=CASCADE)
    user = ReferenceField('User', reverse_delete_rule=CASCADE)
    sexe = StringField(max_length=150)
    nom = StringField(max_length=150)
    taille = StringField(max_length=150)
    poids = StringField(max_length=150)
    date = StringField(max_length=150)