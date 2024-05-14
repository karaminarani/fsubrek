from pyrogram.filters import command
from pyrogram.filters import private
from pyrogram.handlers import MessageHandler
from pyrogram.helpers import ikb
from pyrogram.types import Message

from .helpers import Filter
from .helpers import helpers
from bot.client import Bot


@Filter.Admins
async def generate(client: Bot, message: Message):
    if not helpers.generate:
        return None

    dbchid = client.env.DATABASE_ID
    copied = await helpers.copymsg(message)
    encode = client.url.encode(
        f'id-{copied * abs(dbchid)}',
    )
    urlstr = helpers.urlstr(encode)
    urlmsg = f'https://t.me/c/{str(dbchid)[4:]}/{copied}'
    markup = ikb([
        [
            ('Message', urlmsg, 'url'),
            (
                'Share',
                helpers.urlstr(urlstr, share=True),
                'url',
            ),
        ],
    ])
    await message.reply(
        urlstr,
        reply_markup=markup,
    )
    return await message.delete()


Bot.add_handler(
    MessageHandler(
        generate,
        filters=~command(Bot.cmd.cmds) & private,
    ),
)