from slack_bolt import App

def register(app: App):
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
                        "block_id": "featured_image_block",
                        "optional": True,
                        "element": {
                            "type": "file_input",
                            "accept": ["image/png", "image/jpeg", "image/webp"],
                            "action_id": "featured_image_input"
                        },
                        "label": {"type": "plain_text", "text": "Featured Image"}
                    }
                ]
            }
        )
