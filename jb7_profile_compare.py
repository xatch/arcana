# Uses aracana API to compare profiles and suggest tournament picks

import requests


def open_session(token):
    session = requests.Session()
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer %s' % token}
    session.headers.update(headers)
    return session


def get(session, call):
    res = session.get(call)
    data = res.json()
    return data


def identify_my_profile(session, root):
    data1 = get(session, root)
    call = data1['_links']['my_profile']
    data2 = get(session, call)
    pid = data2['_id']
    print 'Your ID: %s' % pid
    return pid


def identify_rival_profile(session, root):
    name = raw_input('Name of rival profile: ')
    pid = ''
    data = get(session, root + 'profiles/')
    profiles = data['_items']
    for profile in profiles:
        if name.upper() in profile['name']:
            pid = profile['_id']
    if pid:
        print 'Their ID: %s' % pid
        return pid
    else:
        raise RuntimeError('No matching profile name found.')


def build_overlap(session, root, id_me, id_you):
    data_me = get(session, root + 'player_bests/?profile_id=%s' % id_me)
    data_you = get(session, root + 'player_bests/?profile_id=%s' % id_you)
    overlap = []
    for i in data_me['_items']:
        for j in data_you['_items']:
            if i['chart_id'] == j['chart_id']:
                overlap.append({'chart': i['chart_id'], 'music': i['music_id'],
                                'me': i['score'], 'you': j['score'], 'diff': i['score'] - j['score']})
    return overlap


def get_full_db(session, root, data_type):
    data = get(session, root + '%s/' % data_type)
    result = dict()
    while True:
        if data_type == 'music':
            for song in data['_items']:
                result[song['_id']] = '%s (%s)' % (song['title'], song['artist'])
        elif data_type == 'charts':
            for chart in data['_items']:
                result[chart['_id']] = '%s [%s]' % (chart['chart_type'], chart['rating'])
        else:
            raise Exception('Unknown DB type')
        if 'None' in str(data['_links']['_next']):
            break
        else:
            data = get(session, data['_links']['_next'])
    return result


def main():
    # Set API root
    root = 'https://arcana.nu/api/v1/jb/7/'
    # Ask for API token
    token = raw_input('Enter API token: ')
    # Open API session
    session = open_session(token)
    # Find your profile
    id_me = identify_my_profile(session, root)
    # Find their profile
    id_you = identify_rival_profile(session, root)
    score_data = sorted(build_overlap(session, root, id_me, id_you), key=lambda x: x['diff'], reverse=True)
    num = len(score_data)
    print '%s charts found in common' % num
    # Get all music
    music = get_full_db(session, root, 'music')
    # Get all charts
    charts = get_full_db(session, root, 'charts')
    # Show best
    for i in range(0, num):
        score = score_data[i]
        print '[#%s]' % (i+1)
        print 'Song: %s' % music[score['music']]
        try:
            print 'Chart: %s' % charts[score['chart']]
        except KeyError:
            print 'Chart: ???'
        print 'You: %s' % score['me']
        print 'Them: %s' % score['you']
        print 'Score differential: %s' % score['diff']
        print


if __name__ == '__main__':
    main()