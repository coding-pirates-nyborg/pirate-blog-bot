# features/post_delete/view.py
from slack_bolt import App
from api import delete_posts
import os

def register(app: App):
    @app.view("delete_post_modal")
    def handle_delete_modal_submission(ack, body, view, client):
        ack()
        
        # Get selected posts
        selected_posts = view["state"]["values"]["post_selection"]["post_checkboxes"]["selected_options"]
        
        print("Selected posts:", selected_posts)
        responses = delete_posts(os.environ.get("BLOG_REPOSITORY"), selected_posts)
        
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