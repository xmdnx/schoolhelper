# configure your bot running here

# useful functions
def debugprint(text, level=1):
    if debug:
        print("#" + (" " * level) + text)

# premium settings
use_twav = True  # set True to use TWAV as premium payment
premium_price = 1  # set premium price
force_premium = [841914494]

# global settings
admins = [841914494]
debug = True

# telegram bot settings
token = "test"  # set your Telegram bot token here

# check token
def check_token():
    global token
    if token == "":
        debugprint("Telegram token unset in config.py")
        token = input("Paste Telegram bot token here: ")
    debugprint("Telegram token set")
