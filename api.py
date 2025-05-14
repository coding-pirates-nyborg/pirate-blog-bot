import base64
import requests
import os
from datetime import datetime

owner = os.getenv('GITHUB_ORG')
token = os.getenv('GHP_TOKEN')

def post_markdown_file(repo, path, content, commit_message="Add post with api"):
    """
    Create a new file in a GitHub repository
    
    Args:
        owner (str): Repository owner
        repo (str): Repository name
        path (str): Path to create the file (e.g., 'posts/2024/my-post.md')
        content (str): Content to put in the file
        token (str): GitHub personal access token
        branch (str): Branch to commit to (default: main)
        commit_message (str): Optional commit message
    
    Returns:
        response: GitHub API response
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    
    # If no commit message provided, create a default one
    if not commit_message:
        commit_message = f"Add {path} via API"
    
    # Encode content to base64
    content_bytes = content.encode('utf-8')
    content_base64 = base64.b64encode(content_bytes).decode('utf-8')
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    data = {
        "message": commit_message,
        "content": content_base64,
        "branch": 'main'
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code not in [200, 201]:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
        
    return response

def list_repository_files(repo, path=""):
    """
    List files in a GitHub repository path
    
    Args:
        repo (str): Repository name
        path (str): Optional path to list files from (e.g., 'posts/2024/')
    
    Returns:
        list: List of file information dictionaries
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
        
    return response.json()

def delete_posts(repo, posts, commit_message="Delete files via API"):
    """
    Delete multiple files from a GitHub repository
    
    Args:
        repo (str): Repository name
        posts (list): List of posts to delete, containing post information
        commit_message (str): Optional commit message
    
    Returns:
        dict: Dictionary of responses for each deleted file
    """
    responses = {}
    
    for post in posts:
        path = post["value"]  # The path is stored in the "value" field from the Slack response
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # First get the file's SHA
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            responses[path] = f"Error getting SHA: {response.status_code} - {response.text}"
            continue
        
        file_sha = response.json()["sha"]
        
        # Delete the file
        data = {
            "message": commit_message,
            "sha": file_sha,
            "branch": 'main'
        }
        
        response = requests.delete(url, headers=headers, json=data)
        
        if response.status_code != 200:
            responses[path] = f"Error deleting: {response.status_code} - {response.text}"
        else:
            responses[path] = "Successfully deleted"
            
    return responses

def update_post(repo, path, content, commit_message="Update post via API"):
    """
    Update an existing file in a GitHub repository
    
    Args:
        repo (str): Repository name
        path (str): Path to the file to update
        content (str): New content for the file
        commit_message (str): Optional commit message
    
    Returns:
        response: GitHub API response
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # First get the file's SHA
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
    
    file_sha = response.json()["sha"]
    
    # Encode content to base64
    content_bytes = content.encode('utf-8')
    content_base64 = base64.b64encode(content_bytes).decode('utf-8')
    
    data = {
        "message": commit_message,
        "content": content_base64,
        "sha": file_sha,
        "branch": 'main'
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
        
    return response

def get_file_content(repo, path):
    """
    Get the content of a file from GitHub repository
    
    Args:
        repo (str): Repository name
        path (str): Path to the file
    
    Returns:
        str: Decoded content of the file
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
    
    # GitHub returns base64 encoded content
    content_base64 = response.json()["content"]
    content = base64.b64decode(content_base64).decode('utf-8')
    
    return content

def post_file(repo: str, path: str, content: bytes, is_base64: bool = False) -> dict:
    """
    Post a binary file to GitHub repository.
    
    Args:
        repo: Repository name (e.g., 'username/repo')
        path: File path in the repository
        content: Binary content of the file
        is_base64: Whether the content is already base64 encoded
    
    Returns:
        Response from GitHub API
    """
    import base64
    
    headers = {
        "Authorization": f"Bearer {os.environ.get('GHP_TOKEN')}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    # Encode content if not already encoded
    if not is_base64:
        content = base64.b64encode(content).decode('utf-8')
    
    data = {
        "message": f"Add file: {path}",
        "content": content
    }
    
    response = requests.put(
        f"https://api.github.com/repos/{repo}/contents/{path}",
        headers=headers,
        json=data
    )
    
    response.raise_for_status()
    return response.json()

def get_posts_list(repo: str) -> list:
    """Get a list of all posts in the repository"""
    import requests
    import os
    
    print(f"Getting posts from repo: {repo}")  # Debug print
    print(f"Using token: {os.environ.get('GHP_TOKEN')[:4]}...")  # Print first 4 chars of token safely
    
    # Get the contents of the posts directory
    response = requests.get(
        f"https://api.github.com/repos/{repo}/contents/posts",
        headers={'Authorization': f'token {os.environ.get("GHP_TOKEN")}'}
    )
    
    if response.status_code != 200:
        print(f"GitHub API response: {response.status_code} - {response.text}")  # Debug print
        raise Exception(f"Failed to get posts list: {response.text}")
    
    posts = []
    
    # Recursively get all .md files
    def process_contents(contents, current_path=""):
        for item in contents:
            if item["type"] == "file" and item["name"].endswith(".md"):
                posts.append(os.path.join(current_path, item["name"]))
            elif item["type"] == "dir":
                # Get contents of subdirectory
                subdir_response = requests.get(
                    item["url"],
                    headers={'Authorization': f'token {os.environ.get("GHP_TOKEN")}'}
                )
                if subdir_response.status_code == 200:
                    process_contents(
                        subdir_response.json(),
                        os.path.join(current_path, item["name"])
                    )
    
    process_contents(response.json())
    return sorted(posts)



