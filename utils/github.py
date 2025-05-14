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

def get_folder_hierarchy(posts):
    """Convert flat list of posts into a hierarchical folder structure"""
    try:
        print("Creating folder hierarchy from posts:", posts)  # Debug print
        hierarchy = {"_posts": {"files": [], "folders": {}}}  # Initialize with _posts folder
        
        if not posts:
            print("Warning: No posts found")
            return hierarchy
            
        for post in posts:
            try:
                if not isinstance(post, dict):
                    print(f"Warning: Post is not a dictionary: {post}")
                    continue
                    
                if "path" not in post:
                    print(f"Warning: Post has no path: {post}")
                    continue
                    
                path_parts = post["path"].split('/')
                print(f"Processing post: {post}")
                print(f"Path parts: {path_parts}")
                
                current_dict = hierarchy["_posts"]
                print(f"Starting at _posts folder: {current_dict}")
                
                # Build the folder hierarchy (skip _posts folder)
                for part in path_parts[1:-1]:  # Skip _posts and filename
                    print(f"Processing folder part: {part}")
                    print(f"Current dictionary before: {current_dict}")
                    
                    if "folders" not in current_dict:
                        current_dict["folders"] = {}
                    
                    if part not in current_dict["folders"]:
                        current_dict["folders"][part] = {
                            "files": [],
                            "folders": {}
                        }
                    current_dict = current_dict["folders"][part]
                    print(f"Current dictionary after: {current_dict}")
                
                print(f"Adding file to final folder: {current_dict}")
                if "files" not in current_dict:
                    current_dict["files"] = []
                current_dict["files"].append(post)
                
            except Exception as e:
                print(f"Error processing post {post}: {str(e)}")
                continue
        
        print("Final hierarchy:", hierarchy)
        return hierarchy
        
    except Exception as e:
        print(f"Error in get_folder_hierarchy: {str(e)}")
        return {"_posts": {"files": [], "folders": {}}}  # Return empty hierarchy on error