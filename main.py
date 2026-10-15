import telebot
import re

TOKEN = "8760601927:AAG2otYDFvDrH6M1Dwq0WrUfdXUi6ff4oQU"
bot = telebot.TeleBot(TOKEN)

# Welcome Message
WELCOME_TEXT = """Welcome {name}! 🎉

Thank you for joining the official Krira TV chat.
Please keep the conversation respectful and avoid sharing any links or spam.
Enjoy your stay!"""

# সব ধরনের লিংক ডিটেক্ট
LINK_PATTERN = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|bit\.ly/|goo\.gl/|tinyurl\.|youtu\.be/|instagram\.com|facebook\.com|fb\.com|onlyfans|pornhub|xvideos|xnxx|xhamster|spankbang|redtube|youporn|chaturbate|stripchat|bongacams|livejasmin|myfreecams|cam4|adult|sex|porn|xxx)",
    re.IGNORECASE
)

# Adult / Spam কিওয়ার্ড (খুব স্ট্রং)
SPAM_KEYWORDS = re.compile(
    r"(adult|massage|body\s*massage|full\s*massage|happy\s*ending|sexy\s*massage|home\s*service|call\s*girl|escort|hot\s*girl|night\s*service|full\s*service|body\s*to\s*body|online\s*models|real\s*girls|active\s*cams|meet\s*models|verified\s*girls|daily\s*live\s*shows|claim\s*free\s*access|download\s*now|instant\s*access|get\s*it\s*free|unlock\s*now|access\s*for\s*free|free\s*access|live\s*shows|cams|models|onlyfans|porn|xxx|sex\s*video|hot\s*video|nude|naked|boobs|pussy|dick|fuck|blowjob|handjob|escort\s*service|dating\s*girl|meet\s*girl|whatsapp\s*girl|telegram\s*girl)",
    re.IGNORECASE
)

# নতুন মেম্বার জয়েন করলে Welcome
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

# লিংক বা স্প্যাম থাকলে মেসেজ ডিলিট
@bot.message_handler(func=lambda message: True, content_types=["text", "photo", "video", "document", "animation", "sticker"])
def delete_spam(message):
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

    # বাটনের টেক্সটও চেক করা
    if message.reply_markup:
        try:
            for row in message.reply_markup.keyboard:
                for button in row:
                    if hasattr(button, 'text') and button.text:
                        text += " " + button.text
        except:
            pass

    if text and (LINK_PATTERN.search(text) or SPAM_KEYWORDS.search(text)):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            print("Delete error:", e)

print("Bot started successfully...")
bot.infinity_polling()
