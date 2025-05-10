# app.py
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from features import register_features

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Register all features
register_features(app)

# Start your app
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()