import irc.bot
import irc.strings
import time
import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Constants
DELAY = 1  # Delay in seconds
MAX_RETRIES = 3  # Maximum number of retries


class CommandFileHandler(FileSystemEventHandler):
    def __init__(self, bot_instance):
        self.bot = bot_instance

    def on_modified(self, event):
        if event.src_path.endswith('commands.json'):
            time.sleep(DELAY)
            self.bot.reload_commands()


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, token, channel, config_file):
        server = 'irc.chat.twitch.tv'
        port = 6667
        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port, token)], username, username
        )
        self.channel = '#' + channel

        # Set up watchdog observer
        self.observer = Observer()
        event_handler = CommandFileHandler(self)
        self.observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(config_file)), recursive=False)
        self.observer.start()

        # Load commands from configuration file
        with open(config_file, 'r') as f:
            self.commands_config = json.load(f)
        self.command_timestamps = {cmd: 0 for cmd in self.commands_config}
        self.last_known_commands_content = self.commands_config


    def reload_commands(self):
        for _ in range(MAX_RETRIES):
            try:
                # Attempt to read the configuration file
                with open('commands.json', 'r') as f:
                    current_content = f.read()
                    # Check if the content has actually changed
                    if current_content == self.last_known_commands_content:
                        return

                    self.commands_config = json.loads(current_content)
                    self.last_known_commands_content = current_content

                # If successful, print a message and exit the loop
                print('Commands reloaded!')
                return

            except json.JSONDecodeError:
                # Handle JSON decoding error (e.g. malformed JSON)
                print('Error decoding JSON. Retrying...')
                time.sleep(DELAY)

            except FileNotFoundError:
                # Handle file not found error
                print('commands.json not found. Retrying...')
                time.sleep(DELAY)

            except Exception as e:
                # Handle any other exceptions
                print(f'Unexpected error: {e}. Retrying...')
                time.sleep(DELAY)

        # If the loop completes without a successful load, print an error message
        print('Failed to reload commands after multiple attempts.')

        # Set the initial timestamp to 0
        for command in self.commands_config:
            if command not in self.command_timestamps:
                self.command_timestamps[command] = 0

        # Remove any commands that no longer exist
        for stored_command in list(self.command_timestamps.keys()):
            if stored_command not in self.commands_config:
                del self.command_timestamps[stored_command]


    def on_welcome(self, c, e):
        c.join(self.channel)
        print(f'Joined {self.channel}')


    def on_pubmsg(self, c, e):
        current_time = time.time()
        received_message = e.arguments[0].lower()

        for command, config in self.commands_config.items():
            command_variations = [var.strip().lower() for var in command.split(',')]

            # Check if any variation is in the received message
            if any(variation in received_message for variation in command_variations) and self.can_execute_command(command, current_time):
                c.privmsg(self.channel, config['response'])
                self.command_timestamps[command] = current_time

    def can_execute_command(self, command, current_time):
        last_time = self.command_timestamps.get(command, 0)
        cooldown = self.commands_config[command].get('cooldown', 0)
        return current_time - last_time > cooldown


    def die(self, msg=''):
        self.observer.stop()  # Stop the observer when the bot stops
        super().die(msg)


def run_bot():
    username = ''
    token = ''  # Generate this from https://twitchapps.com/tmi/
    channel = ''
    config_file = 'commands.json'  # Path to the command configuration file

    bot = TwitchBot(username, token, channel, config_file)
    bot.start()
