# features/post_delete/command.py
from slack_bolt import App
from utils.github import get_posts

def register(app: App):
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