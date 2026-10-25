import telebot
import re

TOKEN = "8760601927:AAG2otYDFvDrH6M1Dwq0WrUfdXUi6ff4oQU"
bot = telebot.TeleBot(TOKEN)

WELCOME_TEXT = """✨ Welcome {name}! ✨
Thank you for joining the official Krira TV chat.
Enjoy your stay! ⚽🔥"""

LINK_PATTERN = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|bit\.ly/|goo\.gl/|tinyurl\.|youtu\.be/|instagram\.com|facebook\.com|fb\.com|onlyfans|pornhub|xvideos|xnxx|xhamster|spankbang|redtube|youporn|chaturbate|stripchat|bongacams|livejasmin|myfreecams|cam4|\.m3u8|\.mp4)",
    re.IGNORECASE
)

SPAM_KEYWORDS = re.compile(
    r"(adult|massage|naughty|models|cams|vip\s*girls|free\s*to\s*watch|claim\s*free|download\s*now|instant\s*access|unlock|access\s*for\s*free|live\s*shows|hot\s*girl|call\s*girl|escort|onlyfans|porn|xxx|sex|nude|naked|gái\s*xinh|ngắm|exclusive|tap\s*to\s*enter|fast\s*&\s*private|real\s*girls|verified\s*girls|online\s*models)",
    re.IGNORECASE
)

def is_admin(chat_id, user_id):
    """অ্যাডমিন কিনা চেক করে"""
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ["creator", "administrator"]
    except:
        return False

@bot.message_handler(content_types=["new_chat_members"])
def welcome_new_member(message):
    for member in message.new_chat_members:
        if member.is_bot:
            continue
        name = member.first_name
        if member.last_name:
            name += f" {member.last_name}"
        try:
            bot.send_message(message.chat.id, WELCOME_TEXT.format(name=name))
        except:
            pass

# মিডিয়া ডিলিট (অ্যাডমিন বাদে)
@bot.message_handler(content_types=["photo", "video", "document", "voice", "video_note", "audio", "contact", "location", "poll"])
def delete_media(message):
    if is_admin(message.chat.id, message.from_user.id):
        return
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

# টেক্সট স্প্যাম ও লিংক ডিলিট (অ্যাডমিন বাদে)
@bot.message_handler(func=lambda message: True, content_types=["text"])
def check_text(message):
    if is_admin(message.chat.id, message.from_user.id):
        return

    text = message.text or ""

    # বাটনের টেক্সটও চেক
    if message.reply_markup:
        try:
            for row in message.reply_markup.keyboard:
                for btn in row:
                    if hasattr(btn, "text") and btn.text:
                        text += " " + btn.text
        except:
            pass

    if LINK_PATTERN.search(text) or SPAM_KEYWORDS.search(text):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass

print("Bot started successfully...")
bot.infinity_polling()
