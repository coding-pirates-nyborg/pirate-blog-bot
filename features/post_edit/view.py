# features/post_edit/view.py
from slack_bolt import App
from api import get_file_content, update_post
import os

def register(app: App):
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
                repo=os.environ.get("BLOG_REPOSITORY"),
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
                repo=os.environ.get("BLOG_REPOSITORY"),
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