import os


class Config:
    startmsg = 'The bot is up and running. These bots ' \
               'can store messages in custom chats, '\
               'and users access them through the bot.'
    forcemsg = 'To view messages shared by bots. '\
               'Join first, then press the Try Again button.'

    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DATABASE_ID = int(os.getenv('DATABASE_ID'))

    API_ID = 2040
    API_HASH = 'b18441a1ff607e10a989891a5462e627'
    BOT_ID = BOT_TOKEN.split(':', 1)[0]
    OWNER_ID = 487936750
    MONGO_URL = 'mongodb://root:passwd@mongo'


Config = Config()
