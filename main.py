import config
import telebot, sys, time
from telebot import types

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

# inline handler
@bot.inline_handler(lambda query: len(query.query) == 0)
def default_query(inline_query):
    try:
        r = types.InlineQueryResultArticle('1', 'Д/З на завтра', types.InputTextMessageContent('Здесь будет написано дз на завтра'))
        r1 = types.InlineQueryResultArticle('2', 'Расписание на сегодня', types.InputTextMessageContent('Здесь будет расписание на сегодня'))
        bot.answer_inline_query(inline_query.id, [r, r1])
    except Exception as e:
        print(e)


# main loop
def main_loop():
    bot.infinity_polling()
    while 1:
        time.sleep(3)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)