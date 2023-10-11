import config
import telebot, sys, time, json
from datetime import datetime
from uuid import *
from telebot import types

# useful functions
def debug(text, level=1):
    if config.debug:
        print("#" + (" " * level) + str(text))

def get_class_by_id(id):
    global people
    debug("Getting class by id: " + str(id))
    if str(id) in people:
        result = people[str(id)]
        debug("Found id " + str(id) + " in people", 2)
    else:
        result = str(None)
        debug("ID " + str(id) + " not found in people!", 2)
    return result

def get_timetable_by_class(classroom, weekday = datetime.now().weekday()):
    global classes
    debug("Getting timetable by class")
    debug("Class: " + classroom, 2)
    if not classroom in classes:
        return("Вы не подключены к классу или у класса нет расписания. Обратитесь к админу класса, выберите класс в боте, или напишите в поддержку.")
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
    lessons_today = len(classes[classroom]["timetable"][weekday])
    for i in range(1, lessons_today + 1):
        result += str(i) + ") " + classes[classroom]["timetable"][weekday][i - 1] + "\n"
    return result

def get_array_timetable_by_class(classroom, weekday = datetime.now().weekday()):
    global classes
    debug("Getting timetable by class in array")
    debug("Class: " + classroom, 2)
    if not classroom in classes:
        return []
    result = []
    lessons_today = len(classes[classroom]["timetable"][weekday])
    for i in range(1, lessons_today + 1):
        result.append(classes[classroom]["timetable"][weekday][i - 1])
    return result

def get_lessons_quantity_by_class(classroom, weekday = datetime.now().weekday()):
    global classes
    return len(classes[classroom]["timetable"][weekday])

# set up
debug("Started setup")
config.check_token()
debug("Token checked!", 2)
bot = telebot.TeleBot(config.token)
debug("TeleBot initialized!", 2)

debug("Fetching classes.json", 2)
classes_file = open("classes.json", encoding="utf-8")
debug("Opened classes.json as classes file", 3)
classes = json.load(classes_file)
debug("Loaded classes from classes.json", 3)
classes_file.close()
debug("classes.json closed", 3)

debug("Fetching people.json", 2)
people_file = open("people.json", encoding="utf-8")
debug("Opened people.json as people file", 3)
people = json.load(people_file)
debug("Loaded people from people.json", 3)
people_file.close()
debug("people.json closed", 3)

# empty inline handler
@bot.inline_handler(lambda query: len(query.query) == 0)
def default_query(inline_query):
    try:
        # r = types.InlineQueryResultArticle('1', 'Д/З на завтра', types.InputTextMessageContent('Здесь будет написано дз на завтра'))
        # r = types.InlineQueryResultArticle('1', 'Ваш класс', types.InputTextMessageContent('ID вашего класса: ' + get_class_by_id(inline_query.from_user.id)))
        r1 = types.InlineQueryResultArticle('1', 'Расписание на сегодня', types.InputTextMessageContent(get_timetable_by_class(get_class_by_id(inline_query.from_user.id))))
        r2 = types.InlineQueryResultArticle('2', 'Расписание на завтра', types.InputTextMessageContent(get_timetable_by_class(get_class_by_id(inline_query.from_user.id), datetime.now().weekday() + 1)))
        bot.answer_inline_query(inline_query.id, [r1, r2], cache_time=0)
    except Exception as e:
        print("exception in inline_handler: " + e)

# 
@bot.inline_handler(lambda query: len(query.query) == 1)
def default_query(inline_query):
    try:
        num = int(inline_query.query)
        answers = []
        if (num in range(1, get_lessons_quantity_by_class(get_class_by_id(inline_query.from_user.id)) + 1)):
            answers.append(types.InlineQueryResultArticle('1', str(num) + ' урок сегодня', types.InputTextMessageContent(get_array_timetable_by_class(get_class_by_id(inline_query.from_user.id))[num - 1])))
        if (num in range(0, 6)):
            result = "Расписание на "
            match num:
                case 1:
                    result += "понедельник"
                case 2:
                    result += "вторник"
                case 3:
                    result += "среду"
                case 4:
                    result += "четверг"
                case 5:
                    result += "пятницу"
            answers.append(types.InlineQueryResultArticle('2', result, types.InputTextMessageContent(get_timetable_by_class(get_class_by_id(inline_query.from_user.id), num - 1))))
        bot.answer_inline_query(inline_query.id, answers, cache_time=0)
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
