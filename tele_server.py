from tkinter import messagebox
import mysql.connector as conn
import telebot
import io
import csv

try:
    with open("tele_creds.txt",'r') as file:
        contents = file.read().split("\n")
        MYSQL_USERNAME = contents[0].partition(":")[2]
        MYSQL_PASSWORD = contents[1].partition(":")[2]
        API_TOKEN = contents[2].partition(":")[2] 
        file.close()
except FileNotFoundError:
    messagebox.showerror("Error", "tele_creds.txt not found on current path!!")

CHAT_ID = ''
HELP = f"""COMMANDS: 
/help - show this message
/view - view all books
/issued - view all issued books"""

db = conn.connect(host = 'localhost', user = MYSQL_USERNAME, password = MYSQL_PASSWORD, database='library')
cursor = db.cursor()

bot = telebot.TeleBot(API_TOKEN)
BOT_NAME = bot.get_me().first_name

def online_alert():
    try:    
        cursor.execute("SELECT * FROM TELEBOT")
        result = cursor.fetchall()
        for i in result:
            bot.send_message(chat_id=int(i[0]), text="Bot is Online!")
    except:
        pass

online_alert()

@bot.message_handler(commands = ['help'])
def help(message):
    bot.send_message(message.chat.id, HELP)


@bot.message_handler(commands = ['start'])
def start(message):
    cursor.execute("SELECT * FROM TELEBOT WHERE STUDENT_ID=%s",(message.chat.id,))
    result = cursor.fetchall()
    CHAT_ID = message.chat.id

    if result == []:    
        cursor.execute("INSERT INTO TELEBOT(STUDENT_ID) VALUES(%s)", (message.chat.id,))
        db.commit()
        

    bot.send_message(message.chat.id, f"Welcome to {BOT_NAME}")
    bot.send_message(message.chat.id, HELP)


@bot.message_handler(commands = ['view'])
def view(message):
    cursor.execute("DESC books")
    result = cursor.fetchall()
    fields = []

    for i in result:
        fields.append(i[0])

    cursor.execute("SELECT * FROM books")
    data = cursor.fetchall()

    # csv module can write data in io.StringIO buffer only
    s = io.StringIO()
    csv.writer(s).writerow(fields)
    csv.writer(s).writerows(data)
    s.seek(0)

    # telebot library can send files only from io.BytesIO buffer
    # we need to convert StringIO to BytesIO
    buf = io.BytesIO()
    buf.write(s.getvalue().encode())
    buf.seek(0)
    buf.name = f'BOOKS.csv'

    bot.send_document(message.chat.id, document=buf)


@bot.message_handler(commands = ['issued'])
def generate_csv(query):
    student_name = query.text

    cursor.execute("DESC issued_books")
    result = cursor.fetchall()
    fields = []

    for i in result:
        fields.append(i[0])

    cursor.execute("SELECT * FROM issued_books WHERE STUDENT_NAME=%s", (student_name,))
    result = cursor.fetchall()
    data = []
    for i in result:
        row = []
        row.append(i[0])
        row.append(i[1])
        row.append(i[2])
        row.append(i[3])
        row.append(i[4])
        row.append(i[5])
        row.append(i[6])
        row.append(i[7].strftime('%Y-%m-%d'))
        row.append(i[8])

        data.append(row)

    s = io.StringIO()
    csv.writer(s).writerow(fields)
    csv.writer(s).writerows(data)
    s.seek(0)

    buf = io.BytesIO()
    buf.write(s.getvalue().encode())
    buf.seek(0)
    buf.name = f'ISSUED_BOOKS.csv'

    bot.send_document(query.chat.id, document=buf)


bot.infinity_polling()
