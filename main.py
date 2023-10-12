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

def create_lesson_list_by_class(classroom):
    global classes
    result = []
    quantity = get_lessons_quantity_by_class(classroom, 0) + get_lessons_quantity_by_class(classroom, 1) + get_lessons_quantity_by_class(classroom, 2) + get_lessons_quantity_by_class(classroom, 3) + get_lessons_quantity_by_class(classroom, 4)
    for i in range(0, 5):
        today_timetable = get_array_timetable_by_class(classroom, i)
        for j in range(len(today_timetable)):
            if not today_timetable[j] in result:
                result.append(today_timetable[j])
    return result

def create_lesson_list_by_id(id):
    return create_lesson_list_by_class(get_class_by_id(id))

def get_current_homework_by_class(classroom):
    global homework
    return homework[classroom]

def get_current_homework_by_id(id):
    return get_current_homework_by_class(get_class_by_id(id))

def record_homework_file(jsondata):
    debug("Writing homework file...")
    homework_file = open("homework.json", encoding="utf-8")
    debug("Opened homework.json as homework file", 2)
    json.dump(jsondata, homework_file)
    debug("Wrote jsondata to homework.json", 2)
    homework_file.close()
    debug("homework.json closed", 2)

def set_current_homework_by_class(classroom, lesson, task):
    global homework
    full_current_json = homework
    full_current_json[classroom][lesson] = task
    homework = full_current_json
    record_homework_file(full_current_json)

def set_current_homework_by_id(id, lesson, task):
    set_current_homework_by_class(get_class_by_id(id), lesson, task)

def get_formatted_homework_by_class(classroom):
    global homework
    class_homework = homework[classroom]
    lessons = list(mydict.keys())
    result = ""
    for i in range(0, len(lessons)):
        result += lessons[i] + ") " + class_homework[lessons[i]] + "\n"
    return result

def get_formatted_homework_by_id(id):
    return get_formatted_homework_by_class(get_class_by_id(id))


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

debug("Fetching homework.json", 2)
homework_file = open("homework.json", encoding="utf-8")
debug("Opened homework.json as homework file", 3)
homework = json.load(homework_file)
debug("Loaded homework from homework.json", 3)
homework_file.close()
debug("homework.json closed", 3)

# inline handlers
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

@bot.inline_handler(lambda query: query.query.startswith("!"))
def default_query(inline_query):
    try:
        if not inline_query.from_user.id in config.admins:
            bot.answer_inline_query(inline_query.id, [types.InlineQueryResultArticle('1', 'No rights', types.InputTextMessageContent("You have no rights to use this command"))])
            return
        request = inline_query.query.replace("!", "")
        answers = []
        if (request == "lessons_list"):
            answers.append(types.InlineQueryResultArticle('1', 'Lessons list for user class', types.InputTextMessageContent(str(create_lesson_list_by_class(get_class_by_id(inline_query.from_user.id))))))
        if (request == "homework_list"):
            answers.append(types.InlineQueryResultArticle('2', 'Homework list for user class today', types.InputTextMessageContent(get_formatted_homework_by_id(inline_query.from_user.id))))
        bot.answer_inline_query(inline_query.id, answers, cache_time=0)
    except Exception as e:
        print("exception in inline_handler: " + e)

# direct message handlers
@bot.message_handler(func=lambda message: message.text.startswith("!"))
def handle_admin_command(message):
    if not message.from_user.id in config.admins:
        bot.reply_to(message, "You have no rights to use this command")
        return
    command = message.text.replace("!", "")
    if "set_homework" in command:
        command_split = command.split(" ")
        if not command_split[1] in create_lesson_list_by_id(message.from_user.id):
            bot.reply_to(message, "Unknown lesson (not found in your class)")
            return
        lesson = command_split[1]
        command_split.pop(0)
        command_split.pop(1)
        hw = command_split.join(" ")
        result = get_current_homework_by_id(message.from_user.id)
        result[lesson] = hw


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
