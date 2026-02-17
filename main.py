# Bot teh pistrimki FIX.txt  
# [Bot teh pistrimki FIX.txt](Attachments/98963B77-D142-4AD3-9161-091478BC5287.txt)  
import telebot  
from telebot import types  
import os  
import sys  
import io  
  
# =======================  
# Налаштування UTF-8 для консолі Windows  
# =======================  
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  
  
# =======================  
# Токен та оператор  
# =======================  
TOKEN = "8520177737:AAEHCIO0xaryvPdfg9EsK5ekSkeiX8nt2cw"  
OPERATOR_ID =7968501682  
  
bot = telebot.TeleBot(TOKEN)  
  
ticket_counter = 0  
OPERATORS = {OPERATOR_ID: "Владелец"}  
active_chats = {}  
ticket_messages = {}  
canceled_tickets = set()  
pending_tickets = {}  
  
# Створюємо папку logs  
if not os.path.exists("logs"):  
    os.makedirs("logs")  
  
def log_message(ticket_id, text):  
    with open(f"logs/logs{ticket_id}.txt", "a", encoding="utf-8") as f:  
        f.write(text + "\n")  
  
# =======================  
# Головне меню  
# =======================  
def main_menu(name):  
    markup = types.InlineKeyboardMarkup(row_width=1)  
    btn_support = types.InlineKeyboardButton("Тех. Поддержка", callback_data="support")  
    btn_recovery = types.InlineKeyboardButton("В разроботке", url="https://www.python.org/downloads/")  
    btn_site = types.InlineKeyboardButton("🌐Discord", url="[https://www.python.org/downloads/](https://discord.gg/qB4XX9RBZt)")  
    btn_forum = types.InlineKeyboardButton("Связь с владельцем", url="[https://discord.com/users/1467157730920894579](https://discord.com/users/1467157730920894579)")  
    btn_shop = types.InlineKeyboardButton("ℹ️Информация ", url="[https://discord.gg/GwECwquJTd](https://discord.gg/GwECwquJTd)")  
      
    markup.add(btn_support, btn_recovery)  
    markup.row(btn_site, btn_forum, btn_shop)  
      
    text = (  
        f"Привет, {name}!\n\n"  
        "Белый Аист | Поддержка .\n\n"  
        "Выбери действие"  
    )  
    return text, markup  
  
# =======================  
# Старт бота  
# =======================  
@bot.message_handler(commands=['start'])  
def start(message):  
    name = message.from_user.first_name  
    photo_path = "img/start. jpeg"  
    text, markup = main_menu(name)  
    try:  
        if os.path.exists(photo_path):  
            with open(photo_path, 'rb') as photo:  
                bot.send_photo(message.chat.id, photo, caption=text, reply_markup=markup, parse_mode="HTML")  
        else:  
            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")  
    except Exception as e:  
        print(f"❌ Помилка при старті: {e}")  
        bot.send_message(message.chat.id, "Сталася помилка при старті бота.")  
  
# =======================  
# Повідомлення оператору  
# =======================  
def notify_operators(ticket_id, user_id, username, chat_id, message_id):  
    try:  
        for operator_id in OPERATORS.keys():  
            markup = types.InlineKeyboardMarkup()  
            btn_accept = types.InlineKeyboardButton(  
                "✅ Принять",  
                callback_data=f"accept_{ticket_id}_{user_id}_{operator_id}_{chat_id}_{message_id}"  
            )  
            btn_close = types.InlineKeyboardButton(  
                "🛑 Закрыть тикет",  
                callback_data=f"close_ticket_{ticket_id}_{operator_id}"  
            )  
            markup.add(btn_accept, btn_close)  
            bot.send_message(operator_id,  
                             f"🔔 Новый тикет #{ticket_id}\nID користувача: {user_id}\nВід: @{username}",  
                             reply_markup=markup)  
        log_message(ticket_id, f"Запит надіслано операторам від @{username}")  
    except Exception as e:  
        print(f"❌ Помилка notify_operators: {e}")  
  
# =======================  
# Callback кнопки  
# =======================  
@bot.callback_query_handler(func=lambda call: True)  
def callback_query(call):  
    global ticket_counter  
    name = call.from_user.first_name  
    username = call.from_user.username or name  
  
    try:  
        if call.data == "support":  
            markup = types.InlineKeyboardMarkup()  
            btn_connect = types.InlineKeyboardButton("Підключити оператора", callback_data="connect_operator")  
            btn_back = types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_start")  
            markup.add(btn_connect, btn_back)  
            text = f"Вітаю, {username}!\n\nНатисніть 'Підключити оператора' для звернення."  
            bot.edit_message_caption(chat_id=call.message.chat.id,  
                                     message_id=call.message.message_id,  
                                     caption=text,  
                                     reply_markup=markup,  
                                     parse_mode="HTML")  
  
        elif call.data == "connect_operator":  
            ticket_counter += 1  
            markup = types.InlineKeyboardMarkup()  
            btn_cancel = types.InlineKeyboardButton(  
                "❌ Отменить. Проблема решена!",  
                callback_data=f"cancel_ticket_{ticket_counter}_{[call.from_user.id](http://call.from_user.id)}_{username}_{[call.message.chat.id](http://call.message.chat.id)}_{call.message.message_id}"  
            )  
            markup.add(btn_cancel)  
            text = f"Вітаю, {username}!\n\nНомер тікету: #{ticket_counter}\nСтатус: <i>Ожидание оператора...</i>"  
            bot.edit_message_caption(chat_id=call.message.chat.id,  
                                     message_id=call.message.message_id,  
                                     caption=text,  
                                     reply_markup=markup,  
                                     parse_mode="HTML")  
            ticket_messages[ticket_counter] = ([call.message.chat.id](http://call.message.chat.id), call.message.message_id, text, [call.from_user.id](http://call.from_user.id))  
            pending_tickets[ticket_counter] = {  
                "user_id": [call.from_user.id](http://call.from_user.id),  
                "username": username,  
                "chat_id": [call.message.chat.id](http://call.message.chat.id),  
                "message_id": call.message.message_id  
            }  
            notify_operators(ticket_counter, [call.from_user.id](http://call.from_user.id), username, [call.message.chat.id](http://call.message.chat.id), call.message.message_id)  
  
        elif call.data.startswith("cancel_ticket_"):  
            parts = call.data.split("_")  
            ticket_id = int(parts[2])  
            if ticket_id in ticket_messages:  
                chat_id, message_id, old_caption, _ = ticket_messages[ticket_id]  
                canceled_tickets.add(ticket_id)  
                caption = old_caption.split("Статус:")[0] + "Статус: Тікет скасовано."  
                markup = types.InlineKeyboardMarkup()  
                btn_back = types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_start")  
                markup.add(btn_back)  
                bot.edit_message_caption(chat_id=chat_id,  
                                         message_id=message_id,  
                                         caption=caption,  
                                         reply_markup=markup,  
                                         parse_mode="HTML")  
                if ticket_id in pending_tickets:  
                    del pending_tickets[ticket_id]  
                if ticket_id in active_chats:  
                    del active_chats[ticket_id]  
                log_message(ticket_id, f"Тікет #{ticket_id} скасовано @{username}")  
  
        elif call.data.startswith("accept_"):  
            parts = call.data.split("_")  
            ticket_id = int(parts[1])  
            if ticket_id in canceled_tickets:  
                bot.answer_callback_query([call.id](http://call.id), text="Тікет скасовано")  
                return  
            user_id = int(parts[2])  
            operator_id = int(parts[3])  
            chat_id_from_ticket = int(parts[4])  
            message_id_from_ticket = int(parts[5])  
            operator_name = OPERATORS.get(operator_id, "Оператор")  
            if ticket_id in ticket_messages:  
                _, _, old_caption, _ = ticket_messages[ticket_id]  
                new_caption = old_caption.split("Статус:")[0] + f"Статус: Оператор {operator_name} подключился."  
                bot.edit_message_caption(chat_id=chat_id_from_ticket,  
                                         message_id=message_id_from_ticket,  
                                         caption=new_caption,  
                                         reply_markup=None,  
                                         parse_mode="HTML")  
            bot.send_message(user_id, f"Оператор {operator_name} подключился к вашему тикету.")  
            active_chats[ticket_id] = (operator_id, user_id)  
            if ticket_id in pending_tickets:  
                del pending_tickets[ticket_id]  
            log_message(ticket_id, f"Оператор {operator_name} принял тикет")  
            bot.answer_callback_query([call.id](http://call.id), text="Тікет прийнято")  
  
        elif call.data.startswith("close_ticket_"):  
            parts = call.data.split("_")  
            ticket_id = int(parts[2])  
            if ticket_id in active_chats:  
                operator_id, user_id = active_chats[ticket_id]  
                # Відправляємо оцінку користувачу  
                markup = types.InlineKeyboardMarkup(row_width=5)  
                for i in range(1,6):  
                    markup.add(types.InlineKeyboardButton(str(i), callback_data=f"rate_{ticket_id}_{i}"))  
                bot.send_message(user_id, "Тікет закрито оператором. Оцените работу:", reply_markup=markup)  
                del active_chats[ticket_id]  
                log_message(ticket_id, f"Тікет #{ticket_id} закрито оператором")  
            bot.answer_callback_query([call.id](http://call.id), text="Тікет закрито")  
  
        elif call.data.startswith("rate_"):  
            parts = call.data.split("_")  
            ticket_id = int(parts[1])  
            rating = int(parts[2])  
            log_message(ticket_id, f"Оценка оператора: {rating}/5")  
            bot.send_message([call.from_user.id](http://call.from_user.id), "Дякуємо за оцінку!")  
            bot.answer_callback_query([call.id](http://call.id), text="Оцінка прийнята")  
  
        elif call.data == "back_to_start":  
            text, markup = main_menu(name)  
            bot.edit_message_caption(chat_id=call.message.chat.id,  
                                     message_id=call.message.message_id,  
                                     caption=text,  
                                     reply_markup=markup,  
                                     parse_mode="HTML")  
  
    except Exception as e:  
        print(f"❌ Помилка callback_query: {e}")  
        bot.answer_callback_query(call.id, text="Сталася помилка")  
  
# =======================  
# Пересилання повідомлень  
# =======================  
@bot.message_handler(func=lambda message: True)  
def forward_messages(message):  
    try:  
        if message.from_user.id in OPERATORS:  
            for ticket_id, (operator_id, user_id) in active_chats.items():  
                if operator_id == message.from_user.id:  
                    bot.send_message(user_id, message.text)  
                    log_message(ticket_id, f"Повідомлення від оператора {OPERATORS[message.from_user.id]}: {message.text}")  
                    return  
            bot.send_message(message.from_user.id, "❌ Нету активних тикетов")  
        else:  
            for ticket_id, (operator_id, user_id) in active_chats.items():  
                if user_id == message.from_user.id:  
                    operator_name = OPERATORS.get(operator_id, "Оператор")  
                    bot.send_message(operator_id, f"Сообщение от пользователя (тикет #{ticket_id}): {message.text}")  
                    log_message(ticket_id, f"Повідомлення від користувача: {message.text}")  
                    return  
            bot.send_message(message.chat.id, "Я не розумію вас. Попробуйте /start")  
    except Exception as e:  
        print(f"❌ Помилка forward_messages: {e}")  
  
# =======================  
# Запуск бота  
# =======================  
print("✅ Бот запущено")  
bot.infinity_polling()  
