
# Twitch Bot

A customizable Twitch bot that listens to chat messages in a specific channel and responds to user-defined commands. The bot also features a dark-themed command management GUI for easy command additions, modifications, and removals.

## Features

- Responds to user-defined chat commands.
- Command cooldown to prevent spam.
- Real-time command update without restarting the bot.
- Dark-themed GUI for managing commands.

## Installation

### Prerequisites

- Python 3.x

### Steps

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/nixyyyy/twitch-bot.git
    cd twitch-bot
    ```

2. **Set Up a Virtual Environment (Recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configuration**:
   
   - Update the `bot.py` file with your Twitch username, token (which can be generated from [Twitch Token Generator](https://twitchapps.com/tmi/)), and the channel you wish to join.
   - Modify `commands.json` if you want to predefine some commands before running the bot.

5. **Run the Program**:
    ```bash
    python main.py
    ```

## Usage

1. **Twitch Bot**: Once the program is running, the bot will join the specified Twitch channel and start listening to chat messages.

2. **Command Manager GUI**: The GUI allows you to add, modify, or remove commands. Any changes made to commands are immediately picked up by the bot without needing a restart.
