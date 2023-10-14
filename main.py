import config
import telebot, sys, time, json
from datetime import datetime
from uuid import *
from telebot import types, util

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

def get_workdays_by_class(classroom):
    global classes
    return len(classes[classroom]["timetable"]) - 1

def get_lessons_quantity_by_class(classroom, weekday = datetime.now().weekday()):
    global classes
    return len(classes[classroom]["timetable"][weekday])

def create_lesson_list_by_class(classroom):
    global classes
    result = []
    for i in range(0, get_workdays_by_class(classroom)):
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
    homework_file = open("homework.json", "r+", encoding="utf-8")
    debug("Opened homework.json as homework file", 2)
    homework_file.truncate(0)
    json.dump(jsondata, homework_file, ensure_ascii=False)
    debug("Wrote jsondata to homework.json", 2)
    homework_file.close()
    debug("homework.json closed", 2)

def set_current_homework_by_class(classroom, lesson, task):
    global homework
    full_current_json = homework
    full_current_json[classroom][lesson] = task
    homework = full_current_json
    record_homework_file(full_current_json)

def format_homework(classroom, text):
    global classes
    lessons = create_lesson_list_by_class(classroom)
    result = []
    for i in range(len(lessons)):
        if lessons[i] in text:
            result.append(lessons[i])
            result.append(text.replace(lessons[i] + " ", "").replace("/add ", ""))
    return result

def set_current_homework_by_id(id, lesson, task):
    set_current_homework_by_class(get_class_by_id(id), lesson, task)

def get_formatted_homework_by_class(classroom):
    global homework
    class_homework = homework[classroom]
    lessons = list(class_homework.keys())
    result = "Всё ДЗ:\n\n"
    for i in range(0, len(lessons)):
        result += lessons[i] + ": " + class_homework[lessons[i]] + "\n"
    return result

def get_formatted_homework_by_id(id):
    return get_formatted_homework_by_class(get_class_by_id(id))

def get_formatted_day_homework_by_class(classroom, weekday = datetime.now().weekday()):
    global homework
    class_homework = homework[classroom]
    timetable = get_array_timetable_by_class(classroom, weekday)
    lessons = get_lessons_quantity_by_class(classroom, weekday)
    result = "ДЗ на "
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
    for i in range(0, lessons):
        if timetable[i] in list(class_homework.keys()):
            result += timetable[i] + ": " + class_homework[timetable[i]] + "\n"
    return result

def clear_homework_by_admin_id(id):
    debug("Clearing homework...")
    global homework
    full_current_json = homework
    clear_class = get_class_by_admin_id(id)
    full_current_json[clear_class] = {}
    homework = full_current_json
    record_homework_file(full_current_json)

def get_class_by_admin_id(id):
    debug("Getting class by admin id...")
    global classes
    all_classes = list(classes.keys())
    debug("All classes:", 2)
    debug(all_classes, 3)
    for i in range(0, len(all_classes)):
        debug(classes[all_classes[i]]["admins"], 2)
        if str(id) in classes[all_classes[i]]["admins"]:
            return all_classes[i]
    return ""

def get_admins_of_class(classroom):
    global classes
    return classes[classroom]["admins"]

def is_registered_class(classroom):
    global classes
    return classroom in list(classes.keys())

def all_homework_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        types.InlineKeyboardButton("🗑️ Очистить", callback_data="clear_homework"))
    return markup

def homework_request_markup(request):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("❌ Отклонить", callback_data="decline_homework_" + request),
        types.InlineKeyboardButton("✅ Принять", callback_data="accept_homework_" + request)
    )
    return markup

def is_int(var):
    try:
        a = int(var)
        return True
    except ValueError:
        return False
    
def get_hw_request_by_uuid(uid):
    global hw_requests
    return hw_requests[uid]

def create_hw_request(classroom, lesson, task):
    global hw_requests
    uid = str(uuid4())
    hw_requests[uid] = [classroom, lesson, task]
    return uid

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

hw_requests = {}
'''
each request has uuid generated with uuid4

to get array use get_hw_request_by_uuid(<uuid here>)

get_hw_request_by_uuid(uuid)[0] = classroom
get_hw_request_by_uuid(uuid)[1] = lesson
get_hw_request_by_uuid(uuid)[2] = task

structure example:

hw_requests = {
    "uuid4": [
        "classroom", "lesson", "task"
    ]
}
'''

# inline handlers
@bot.inline_handler(lambda query: len(query.query) == 0)
def default_query(inline_query):
    try:
        answers = []
        if datetime.now().weekday() in range(0, get_workdays_by_class(get_class_by_id(inline_query.from_user.id))):
            answers.append(types.InlineQueryResultArticle('1', 'Расписание на сегодня', types.InputTextMessageContent(get_timetable_by_class(get_class_by_id(inline_query.from_user.id)))))
            answers.append(types.InlineQueryResultArticle('3', 'ДЗ на сегодня', types.InputTextMessageContent(get_formatted_day_homework_by_class(get_class_by_id(inline_query.from_user.id)))))
        if datetime.now().weekday() + 1 in range(0, get_workdays_by_class(get_class_by_id(inline_query.from_user.id))):
            answers.append(types.InlineQueryResultArticle('2', 'Расписание на завтра', types.InputTextMessageContent(get_timetable_by_class(get_class_by_id(inline_query.from_user.id), datetime.now().weekday() + 1))))
            answers.append(types.InlineQueryResultArticle('4', 'ДЗ на завтра', types.InputTextMessageContent(get_formatted_day_homework_by_class(get_class_by_id(inline_query.from_user.id), datetime.now().weekday() + 1))))
        bot.answer_inline_query(inline_query.id, answers, cache_time=0)
    except Exception as e:
        print("exception in inline_handler: " + e)

@bot.inline_handler(lambda query: len(query.query) == 1 and is_int(query.query))
def default_query(inline_query):
    try:
        num = int(inline_query.query)
        answers = []
        if (num in range(1, get_workdays_by_class(get_class_by_id(inline_query.from_user.id)) + 1)) and (datetime.now().weekday() in range(0, get_workdays_by_class(get_class_by_id(inline_query.from_user.id)) + 1)):
            answers.append(types.InlineQueryResultArticle('1', str(num) + ' урок сегодня', types.InputTextMessageContent(get_array_timetable_by_class(get_class_by_id(inline_query.from_user.id))[num - 1])))
        if (num in range(1, get_workdays_by_class(get_class_by_id(inline_query.from_user.id)) + 1)):
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

            result = "ДЗ на "
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
            answers.append(types.InlineQueryResultArticle('3', result, types.InputTextMessageContent(get_formatted_day_homework_by_class(get_class_by_id(inline_query.from_user.id), num - 1))))
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
        hw = command.partition(" ")[2].partition(" ")[2]
        set_current_homework_by_id(message.from_user.id, lesson, hw)
        bot.reply_to(message, lesson + " set to " + hw)

@bot.message_handler(commands=["homework"])
def handle_homework(message):
    if get_class_by_admin_id(message.from_user.id) == "":
        bot.reply_to(message, "Вы не являетесь админом ни одного из зарегистрированных классов!")
        return
    bot.send_message(message.from_user.id, get_formatted_homework_by_id(message.from_user.id), reply_markup=all_homework_markup())

@bot.message_handler(commands=["add"])
def handle_homework_report(message):
    debug("recieved /add")
    report_text = util.extract_arguments(message.text)
    if report_text == "":
        text = "Команда /add используется для добавления недобавленного или неправильного ДЗ.\n\nИспользование:\n/add [предмет] [задание]"
        bot.reply_to(message, text)
        return
    if get_class_by_admin_id(message.from_user.id) == "":
        user_class = get_class_by_id(message.from_user.id)
        hw = format_homework(user_class, message.text)
        if (hw != []):
            request = create_hw_request(user_class, hw[0], hw[1])
            for i in range(0, len(get_admins_of_class(user_class))):
                bot.send_message(get_admins_of_class(user_class)[i], "Запрос на добавление ДЗ:\n\n" + get_hw_request_by_uuid(request)[1] + ": " + get_hw_request_by_uuid(request)[2], reply_markup=homework_request_markup(request))
    
# callback handlers
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # call.data
    if get_class_by_admin_id(call.from_user.id) != None and call.data == "clear_homework":
        clear_homework_by_admin_id(call.from_user.id)
        bot.answer_callback_query(call.id, "✅ ДЗ очищено!")
    if call.data.startswith("accept_"):
        request_uuid = call.data.replace("accept_", "")
        request = get_hw_request_by_uuid(request_uuid)
        set_current_homework_by_class(get_class_by_admin_id(call.from_user.id), request[1], request[2])
        bot.answer_callback_query(call.id, "✅ Запрос принят!")

# main loop
for i in range(len(config.admins)):
    bot.send_message(config.admins[i], "Bot started!")

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
