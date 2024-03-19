import requests
from .models import Node

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
    
def change_image_url(content, check_url ,api_url):
    if f"![image]({check_url}" in content:
        content = content.replace(f"![image]({check_url}", f"![image]({api_url}")
    return content

def check_content_type_and_change_url(content, nodes, api_url):
    print(content)
    if content.get('contentType') == 'text/markdown':
        for node in nodes:
            content['content'] = change_image_url(content.get('content'), node.api_url, api_url)
    return content

def get_our_host(request):
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    host_url = f"{protocol}://{domain}/api/"

    return host_url

def check_content(post, request):
    nodes = Node.objects.all()

    api_url = get_our_host(request)

    post = check_content_type_and_change_url(post, nodes, api_url)

    return post