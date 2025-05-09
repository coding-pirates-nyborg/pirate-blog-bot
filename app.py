import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime
from api import post_markdown_file, list_repository_files, delete_posts, update_post, get_file_content

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.command("/delete")
def delete_github_post(ack, body, client):
    ack()
    posts = get_posts()
    
    # Create blocks with checkboxes for each post
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Select posts to delete:"
            }
        }
    ]
    
    # Add a checkbox for each post
    blocks.append({
        "type": "input",
        "block_id": "post_selection",
        "element": {
            "type": "checkboxes",
            "action_id": "post_checkboxes",
            "options": [
                {
                    "text": {"type": "plain_text", "text": post["name"]},
                    "value": post["path"]
                } for post in posts
            ]
        },
        "label": {"type": "plain_text", "text": "Posts"}
    })
    
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "delete_post_modal",
            "title": {"type": "plain_text", "text": "Delete Post"},
            "submit": {"type": "plain_text", "text": "Delete"},
            "blocks": blocks
        }
    )

@app.command("/edit")
def edit_post(ack, body, client):
    print("Starting edit_post command")
    ack()
    posts = get_posts()
    print(f"Found {len(posts)} posts")
    
    # Create blocks with radio buttons for post selection
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Select a post to edit:"
            }
        },
        {
            "type": "input",
            "block_id": "post_selection",
            "element": {
                "type": "radio_buttons",
                "action_id": "post_radio",
                "options": [
                    {
                        "text": {"type": "plain_text", "text": post["name"]},
                        "value": post["path"]
                    } for post in posts
                ]
            },
            "label": {"type": "plain_text", "text": "Posts"}
        }
    ]
    
    print("Opening selection modal")
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "post_selection_modal",
            "title": {"type": "plain_text", "text": "Select Post"},
            "submit": {"type": "plain_text", "text": "Next"},
            "blocks": blocks
        }
    )

@app.command("/post")
def create_post(ack, body, client):
    # Acknowledge command request
    ack()
    
    # Open a modal
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "blog_post_modal",
            "title": {"type": "plain_text", "text": "Create Blog Post"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "title_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "title_input",
                        "placeholder": {"type": "plain_text", "text": "Enter post title"}
                    },
                    "label": {"type": "plain_text", "text": "Title"}
                },
                {
                    "type": "input",
                    "block_id": "description_block",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "description_input",
                        "placeholder": {"type": "plain_text", "text": "Enter post description"}
                    },
                    "label": {"type": "plain_text", "text": "Description"},
                    "optional": True
                },
                {
                    "type": "input",
                    "block_id": "categories_block",
                    "element": {
                        "type": "multi_static_select",
                        "action_id": "categories_select",
                        "placeholder": {"type": "plain_text", "text": "Select categories"},
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "Blogging"},
                                "value": "Blogging"
                            },
                            {
                                "text": {"type": "plain_text", "text": "News"},
                                "value": "News"
                            },
                            {
                                "text": {"type": "plain_text", "text": "Tutorial"},
                                "value": "Tutorial"
                            }
                        ]
                    },
                    "label": {"type": "plain_text", "text": "Categories"}
                },
                {
                    "type": "input",
                    "block_id": "tags_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "tags_input",
                        "placeholder": {"type": "plain_text", "text": "Enter tags (comma-separated)"}
                    },
                    "label": {"type": "plain_text", "text": "Tags"},
                    "optional": True
                },
                {
                    "type": "input",
                    "block_id": "pin_block",
                    "element": {
                        "type": "checkboxes",
                        "action_id": "pin_checkbox",
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": "Pin this post"},
                                "value": "pin"
                            }
                        ]
                    },
                    "label": {"type": "plain_text", "text": "Pin Post"},
                    "optional": True
                },
                {
                    "type": "input",
                    "block_id": "blog_content",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "content"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Skriv dit blog-indlæg som markdown her",
                        "emoji": True
                    }
                }
            ]
        }
    )

@app.view("blog_post_modal")
def handle_modal_submission(ack, body, client, view):
    # Acknowledge the view submission
    ack()
    
    # Extract values from the view
    title = view["state"]["values"]["title_block"]["title_input"]["value"]
    description = view["state"]["values"]["description_block"]["description_input"]["value"]
    categories = view["state"]["values"]["categories_block"]["categories_select"]["selected_options"]
    tags = view["state"]["values"]["tags_block"]["tags_input"]["value"]
    content = view["state"]["values"]["blog_content"]["content"]["value"]
    pin_value = view["state"]["values"]["pin_block"]["pin_checkbox"]["selected_options"]
    
    # Format categories and tags
    categories_list = [cat["value"] for cat in categories]
    tags_list = [tag.strip() for tag in tags.split(",")] if tags else []
    is_pinned = len(pin_value) > 0
    
    # Get current date and user name
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S +0200")
    file_date = current_date.strftime("%Y%m%d")
    
    # Get the Slack username
    user_info = client.users_info(user=body["user"]["id"])
    username = user_info["user"]["name"]
    
    print(f'username: {username}')
    
    # Create markdown content
    markdown_content = f"""---
title: {title}
description: >-
  {description}
author: {username}
date: {formatted_date}
categories: {categories_list}
tags: {tags_list}
pin: {str(is_pinned).lower()}
media_subpath: '/posts/{file_date}'
---

{content}
"""
    
    # Create the file path
    file_path = f"_posts/{current_date.strftime('%Y-%m-%d')}-{title.lower().replace(' ', '-')}.md"
    
    try:
        # Import and use your GitHub API function
        response = post_markdown_file(
            repo=os.environ.get("GITHUB_REPOSITORY"),
            path=file_path,
            content=markdown_content)
        
        print(f'response: {response}')
        
        # Notify the user of success
        client.chat_postMessage(
            channel=body["user"]["id"],
            text=f"✅ Blog post created successfully! File: {file_path}"
        )
    except Exception as e:
        # Notify the user of failure
        client.chat_postMessage(
            channel=body["user"]["id"],
            text=f"❌ Failed to create blog post: {str(e)}"
        )

def get_posts():
    # List files in a directory
    files = list_repository_files(os.environ.get("GITHUB_REPOSITORY"), "_posts/")
    # Transform the files into the format we need
    posts = [
        {
            "name": file["name"],
            "path": file["path"]
        }
        for file in files
    ]
    return posts

@app.view("delete_post_modal")
def handle_delete_modal_submission(ack, body, view, client):
    ack()
    
    # Get selected posts
    selected_posts = view["state"]["values"]["post_selection"]["post_checkboxes"]["selected_options"]
    
    print("Selected posts:", selected_posts)
    responses = delete_posts(os.environ.get("GITHUB_REPOSITORY"), selected_posts)
    
    # Print deletion results
    print("Deletion responses:", responses)
    
    # Notify user of results
    message = "Deletion results:\n"
    for path, status in responses.items():
        message += f"• {path}: {status}\n"
    
    client.chat_postMessage(
        channel=body["user"]["id"],
        text=message
    )

@app.view("post_selection_modal")
def handle_post_selection(ack, body, view, client):
    print("Post selection modal submitted")
    
    # Get selected post
    selected_post = view["state"]["values"]["post_selection"]["post_radio"]["selected_option"]
    print(f"Selected post: {selected_post}")
    
    try:
        # Get the current content of the file
        print(f"Fetching content for {selected_post['value']}")
        current_content = get_file_content(
            repo=os.environ.get("GITHUB_REPOSITORY"),
            path=selected_post["value"]
        )
        print("Content fetched successfully")
        
        # Open new modal with content
        blocks = [
            {
                "type": "input",
                "block_id": "content_block",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "content_input",
                    "initial_value": current_content
                },
                "label": {"type": "plain_text", "text": "Edit Content"}
            }
        ]
        
        print("Updating view with content")
        # Return a new view in the acknowledgement
        ack({
            "response_action": "update",
            "view": {
                "type": "modal",
                "callback_id": "edit_post_modal",
                "title": {"type": "plain_text", "text": "Edit Post"},
                "submit": {"type": "plain_text", "text": "Save Changes"},
                "blocks": blocks,
                "private_metadata": selected_post["value"]  # Store the path for later
            }
        })
        print("View update response sent")
    except Exception as e:
        print(f"Error in handle_post_selection: {str(e)}")
        client.chat_postMessage(
            channel=body["user"]["id"],
            text=f"❌ Failed to load post content: {str(e)}"
        )

@app.view("edit_post_modal")
def handle_edit_modal_submission(ack, body, view, client):
    print("Edit modal submitted")
    ack()
    
    # Get file path from private_metadata and new content
    file_path = view["private_metadata"]
    new_content = view["state"]["values"]["content_block"]["content_input"]["value"]
    print(f"Updating file: {file_path}")
    
    try:
        # Update the post
        response = update_post(
            repo=os.environ.get("GITHUB_REPOSITORY"),
            path=file_path,
            content=new_content,
            commit_message=f"Update {file_path} via Slack"
        )
        
        print(f'Update response: {response}')
        
        # Notify user of success
        client.chat_postMessage(
            channel=body["user"]["id"],
            text=f"✅ Post updated successfully! File: {file_path}"
        )
        
    except Exception as e:
        print(f"Error in handle_edit_modal_submission: {str(e)}")
        # Notify user of failure
        client.chat_postMessage(
            channel=body["user"]["id"],
            text=f"❌ Failed to update post: {str(e)}"
        )

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()