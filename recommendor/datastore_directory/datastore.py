import os

project_id = os.getenv('GCLOUD_PROJECT')

from google.cloud import datastore
from flask import current_app

datastore_client = datastore.Client()

def save_credentials(fullname, email, name, hashpass):
    kind = "users"
    users_key = datastore_client.key(kind,name)
    users = datastore.Entity(key=users_key)
    users["fullname"] = fullname
    users["email"] = email
    users["username"] = name
    users["password"] = hashpass
    datastore_client.put(users)

def save_data(name1,lang, year):
    client = datastore.Client()
    # Entity to update Kind and ID. Replace this values 
    # with ones that you know that exist.
    entity_kind = 'users'
    name = name1
    key = client.key(entity_kind, name)

    result = client.get(key)
    print(result)

    entity = client.get(key)
    entity.update({
        'language' : lang,
        'year' : year,
        })
    client.put(entity)

def get_user(name):
    client = datastore.Client()
    # Entity to update Kind and ID. Replace this values 
    # with ones that you know that exist.
    entity_kind = 'users'
    key = client.key(entity_kind, name)
    result = client.get(key)
    print(result)
    return result

def save_preference(name1, Action, Comedy, Drama, Horror, Sci_Fi):
    client = datastore.Client()
    # Entity to update Kind and ID. Replace this values 
    # with ones that you know that exist.
    entity_kind = 'users'
    name = name1
    key = client.key(entity_kind, name)

    result = client.get(key)
    print(result)

    entity = client.get(key)
    entity.update({
        'action' : Action,
        'comedy' : Comedy,
        'drama' : Drama,
        'horror' : Horror,
        'sci-fi' : Sci_Fi,
        
        })
    client.put(entity)
