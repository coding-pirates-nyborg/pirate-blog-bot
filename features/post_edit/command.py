# features/post_edit/command.py
from slack_bolt import App
from api import list_repository_files
from utils.github import get_posts 

def register(app: App):
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