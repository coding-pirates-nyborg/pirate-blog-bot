# features/post_edit/__init__.py
from slack_bolt import App
from .command import register as register_command
from .view import register as register_view

def register(app: App):
    register_command(app)
    register_view(app)