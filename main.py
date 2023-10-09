import config

# useful functions
def debug(text, level=1):
    if config.debug:
        print("#" + (" " * level) + text)

