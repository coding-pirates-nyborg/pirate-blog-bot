from slack_bolt import App

def register_features(app: App):
    from .blog_post import register as register_blog_post
    from .post_edit import register as register_post_edit
    from .post_delete import register as register_post_delete
    
    register_blog_post(app)
    register_post_edit(app)
    register_post_delete(app)
