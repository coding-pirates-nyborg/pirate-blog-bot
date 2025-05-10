# Pirate Blog Bot

A Slack bot that helps manage blog posts through GitHub integration. This bot allows users to create, edit, and delete blog posts directly from Slack, with all changes being synchronized to a GitHub repository.

## Features

- **Create Blog Posts**: Create new blog posts with markdown support
- **Edit Posts**: Modify existing blog posts
- **Delete Posts**: Remove blog posts from the repository
- **GitHub Integration**: All changes are automatically synchronized with your GitHub repository

## Prerequisites

- Python 3.7 or higher
- A Slack workspace with admin privileges
- A GitHub account with repository access
- GitHub Personal Access Token with repo scope

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
GITHUB_ORG=your-github-org
GHP_TOKEN=your-github-personal-access-token
BLOG_REPOSITORY=[the blog repository]
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/pirate-blog-bot.git
cd pirate-blog-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Bot

1. Make sure your virtual environment is activated
2. Ensure all environment variables are set
3. Run the bot:
```bash
python app.py
```

The bot will start in socket mode and connect to Slack. You should see a message indicating that the bot is running.

## Project Structure

```
pirate-blog-bot/
├── app.py              # Main application entry point
├── api.py             # GitHub API integration
├── features/          # Bot features
│   ├── blog_post/    # Blog post creation
│   ├── post_edit/    # Post editing
│   └── post_delete/  # Post deletion
└── requirements.txt   # Project dependencies
```

## Development

Each feature in the `features` directory follows a consistent structure:
- `__init__.py`: Module initialization and registration
- `command.py`: Command handlers
- `view.py`: UI components and views

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license here] 