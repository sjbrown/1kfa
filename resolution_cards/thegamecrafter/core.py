#! /usr/bin/env python

import os
import requests

base_url="https://www.thegamecrafter.com/api"

session = None

def post(endpoint, files=None, **kwargs):
    if session is None:
        raise Exception('Must be logged in before post() can be called')

    url = base_url
    if not endpoint.startswith('/'):
        url += '/'
    url += endpoint

    params = kwargs
    params['session_id'] = session['id']
    print 'POST', url, params.keys()
    response = requests.post(url, params=params, files=files)

    if not str(response.status_code).startswith('2'):
        print 'FAIL', response
        print 'FAIL', response.json()
        raise Exception('Request failed')

    return response.json()['result']

def get(endpoint, **kwargs):
    if session is None:
        raise Exception('Must be logged in before get() can be called')

    url = base_url
    if not endpoint.startswith('/'):
        url += '/'
    url += endpoint

    params = kwargs
    params['session_id'] = session['id']
    print 'GET', url, params.keys()
    response = requests.get(url, params=params)
    if not str(response.status_code).startswith('2'):
        print 'FAIL', response
        print 'FAIL', response.json()
        raise Exception('Request failed')
    return response.json()['result']


def login():
    global session
    params = {
        'api_key_id': os.environ.get('THEGAMECRAFTER_PUBLIC_KEY'),
        'username' : os.environ.get('THEGAMECRAFTER_USER'),
        'password': os.environ.get('THEGAMECRAFTER_PASSWORD'),
    }
    response = requests.post(base_url + "/session", params=params)
    print 'LOGIN RESPONSE', response.json()
    if response.status_code == 200:
        session = response.json()['result']
    else:
        if not os.environ.get('THEGAMECRAFTER_PUBLIC_KEY'):
            print 'You need to set the env variable THEGAMECRAFTER_PUBLIC_KEY'
        if not os.environ.get('THEGAMECRAFTER_USER'):
            print 'You need to set the env variable THEGAMECRAFTER_USER'
        if not os.environ.get('THEGAMECRAFTER_PASSWORD'):
            print 'You need to set the env variable THEGAMECRAFTER_PASSWORD'
        raise Exception('Could not log in. Check your environment variables')

    return get('/user/' + session['user_id'])

def new_game(user, name):
    return post('game',
        name=name,
        designer_id=user.designer_id,
        description='Automatically created (%s)' % name,
    )

def new_folder(user, asset_name, parent_id=None):
    if parent_id is None:
        parent_id = user['root_folder_id']
    return post('folder',
        name=asset_name,
        user_id=user.id,
        parent_id=parent_id,
    )

def new_file(filepath, folder_id):
    if not os.path.isfile(filepath):
        raise Exception('Not a file: %s' % filepath)
    fp = file(filepath)
    filename = os.path.basename(filepath)
    return post('file', files={'file':fp}, name=filename, folder_id=folder_id)

