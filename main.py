import telebot
import re

TOKEN = "8760601927:AAG2otYDFvDrH6M1Dwq0WrUfdXUi6ff4oQU"
bot = telebot.TeleBot(TOKEN)

# Welcome Message
WELCOME_TEXT = """স্বাগতম {name}! 🎉

Krira TV অফিসিয়াল চ্যাটে জয়েন করার জন্য ধন্যবাদ।
এখানে শুধু আলোচনা করবেন, কোনো লিংক দেওয়া যাবে না।"""

# লিংক ডিটেক্ট করার প্যাটার্ন
LINK_PATTERN = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|bit\.ly/|goo\.gl/|tinyurl\.|youtu\.be/|instagram\.com|facebook\.com|fb\.com)",
    re.IGNORECASE
)

# নতুন মেম্বার জয়েন করলে Welcome
@bot.message_handler(content_types=["new_chat_members"])
def welcome_new_member(message):
    for member in message.new_chat_members:
        if member.is_bot:
            continue
        
        name = member.first_name
        if member.last_name:
            name += f" {member.last_name}"
        
        try:
            bot.send_message(
                message.chat.id,
                WELCOME_TEXT.format(name=name)
            )
        except Exception as e:
            print("Welcome error:", e)

# লিংক থাকলে মেসেজ ডিলিট
@bot.message_handler(func=lambda message: True, content_types=["text", "photo", "video", "document", "animation", "sticker"])
def delete_links(message):
    # অ্যাডমিনদের মেসেজ ডিলিট করবে না
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ["creator", "administrator"]:
            return
    except:
        pass

    text = ""
    if message.text:
        text = message.text
    elif message.caption:
        text = message.caption

    if text and LINK_PATTERN.search(text):
        try:
          bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            print("Delete error:", e)

print("Bot started successfully...")
bot.infinity_polling()
