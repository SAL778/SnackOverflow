import requests
from .models import Node

def get_request_remote(host_url, path):

    node = Node.objects.filter(host_url=host_url, is_active=True).first()
    if node != None:
        print("Node from get_request_remote: "+ node.team_name)
    if node:
        request_url = f"{node.api_url}{path}"
        try:
            response = requests.get(request_url, headers={'Authorization': f'Basic {node.base64_authorization}'})
        except requests.exceptions.RequestException as e:
            print("Request failed for node: ", node.team_name, node.api_url)
            print("Error: ", e)
            return None

        if response.status_code == 403:
            print("Authorization failed for node: ", node.team_name, node.api_url)

        elif response.status_code == 500:
            print("Internal server error for node: ", node.team_name, node.api_url)

        elif response.status_code == 404:
            print(f"Requested url {request_url} not found for node: ", node.team_name, node.api_url)
        
        # add more error code handling as needed
        return response
            
    else:
        print("No active node found for host: ", host_url)
        return None
    

def post_request_remote(host_url, path, data):
    
        node = Node.objects.filter(host_url=host_url, is_active=True).first()
    
        if node:
            request_url = f"{node.api_url}{path}"
            try:
                response = requests.post(request_url, json=data, headers={'Authorization': f'Basic {node.base64_authorization}'})
            except requests.exceptions.RequestException as e:
                print("Request failed for node: ", node.team_name, node.api_url)
                print("Error: ", e)
                return None
    
            if response.status_code == 403:
                print("Authorization failed for node: ", node.team_name, node.api_url)
    
            elif response.status_code == 500:
                print("Internal server error for node: ", node.team_name, node.api_url)
    
            elif response.status_code == 404:
                print(f"Requested url {request_url} not found for node: ", node.team_name, node.api_url)
            
            # add more error code handling as needed
                
            return response
                
        else:
            print("No active node found for host: ", host_url)
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