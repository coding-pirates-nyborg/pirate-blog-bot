# utils/github.py
import os
from api import list_repository_files

def get_posts():
    """Get list of posts from the repository"""
    # List files in a directory
    files = list_repository_files(os.environ.get("BLOG_REPOSITORY"), "_posts/")
    # Transform the files into the format we need
    posts = [
        {
            "name": file["name"],
            "path": file["path"]
        }
        for file in files
    ]
    return posts