import telebot
import re

TOKEN = "8760601927:AAG2otYDFvDrH6M1Dwq0WrUfdXUi6ff4oQU"
bot = telebot.TeleBot(TOKEN)

WELCOME_TEXT = """✨ Welcome {name}! ✨
Thank you for joining the official Krira TV chat.
Enjoy your stay! ⚽🔥"""

LINK_PATTERN = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|bit\.ly/|goo\.gl/|tinyurl\.|youtu\.be/|instagram\.com|facebook\.com|fb\.com|onlyfans|pornhub|xvideos|xnxx|xhamster|spankbang|redtube|youporn|chaturbate|stripchat|bongacams|livejasmin|myfreecams|cam4|adult|sex|porn|xxx)",
    re.IGNORECASE
)

SPAM_KEYWORDS = re.compile(
    r"(adult|massage|body\s*massage|full\s*massage|happy\s*ending|sexy\s*massage|home\s*service|call\s*girl|escort|hot\s*girl|night\s*service|full\s*service|body\s*to\s*body|online\s*models|real\s*girls|active\s*cams|meet\s*models|verified\s*girls|daily\s*live\s*shows|claim\s*free\s*access|download\s*now|instant\s*access|get\s*it\s*free|unlock\s*now|access\s*for\s*free|free\s*access|live\s*shows|cams|models|onlyfans|porn|xxx|sex\s*video|hot\s*video|nude|naked|boobs|pussy|dick|fuck|blowjob|handjob|escort\s*service|dating\s*girl|meet\s*girl|whatsapp\s*girl|telegram\s*girl)",
    re.IGNORECASE
)

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

# শুধু Photo, Video, File, Voice ইত্যাদি ডিলিট (Sticker & Animation থাকবে)
@bot.message_handler(content_types=["photo", "video", "document", "voice", "video_note", "audio", "contact", "location", "poll"])
def delete_media(message):
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ["creator", "administrator"]:
            return
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

# টেক্সট স্প্যাম ও লিংক ডিলিট
@bot.message_handler(func=lambda message: True, content_types=["text"])
def delete_spam_text(message):
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ["creator", "administrator"]:
            return
    except:
        pass

    text = message.text or ""

    if message.reply_markup:
        try:
            for row in message.reply_markup.keyboard:
                for button in row:
                    if hasattr(button, 'text') and button.text:
                        text += " " + button.text
        except:
            pass

    if LINK_PATTERN.search(text) or SPAM_KEYWORDS.search(text):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass

print("Bot started successfully...")
bot.infinity_polling()
