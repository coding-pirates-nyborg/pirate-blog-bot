from slack_bolt import App
from datetime import datetime
from api import post_markdown_file
import os

def register(app: App):
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
            response = post_markdown_file(
                repo=os.environ.get("BLOG_REPOSITORY"),
                path=file_path,
                content=markdown_content)
            
            client.chat_postMessage(
                channel=body["user"]["id"],
                text=f"✅ Blog post created successfully! File: {file_path}"
            )
        except Exception as e:
            client.chat_postMessage(
                channel=body["user"]["id"],
                text=f"❌ Failed to create blog post: {str(e)}"
            )
