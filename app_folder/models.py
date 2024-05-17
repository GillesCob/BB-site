from flask_login import UserMixin
from mongoengine import Document, StringField, ReferenceField, CASCADE


class User(Document, UserMixin):
    meta = {'collection': 'users_collection'}

    username = StringField(max_length=150, unique=True, required=True)
    password = StringField(max_length=150, required=True)
    roles = StringField(max_length=50, default='guest')
    info = ReferenceField('Info')

class Info(Document):
    meta = {'collection': 'Info'}
    
    user = ReferenceField('User', reverse_delete_rule=CASCADE)
    sexe = StringField(max_length=150)
    nom = StringField(max_length=150)
    taille = StringField(max_length=150)
    poids = StringField(max_length=150)
    date = StringField(max_length=150)