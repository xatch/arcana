# Uses aracana API to compare profiles and suggest tournament picks

import requests


def open_session(token):
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer %s' % token}
    session = requests.Session(headers=headers)
    return session


def get(session, call):
    res = session.get(call)
    data = res.json()
    return data


def main():
    # Set API root
    root = 'https://arcana.nu/api/v1/jb/7/'
    # Ask for API token
    token = raw_input('Enter API token: ')
    # Open API session
    session = open_session(token)
    # Get profiles
    data = get(session, root + 'profiles/')
    if data:
        print 'Retrieved profile list.'
    else:
        raise RuntimeError('Could not log into the API.')
    for profile in data['_items']:
        print profile['name']


if __name__ == '__main__':
    main()