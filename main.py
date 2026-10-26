import telebot
import re
import os
import time

# টোকেন কোডে না রেখে হোস্টিং এর Environment Variable (BOT_TOKEN) থেকে নেয়
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise SystemExit("BOT_TOKEN environment variable সেট করা নেই")
bot = telebot.TeleBot(TOKEN)

# এদের মেসেজ কখনো ডিলিট হবে না (নিজের Telegram user ID)
OWNER_IDS = {8034030069}

# নিজের চ্যানেলের নামে পোস্ট করলে সেই চ্যানেলের ID এখানে দিন
ALLOWED_SENDER_CHATS = set()

ANON_ADMIN_BOT_ID = 1087968824   # GroupAnonymousBot
TG_SERVICE_ID = 777000           # linked channel auto-forward

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

# অ্যাডমিন লিস্ট ৫ মিনিট ক্যাশ থাকে, প্রতি মেসেজে API কল হয় না
_admin_cache = {}
CACHE_SECONDS = 300

def get_admin_ids(chat_id):
    cached = _admin_cache.get(chat_id)
    if cached and time.time() - cached[0] < CACHE_SECONDS:
        return cached[1]
    admins = bot.get_chat_administrators(chat_id)
    ids = {a.user.id for a in admins}
    _admin_cache[chat_id] = (time.time(), ids)
    return ids

def is_admin(message):
    """অ্যাডমিন কিনা নিশ্চিত করে চেক করে"""
    try:
        # গ্রুপ বা চ্যানেলের নামে পোস্ট
        if message.sender_chat is not None:
            if message.sender_chat.id == message.chat.id:
                return True    # anonymous admin
            if getattr(message, "is_automatic_forward", False):
                return True    # linked channel এর পোস্ট
            return message.sender_chat.id in ALLOWED_SENDER_CHATS

        user = message.from_user
        if user is None:
            return True
        if user.id in OWNER_IDS or user.id in (ANON_ADMIN_BOT_ID, TG_SERVICE_ID):
            return True

        return user.id in get_admin_ids(message.chat.id)
    except Exception as e:
        print("Admin check error:", e)
        return True   # এরর হলে সেফ থাকার জন্য ডিলিট করবে না

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

# মিডিয়া ডিলিট (অ্যাডমিন হলে কিছুই করবে না)
@bot.message_handler(content_types=["photo", "video", "document", "voice", "video_note", "audio", "contact", "location", "poll", "animation"])
def delete_media(message):
    if is_admin(message):
        return
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

def has_hidden_link(message):
    """'Click here' এর মতো লুকানো লিংক ধরে"""
    for ent in (message.entities or []):
        if ent.type in ("url", "text_link"):
            return True
    return False

@bot.message_handler(commands=["myid"])
def send_my_id(message):
    if message.chat.type == "private":
        bot.reply_to(message, f"Your ID: {message.from_user.id}")
    else:
        check_text(message)

# টেক্সট লিংক/স্প্যাম ডিলিট (অ্যাডমিন হলে কিছুই করবে না)
@bot.message_handler(func=lambda message: True, content_types=["text"])
@bot.edited_message_handler(func=lambda message: True, content_types=["text"])
def check_text(message):
    if is_admin(message):
        return

    text = message.text or ""

    if message.reply_markup:
        try:
            for row in message.reply_markup.keyboard:
                for btn in row:
                    if hasattr(btn, "text") and btn.text:
                        text += " " + btn.text
        except:
            pass

    if has_hidden_link(message) or LINK_PATTERN.search(text) or SPAM_KEYWORDS.search(text):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass

print("Bot started successfully...")
bot.infinity_polling(allowed_updates=["message", "edited_message"])
