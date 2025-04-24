import telebot
import config
import voice
import os

API_TOKEN = config.bot_token
bot = telebot.TeleBot(API_TOKEN)

voices = voice.get_all_voices()
voice_buttons = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
for v in voices:
    button = telebot.types.KeyboardButton(v['name'])
    voice_buttons.add(button)

voice_buttons.add(telebot.types.KeyboardButton("Скачать как MP3"))

selected_voice = {}
download_mp3 = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "Запустить бота и выбрать голос"),
        telebot.types.BotCommand("/help", "Как использовать бота"),
        telebot.types.BotCommand("/about", "Информация о боте"),
    ])
    bot.reply_to(message,
                 "Привет! Я бот для создания озвучки! Выбери голос, который будет использоваться при создании озвучки:",
                 reply_markup=voice_buttons)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "🤖 *Как пользоваться ботом:*

"
        "1. Нажмите /start и выберите голос
"
        "2. Введите текст, который нужно озвучить
"
        "3. Получите голосовое сообщение или mp3-файл

"
        "🎙 Бот поддерживает несколько голосов Yandex SpeechKit."
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['about'])
def about_bot(message):
    bot.send_message(
        message.chat.id,
        "Этот бот озвучивает текст с помощью Yandex SpeechKit. "
        "Выберите голос и отправьте сообщение — бот пришлёт вам озвучку 🎧"
    )

@bot.message_handler(func=lambda message: message.text == "Скачать как MP3")
def set_mp3_download(message):
    user_id = message.from_user.id
    download_mp3[user_id] = True
    bot.send_message(user_id, "Теперь озвучка будет отправляться в mp3 формате 🎵")

@bot.message_handler(func=lambda message: message.text in [v['name'] for v in voices])
def voice_selected(message):
    user_id = message.from_user.id
    selected_voice[user_id] = message.text
    bot.reply_to(message, f"Вы выбрали голос: {message.text}. Теперь введите текст для озвучки:")

@bot.message_handler(func=lambda message: True)
def generate_voice(message):
    user_id = message.from_user.id
    if user_id in selected_voice:
        voice_name = selected_voice[user_id]
        voice_id = next(v['id'] for v in voices if v['name'] == voice_name)
        is_mp3 = download_mp3.get(user_id, False)
        try:
            audio_file = voice.generate_audio(message.text, voice_id, format="mp3" if is_mp3 else "oggopus")
            with open(audio_file, 'rb') as audio:
                if is_mp3:
                    bot.send_document(user_id, audio, caption="Ваша озвучка в mp3 🎵")
                else:
                    bot.send_voice(user_id, audio)
            os.remove(audio_file)
        except Exception as e:
            bot.reply_to(message, f"Ошибка при генерации озвучки: {e}")
    else:
        bot.reply_to(message, "Сначала выберите голос командой /start")

if __name__ == '__main__':
    bot.polling(none_stop=True)
