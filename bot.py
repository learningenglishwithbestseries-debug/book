import telebot
from telebot import types

TOKEN = "8921033224:AAEj6hQEyzDfTS_csnDdlYEh6hrXrf-Oawg"
ADMIN_ID = 1218611906

CHANNELS = [
    "@RomanceWord",
    "@INFORMATIONINSTITUTE",
    "@MaryamTeam"
]

bot = telebot.TeleBot(TOKEN)

# کاربر فعلی که ادمین برایش در حال ارسال است
current_target = None

# شماره درخواست
request_counter = 1000


def is_joined(user_id):
    try:
        for channel in CHANNELS:
            member = bot.get_chat_member(channel, user_id)

            if member.status not in [
                "member",
                "administrator",
                "creator"
            ]:
                return False

        return True

    except Exception as e:
        print("Membership Error:", e)
        return False


def join_keyboard():
    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "کانال اول",
            url="https://t.me/RomanceWord"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "کانال دوم",
            url="https://t.me/INFORMATIONINSTITUTE"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "کانال سوم",
            url="https://t.me/MaryamTeam"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "✅ بررسی عضویت",
            callback_data="check_join"
        )
    )

    return kb


@bot.message_handler(commands=["start"])
def start(message):

    if not is_joined(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "برای دریافت کتاب ابتدا عضو کانال‌ها شوید.",
            reply_markup=join_keyboard()
        )

        return

    bot.send_message(
        message.chat.id,
        "📚 سلام\n\nنام کتاب یا درخواست خود را ارسال کنید."
    )


@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join(call):

    if is_joined(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "عضویت تایید شد."
        )

        bot.send_message(
            call.message.chat.id,
            "✅ عضویت تایید شد.\n\nنام کتاب را ارسال کنید."
        )

    else:

        bot.answer_callback_query(
            call.id,
            "هنوز عضو همه کانال‌ها نیستید."
        )


# درخواست کاربران
@bot.message_handler(
    func=lambda m: m.from_user.id != ADMIN_ID,
    content_types=["text"]
)
def user_request(message):

    global request_counter

    if not is_joined(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "ابتدا عضو کانال‌ها شوید.",
            reply_markup=join_keyboard()
        )

        return

    request_counter += 1

    admin_text = (
        f"📚 درخواست #{request_counter}\n\n"
        f"نام: {message.from_user.first_name}\n"
        f"یوزرنیم: @{message.from_user.username}\n"
        f"ID: {message.from_user.id}\n\n"
        f"کتاب:\n{message.text}"
    )

    bot.send_message(
        ADMIN_ID,
        admin_text
    )

    bot.send_message(
        message.chat.id,
        "✅ درخواست شما ثبت شد."
    )


# انتخاب کاربر
@bot.message_handler(commands=["send"])
def send_mode(message):

    global current_target

    if message.from_user.id != ADMIN_ID:
        return

    try:

        parts = message.text.split()

        if len(parts) != 2:
            bot.reply_to(
                message,
                "فرمت صحیح:\n/send USER_ID"
            )
            return

        current_target = int(parts[1])

        bot.reply_to(
            message,
            f"✅ حالت ارسال فعال شد\n\nUser ID: {current_target}\n\nهر فایل، متن، کتاب صوتی یا فورواردی ارسال کنید."
        )

    except Exception as e:
        bot.reply_to(message, str(e))


@bot.message_handler(commands=["stop"])
def stop_mode(message):

    global current_target

    if message.from_user.id != ADMIN_ID:
        return

    current_target = None

    bot.reply_to(
        message,
        "⛔ حالت ارسال غیرفعال شد."
    )


# ارسال هر نوع محتوا از ادمین
@bot.message_handler(
    func=lambda m: m.from_user.id == ADMIN_ID,
    content_types=[
        "text",
        "document",
        "photo",
        "audio",
        "video",
        "voice",
        "animation",
        "sticker"
    ]
)
def admin_sender(message):

    global current_target

    if current_target is None:
        return

    try:

        # دستورات را ارسال نکن
        if message.content_type == "text" and message.text.startswith("/"):
            return

        # بهترین حالت برای فوروارد و فایل‌ها
        bot.copy_message(
            chat_id=current_target,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        bot.reply_to(
            message,
            "✅ ارسال شد"
        )

    except Exception as e:

        bot.reply_to(
            message,
            f"❌ خطا:\n{e}"
        )


print("Bot Started...")
bot.infinity_polling(skip_pending=True)