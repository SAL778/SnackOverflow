import requests


def get_remote_request(url, host):
    
    # Based on team name, set the authorization
    if host.startswith('http://remote-nodeA:8000'):
        headers = {'Authorization': 'Basic YWRtaW46YWR'}
    elif host.startswith('http://remote-nodeB:8000'):
        headers = {'Authorization': 'Basic YWR'}
    else:
        headers = {}


    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None