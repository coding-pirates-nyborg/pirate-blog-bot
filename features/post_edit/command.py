# features/post_edit/command.py
from slack_bolt import App
from utils.github import get_posts, get_folder_hierarchy
import os

def get_folder_hierarchy(posts):
    """Convert flat list of posts into a hierarchical folder structure"""
    hierarchy = {}
    for post in posts:
        path_parts = post["path"].split('/')
        current_dict = hierarchy
        
        # Build the folder hierarchy
        for part in path_parts[:-1]:  # Skip the file name
            if part not in current_dict:
                current_dict[part] = {"files": [], "folders": {}}
            current_dict = current_dict[part]["folders"]
        
        # Add the file to its folder
        current_dict = hierarchy
        for part in path_parts[:-1]:
            current_dict = current_dict[part]["folders"]
        current_dict["files"].append(post)
    
    return hierarchy

def create_folder_blocks(folder_name, folder_content, current_path=""):
    """Create blocks for a folder and its contents"""
    blocks = []
    full_path = os.path.join(current_path, folder_name) if current_path else folder_name
    indent_level = len(current_path.split('/')) if current_path else 0
    
    # Add folder header
    blocks.extend([
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{'  ' * indent_level}📁 *{folder_name}*"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "▼ Show Files",
                    "emoji": True
                },
                "value": full_path,
                "action_id": f"expand_folder_{full_path}"
            }
        },
        {
            "type": "context",
            "block_id": f"folder_content_{full_path}",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "_Click to show contents_"
                }
            ]
        },
        {
            "type": "divider"
        }
    ])
    
    return blocks

def register(app: App):
    @app.command("/edit")
    def edit_post(ack, body, client):
        print("Starting edit_post command")
        ack()
        
        try:
            # Get list of posts from GitHub using existing function
            posts = get_posts()
            print(f"Found {len(posts)} posts")
            
            # Create hierarchical folder structure
            hierarchy = get_folder_hierarchy(posts)
            print(f"Created hierarchy: {hierarchy}")
            
            # Create blocks for the modal
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Select a post to edit",
                        "emoji": True
                    }
                }
            ]
            
            # Add blocks for each folder in the _posts directory
            for folder_name, folder_content in sorted(hierarchy["_posts"]["folders"].items()):
                blocks.extend(create_folder_blocks(folder_name, folder_content))
            
            print("Opening selection modal")
            # Open the modal
            client.views_open(
                trigger_id=body["trigger_id"],
                view={
                    "type": "modal",
                    "callback_id": "post_selection_modal",
                    "title": {"type": "plain_text", "text": "Edit Post", "emoji": True},
                    "blocks": blocks
                }
            )
            
        except Exception as e:
            print(f"Error in edit_post command: {str(e)}")
            client.chat_postMessage(
                channel=body["user_id"],
                text=f"❌ Failed to list posts: {str(e)}"
            )