import telebot, os, requests
from gtts import gTTS
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

api_token = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(api_token)

bad_words = [
    'fuck', 'shit', 'bitch', 'asshole', 'bastard', 'dick', 'cunt', 'piss', 'damn', 'crap',
    'slut', 'whore', 'fucker', 'motherfucker', 'hell', 'sex', 'porn', 'devil', 'dumbass',
    'nigger', 'retard', 'fag', 'idiot', 'moron', 'douche', 'jackass', 'prick', 'pussy',
    'cock', 'balls', 'blowjob', 'boobs', 'nude', 'jerk', 'mad', 'stupid', 'ass', 'freak',
    'bloody', 'bugger', 'arse', 'wanker', 'tosser', 'son of a bitch', 'go to hell',
    'fuck off', 'piece of shit', 'screw you', 'you suck', 'kiss my ass', 'shut up',
    'what the fuck', 'dickhead', 'fucked up', 'goddamn', 'dumbfuck', 'eat shit',
    'bullshit', 'dickface', 'asswipe', 'fuckface', 'piss off', 'bitchass', 'hell no',
    'suck my dick', 'eat a dick', 'bastard child', 'you’re a bitch', 'dirty whore',
    'motherfucking', 'cocksucker', 'who the hell', 'freaking out', 'fatass', 'shithead',
    'lazy ass', 'son of a whore', 'stupid bitch', 'fucktard', 'idiot bitch', 'shut the fuck up',
    'whorehouse', 'bitch slap', 'dumb bitch', 'choke on it', 'screw that', 'goddammit',
    'screw this', 'you bastard', "you're an idiot", 'moron fuck', "you're dead", 'dumbass idiot',
    'I hate you', 'dumb motherfucker', 'fat bitch', 'fuck you all', 'dick sucking', 'balls deep',
    'horny bastard', 'no damn way', 'sex addict', 'get fucked', 'bloody fool', 'asslicker'
]


def the_word(message):
    return [word for word in bad_words if word in message.text.lower()]


def get_bible_verse(reference):
    response = requests.get(f'https://bible-api.com/{reference}')
    if response.status_code == 200:
        data = response.json()
        return f"{data['reference']}\n{data['text']}"
    else:
        return None


voice_cond = ["audio", "read", "say", "recite"]

def help_read(message):
    text = message.text.lower()
    text_list = text.split()
    first_word = text_list[0]
    last_words = text_list[1:]
    if first_word in voice_cond:
        verse_reference = " ".join(last_words)
        bible_ver = get_bible_verse(verse_reference)
        if bible_ver is None:
            return None, "Sorry, we couldn't find the verse. Please check the reference and try again."
        else:
            # Use gTTS to generate the audio file
            audio_file = 'audio.mp3'
            tts = gTTS(text=bible_ver, lang='en')
            tts.save(audio_file)
            return bible_ver, audio_file  # Return both text and audio file
    else:
        bible_ver = get_bible_verse(text)
        return bible_ver, None  # Return only text if no voice keyword


def s_word(message):
    return any(word in message.text.lower() for word in bad_words)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
                 """Hello! I'm God'sBrain_BibleBot.
I'm here to help you access Bible verses on Telegram. Here's how you can use me:

Simply send me the correct Bible verse reference, and I’ll send you the verse.

(e.g., "John 3:16").

If you'd like to hear the verse, just include one of these keywords: read, audio, recite, say along with the verse reference.

(e.g., "read John 3:16"),

and I’ll send you an audio version.
I hope you find this bot helpful in making your daily spiritual journey easier. Feel free to reach out anytime – you’re always welcome!

You can reach out to the Developer on
Telegram: https://t.me/kingsleyumekwe
Whatsapp: https://wa.me/2347042637659.
Thank you very much for utilizing my Bot.
                 """)


@bot.message_handler(func=s_word)
def warn_reply(message):
    bad_words_found = the_word(message)
    bot.reply_to(message, f"Please don't use the word(s) {', '.join(bad_words_found)} when texting me. Thank you")


@bot.message_handler(func=lambda message: message.text.lower().startswith(tuple(voice_cond)))
def audio_verse_reply(message):
    bible_text, voice_file = help_read(message)

    if bible_text is None:
        bot.reply_to(message, "Sorry, we couldn't find the verse. Please check the reference and try again.")
        return

    # Send the text of the Bible verse
    bot.reply_to(message, bible_text)

    # Send audio if it's available
    if voice_file and Path(voice_file).is_file():
        with open(voice_file, 'rb') as voice_note:
            bot.send_voice(message.chat.id, voice_note)
        os.remove(voice_file)


@bot.message_handler(func=lambda message: not message.text.lower().startswith(tuple(voice_cond)))
def text_verse_reply(message):
    bible_text, _ = help_read(message)

    if bible_text:
        bot.reply_to(message, bible_text)
    else:
        bot.reply_to(message, "Sorry, we couldn't find the verse. Please check the reference and try again.")


bot.infinity_polling()
