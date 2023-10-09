import config
import telebot, sys, time, json
from datetime import datetime
from telebot import types

# useful functions
def debug(text, level=1):
    if config.debug:
        print("#" + (" " * level) + str(text))

def get_class_by_id(id):
    global data
    debug(data["people"])
    debug(str(id))
    debug(str(id) in data["people"])
    debug(id in data["people"])
    if str(id) in data["people"]:
        result = data["people"][str(id)]
    else:
        result = str(None)
    return result

def get_today_timetable_by_class(classroom):
    global data
    if not classroom in data["classes"]:
        return("Вы не подключены к классу. Обратитесь к админу класса, выберите класс в боте, или напишите в поддержку.")
    weekday = datetime.now().weekday()
    result = "Расписание на "
    match weekday:
        case 0:
            result += "понедельник"
        case 1:
            result += "вторник"
        case 2:
            result += "среду"
        case 3:
            result += "четверг"
        case 4:
            result += "пятницу"
    result += "\n\n"
    lessons_today = len(data["classes"][classroom]["timetable"][weekday])
    for i in range(1, lessons_today + 1):
        result += str(i) + ") " + data["classes"][classroom]["timetable"][weekday][i - 1] + "\n"
    return result

# set up
debug("Started setup")
config.check_token()
debug("Token checked!", 2)
bot = telebot.TeleBot(config.token)
debug("TeleBot initialized!", 2)
debug("Fetching data.json", 2)
datafile = open("data.json", encoding="utf-8")
debug("Opened data.json as data file", 3)
data = json.load(datafile)
debug("Loaded data from data file to data", 3)
datafile.close()
debug("Data file closed", 3)

# inline handler
@bot.inline_handler(lambda query: len(query.query) == 0)
def default_query(inline_query):
    try:
        # r = types.InlineQueryResultArticle('1', 'Д/З на завтра', types.InputTextMessageContent('Здесь будет написано дз на завтра'))
        r = types.InlineQueryResultArticle('1', 'Ваш класс', types.InputTextMessageContent('ID вашего класса: ' + get_class_by_id(inline_query.from_user.id)))
        r1 = types.InlineQueryResultArticle('2', 'Расписание на сегодня', types.InputTextMessageContent(get_today_timetable_by_class(get_class_by_id(inline_query.from_user.id))))
        bot.answer_inline_query(inline_query.id, [r, r1])
    except Exception as e:
        print("exception in inline_handler: " + e)


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

'''
 {
    'id': '3615995219113418494', 
    'from_user': {
        'id': 841914494, 
        'is_bot': False, 
        'first_name': 'хмдн++', 
        'username': 'xmdnusr', 
        'last_name': None, 
        'language_code': 'ru', 
        'can_join_groups': None, 
        'can_read_all_group_messages': None, 
        'supports_inline_queries': None, 
        'is_premium': None, 
        'added_to_attachment_menu': None
    }, 
    'query': '', 
    'offset': '', 
    'chat_type': 'group', 
    'location': None}
'''