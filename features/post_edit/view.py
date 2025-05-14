# features/post_edit/view.py
from slack_bolt import App
from api import get_file_content, update_post, post_file
from utils.github import get_posts, get_folder_hierarchy
import os
from utils.image_processing import process_image
from datetime import datetime
import time
import requests
import base64
import re

owner = os.environ.get('GITHUB_ORG')
repo = os.environ.get('BLOG_REPOSITORY')

def register(app: App):
    @app.action(re.compile("expand_folder_.*"))
    def handle_folder_expand(ack, body, client):
        ack()
        
        try:
            # Get folder path from action
            folder = body["actions"][0]["value"]
            button_text = body["actions"][0]["text"]["text"]
            is_expanding = "Show" in button_text
            print(f"{'Expanding' if is_expanding else 'Collapsing'} folder: {folder}")
            
            # Get list of posts from GitHub using the utility function
            posts = get_posts()
            
            # Create hierarchical folder structure
            hierarchy = get_folder_hierarchy(posts)
            
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
            
            # Function to recursively build blocks for the folder structure
            def build_folder_blocks(folder_name, folder_content, current_path="", indent_level=0):
                full_path = os.path.join(current_path, folder_name) if current_path else folder_name
                folder_blocks = []
                
                # Add folder header
                folder_blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{'  ' * indent_level}📁 *{folder_name}*"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "▲ Hide Files" if (full_path == folder and is_expanding) else "▼ Show Files",
                            "emoji": True
                        },
                        "value": full_path,
                        "action_id": f"expand_folder_{full_path}"
                    }
                })
                
                # If this folder is expanded, show its contents
                if full_path == folder and is_expanding:
                    # Add files in this folder
                    for post in sorted(folder_content["files"], key=lambda x: x["name"]):
                        folder_blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"{'  ' * (indent_level + 1)}📄 `{post['name']}`"
                            },
                            "accessory": {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Edit",
                                    "emoji": True
                                },
                                "value": post["path"],
                                "action_id": "edit_post"
                            }
                        })
                    
                    # Add subfolders
                    for subfolder_name, subfolder_content in sorted(folder_content["folders"].items()):
                        folder_blocks.extend(build_folder_blocks(
                            subfolder_name,
                            subfolder_content,
                            full_path,
                            indent_level + 1
                        ))
                else:
                    folder_blocks.append({
                        "type": "context",
                        "block_id": f"folder_content_{full_path}",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "_Click to show contents_"
                            }
                        ]
                    })
                
                folder_blocks.append({
                    "type": "divider"
                })
                
                return folder_blocks
            
            # Build blocks for each top-level folder
            def traverse_hierarchy(h, current_path=""):
                result = []
                for name, content in sorted(h.items()):
                    result.extend(build_folder_blocks(name, content, current_path))
                return result
            
            blocks.extend(traverse_hierarchy(hierarchy))
            
            print("Updating view with files")
            client.views_update(
                view_id=body["view"]["id"],
                hash=body["view"]["hash"],
                view={
                    "type": "modal",
                    "callback_id": "post_selection_modal",
                    "title": {"type": "plain_text", "text": "Edit Post", "emoji": True},
                    "blocks": blocks
                }
            )
            
        except Exception as e:
            print(f"Error in handle_folder_expand: {str(e)}")
            client.chat_postMessage(
                channel=body["user"]["id"],
                text=f"❌ Failed to expand folder: {str(e)}"
            )

    @app.action("edit_post")
    def handle_edit_post_click(ack, body, client):
        ack()
        
        try:
            # Get the selected post path
            post_path = body["actions"][0]["value"]
            print(f"Selected post: {post_path}")
            
            # Get the current content of the file
            current_content = get_file_content(
                repo=os.environ.get("BLOG_REPOSITORY"),
                path=post_path
            )
            print("Content fetched successfully")
            
            # Open the edit modal
            client.views_open(
                trigger_id=body["trigger_id"],
                view={
                    "type": "modal",
                    "callback_id": "edit_post_modal",
                    "title": {"type": "plain_text", "text": "Edit Post", "emoji": True},
                    "submit": {"type": "plain_text", "text": "Save Changes", "emoji": True},
                    "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"Editing: *{post_path}*"
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "content_block",
                            "element": {
                                "type": "plain_text_input",
                                "multiline": True,
                                "action_id": "content_input",
                                "initial_value": current_content
                            },
                            "label": {"type": "plain_text", "text": "Content", "emoji": True}
                        },
                        {
                            "type": "input",
                            "block_id": "featured_image_block",
                            "optional": True,
                            "label": {
                                "type": "plain_text",
                                "text": "Featured Image",
                                "emoji": True
                            },
                            "element": {
                                "type": "file_input",
                                "action_id": "featured_image_input"
                            }
                        },
                        {
                            "type": "input",
                            "block_id": "inline_image_block",
                            "optional": True,
                            "label": {
                                "type": "plain_text",
                                "text": "Add Inline Image",
                                "emoji": True
                            },
                            "element": {
                                "type": "file_input",
                                "action_id": "inline_image_input"
                            }
                        }
                    ],
                    "private_metadata": post_path
                }
            )
            
        except Exception as e:
            print(f"Error in handle_edit_post_click: {str(e)}")
            client.chat_postMessage(
                channel=body["user"]["id"],
                text=f"❌ Failed to open edit modal: {str(e)}"
            )

    @app.view("edit_post_modal")
    def handle_edit_modal_submission(ack, body, view, client):
        print("Edit modal submitted")
        ack()
        
        # Get file path from private_metadata and new content
        file_path = view["private_metadata"]
        new_content = view["state"]["values"]["content_block"]["content_input"]["value"]
        print(f"Updating file: {file_path}")
        
        # Extract the post date from the file path (assuming format: posts/YYYYMMDD/YYYY-MM-DD-title.md)
        post_date = file_path.split('/')[1]  # Gets YYYYMMDD from path
        
        try:
            # Handle featured image if present
            featured_image_files = view["state"]["values"].get("featured_image_block", {}).get("featured_image_input", {}).get("files", [])
            if featured_image_files:
                file_info = featured_image_files[0]
                try:
                    # Process featured image
                    response = client.files_info(file=file_info['id']).get('file')
                    headers = {'Authorization': f'Bearer {client.token}'}
                    file_data = requests.get(response['url_private_download'], headers=headers).content
                    processed_image, ext = process_image(file_data)
                    base64_image = base64.b64encode(processed_image).decode('utf-8')
                    
                    # Generate filename and path
                    image_filename = f"featured-{int(time.time())}.{ext}"
                    image_path = f"posts/{post_date}/assets/img/{image_filename}"
                    
                    # Ensure directory exists
                    try:
                        response = requests.get(
                            f"https://api.github.com/repos/{repo}/contents/posts/{post_date}/assets/img",
                            headers={'Authorization': f'token {os.environ.get("GHP_TOKEN")}'}
                        )
                        if response.status_code == 404:
                            post_file(
                                repo=repo,
                                path=f"posts/{post_date}/assets/img/.gitkeep",
                                content="",
                                commit_message=f"Create directory posts/{post_date}/assets/img"
                            )
                    except Exception as e:
                        print(f"Error checking/creating directory: {str(e)}")
                    
                    # Upload image
                    post_file(
                        repo=repo,
                        path=image_path,
                        content=base64_image,
                        is_base64=True
                    )
                    
                    # Update YAML header with featured image
                    featured_image_path = f"/assets/img/{image_filename}"
                    # TODO: Update YAML header
                    
                except Exception as e:
                    print(f"Error processing featured image: {str(e)}")
                    client.chat_postMessage(
                        channel=body["user"]["id"],
                        text=f"⚠️ Failed to process featured image: {str(e)}"
                    )
            
            # Handle inline image if present
            inline_image_files = view["state"]["values"].get("inline_image_block", {}).get("inline_image_input", {}).get("files", [])
            if inline_image_files:
                file_info = inline_image_files[0]
                try:
                    # Process inline image
                    response = client.files_info(file=file_info['id']).get('file')
                    headers = {'Authorization': f'Bearer {client.token}'}
                    file_data = requests.get(response['url_private_download'], headers=headers).content
                    processed_image, ext = process_image(file_data)
                    base64_image = base64.b64encode(processed_image).decode('utf-8')
                    
                    # Generate filename and path
                    image_filename = f"image-{int(time.time())}.{ext}"
                    image_path = f"posts/{post_date}/assets/img/{image_filename}"
                    
                    # Upload image
                    post_file(
                        repo=repo,
                        path=image_path,
                        content=base64_image,
                        is_base64=True
                    )
                    
                    # Add image markdown to content
                    image_markdown = f"\n\n![{image_filename}](/assets/img/{image_filename})\n\n"
                    new_content += image_markdown
                    
                except Exception as e:
                    print(f"Error processing inline image: {str(e)}")
                    client.chat_postMessage(
                        channel=body["user"]["id"],
                        text=f"⚠️ Failed to process inline image: {str(e)}"
                    )
            
            # Update the post
            response = update_post(
                repo=repo,
                path=file_path,
                content=new_content,
                commit_message=f"Update {file_path} via Slack"
            )
            
            print(f'Update response: {response}')
            client.chat_postMessage(
                channel=body["user"]["id"],
                text=f"✅ Post updated successfully! File: {file_path}"
            )
            
        except Exception as e:
            print(f"Error in handle_edit_modal_submission: {str(e)}")
            client.chat_postMessage(
                channel=body["user"]["id"],
                text=f"❌ Failed to update post: {str(e)}"
            )