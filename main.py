import config
import telebot

# useful functions
def debug(text, level=1):
    if config.debug:
        print("#" + (" " * level) + text)

# set up
debug("Started setup")
config.check_token()
debug("Token checked!", 2)
bot = telebot.TeleBot(config.token)
debug("TeleBot initialized!", 2)