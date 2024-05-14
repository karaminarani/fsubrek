import contextlib

from pyrogram.filters import command
from pyrogram.filters import private
from pyrogram.handlers import MessageHandler
from pyrogram.helpers import ikb
from pyrogram.types import Message

from .helpers import Filter
from .helpers import helpers
from bot.client import Bot


@Filter.Admins
async def batch(client: Bot, message: Message):
    cid = message.chat.id
    uid = message.from_user.id
    cdb = client.env.DATABASE_ID

    fask = await client.ask(
        chat_id=cid,
        text='Forward: First Message',
        user_id=uid,
        reply_markup=helpers.urlikb(
            'Database',
            f'tg://openmessage?chat_id={str(cdb)[4:]}',
        ),
    )
    await message.delete()
    await fask.sent_message.delete()
    if (
        not fask.forward_from_chat
        or not fask.forward_from_chat.id == cdb
    ):
        return await fask.reply('Invalid!', quote=True)
    first = fask.forward_from_message_id
    flink = f'https://t.me/c/{str(cdb)[4:]}/{first}'
    while True:
        await fask.delete()
        lask = await client.ask(
            chat_id=cid,
            text='Forward: Last Message',
            user_id=uid,
            reply_markup=helpers.urlikb(
                'Previously',
                flink,
            ),
        )
        await lask.sent_message.delete()
        if (
            not lask.forward_from_chat
            or not lask.forward_from_chat.id == cdb
        ):
            return await lask.reply('Invalid!', quote=True)
        await lask.delete()
        last = lask.forward_from_message_id
        lurl = f'https://t.me/c/{str(cdb)[4:]}/{last}'
        break
    with contextlib.suppress(ValueError):
        if (abs(int(first) - int(last)) + 1) > 200:
            return await message.reply(
                "Can't retrieve >200 messages.",
            )
    urlstr = helpers.urlstr(helpers.encode(first, last))
    markup = ikb([
        [
            ('First', flink, 'url'),
            (
                'Share',
                helpers.urlstr(urlstr, share=True),
                'url',
            ),
            ('Last', lurl, 'url'),
        ],
    ])
    await message.reply(
        urlstr,
        quote=True,
        reply_markup=markup,
    )


Bot.add_handler(
    MessageHandler(
        batch,
        filters=command(Bot.cmd.batch) & private,
    ),
)
